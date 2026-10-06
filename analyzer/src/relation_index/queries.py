import json

from .storage import unpack


def page(items, total, offset, limit):
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
        "truncated": offset + len(items) < total,
        "next_offset": offset + len(items) if offset + len(items) < total else None,
    }


def bounded(limit, offset=0):
    if (
        not isinstance(limit, int)
        or not 1 <= limit <= 100
        or not isinstance(offset, int)
        or offset < 0
    ):
        raise ValueError("limit must be 1..100 and offset must be nonnegative")


class Queries:
    def __init__(self, store, snapshot_id):
        self.store = store
        self.snapshot_id = snapshot_id
        self.snapshot = unpack(
            store.one("SELECT * FROM snapshots WHERE id=?", (snapshot_id,)),
            ("manifest", "metrics", "capabilities"),
        )

    def overview(self):
        return {
            "snapshot_id": self.snapshot_id,
            "metrics": self.snapshot["metrics"],
            "capabilities": self.snapshot["capabilities"],
            "roles": self.store.all(
                "SELECT kind,count(*) AS count FROM facts WHERE snapshot_id=? GROUP BY kind",
                (self.snapshot_id,),
            ),
        }

    def files(self, query="", limit=50, offset=0):
        bounded(limit, offset)
        rows = self.store.all(
            "SELECT path,language,size,line_count FROM files WHERE snapshot_id=? "
            "AND instr(lower(path),lower(?))>0 ORDER BY path",
            (self.snapshot_id, query),
        )
        return page(rows[offset : offset + limit], len(rows), offset, limit)

    def symbols(self, query="", kind="", limit=50, offset=0):
        bounded(limit, offset)
        if isinstance(kind, list):
            kinds = list(dict.fromkeys(kind))
            if not all(isinstance(value, str) for value in kinds):
                raise ValueError("kind must contain only strings")
            if not kinds:
                return page([], 0, offset, limit)
            placeholders = ",".join("?" for _ in kinds)
            where = (
                "snapshot_id=? AND instr(lower(qualified_name),lower(?))>0 "
                f"AND kind IN ({placeholders})"
            )
            args = (self.snapshot_id, query, *kinds)
            total = self.store.one("SELECT count(*) n FROM symbols WHERE " + where, args)["n"]
            rows = self.store.all(
                "SELECT id,name,qualified_name,kind,path,start_line,end_line,signature "
                "FROM symbols WHERE " + where + " ORDER BY qualified_name,id LIMIT ? OFFSET ?",
                (*args, limit, offset),
            )
            return page(rows, total, offset, limit)
        args = (self.snapshot_id, query, kind, kind)
        where = "snapshot_id=? AND instr(lower(qualified_name),lower(?))>0 AND (?='' OR kind=?)"
        total = self.store.one("SELECT count(*) n FROM symbols WHERE " + where, args)["n"]
        rows = self.store.all(
            "SELECT id,name,qualified_name,kind,path,start_line,end_line,signature "
            "FROM symbols WHERE " + where + " ORDER BY qualified_name,id LIMIT ? OFFSET ?",
            (*args, limit, offset),
        )
        return page(rows, total, offset, limit)

    def symbol(self, symbol_id):
        row = self.store.one(
            "SELECT data FROM symbols WHERE snapshot_id=? AND id=?", (self.snapshot_id, symbol_id)
        )
        return json.loads(row["data"])

    def facts(self, kind="", limit=50, offset=0):
        bounded(limit, offset)
        if isinstance(kind, list):
            kinds = list(dict.fromkeys(kind))
            if not all(isinstance(value, str) for value in kinds):
                raise ValueError("kind must contain only strings")
            if not kinds:
                return page([], 0, offset, limit)
            placeholders = ",".join("?" for _ in kinds)
            where = f"snapshot_id=? AND kind IN ({placeholders})"
            args = (self.snapshot_id, *kinds)
            total = self.store.one("SELECT count(*) n FROM facts WHERE " + where, args)["n"]
            rows = self.store.all(
                "SELECT data FROM facts WHERE " + where + " ORDER BY path,kind,id LIMIT ? OFFSET ?",
                (*args, limit, offset),
            )
            return page([json.loads(row["data"]) for row in rows], total, offset, limit)
        rows = self.store.all(
            "SELECT data FROM facts WHERE snapshot_id=? AND (?='' OR kind=?) ORDER BY path,kind,id",
            (self.snapshot_id, kind, kind),
        )
        return page(
            [json.loads(r["data"]) for r in rows[offset : offset + limit]], len(rows), offset, limit
        )

    def read(self, path, start_line=1, end_line=None):
        if not isinstance(start_line, int) or start_line < 1:
            raise ValueError("start_line must be positive")
        try:
            f = self.store.one(
                "SELECT * FROM files WHERE snapshot_id=? AND path=?", (self.snapshot_id, path)
            )
        except KeyError as exc:
            raise ValueError(
                "File path is not in this snapshot. Use list_files to copy its exact relative path; "
                "do not guess or use an absolute path."
            ) from exc
        lines = self.store.get_blob(f["hash"]).decode().splitlines()
        if start_line > max(1, len(lines)):
            raise ValueError("start_line exceeds file length")
        requested_end = end_line if end_line is not None else start_line + 119
        if not isinstance(requested_end, int) or requested_end < start_line:
            raise ValueError("end_line must be >= start_line")
        stop = min(requested_end, start_line + 199, len(lines))
        output, size = [], 0
        for i in range(start_line - 1, stop):
            value = lines[i]
            if not output and len(value) > 24000:
                raise ValueError("A source line exceeds the 24000-character read limit")
            if size + len(value) > 24000:
                break
            output.append({"line": i + 1, "text": value})
            size += len(value)
        end = output[-1]["line"] if output else start_line - 1
        return {
            "path": path,
            "hash": f["hash"],
            "start_line": start_line,
            "end_line": end,
            "total_lines": len(lines),
            "lines": output,
            "truncated": end < min(requested_end, len(lines)),
            "next_line": end + 1 if end < len(lines) else None,
            "span": {"path": path, "start_line": start_line, "end_line": end},
        }

    def search(self, query, limit=30, offset=0):
        bounded(limit, offset)
        if not query.strip():
            raise ValueError("Search query must not be empty")
        tokens = query.split()
        expression = " AND ".join('"' + t.replace('"', '""') + '"' for t in tokens[:12])
        with self.store.connect() as db:
            rows = db.execute(
                "SELECT path,snippet(file_search,2,'','', ' ... ',28) AS excerpt "
                "FROM file_search WHERE file_search MATCH ? AND snapshot_id=? "
                "ORDER BY rank,path",
                (expression, self.snapshot_id),
            ).fetchall()
        return page([dict(r) for r in rows[offset : offset + limit]], len(rows), offset, limit)

    def context(self, symbol_id, limit=20):
        bounded(limit)
        symbol = self.symbol(symbol_id)
        rows = self.store.all(
            "SELECT data FROM edges WHERE snapshot_id=? "
            "AND (src_id=? OR dst_id=?) ORDER BY kind,id",
            (self.snapshot_id, symbol_id, symbol_id),
        )
        # Structural children are accessed separately; keep the navigation view focused.
        relations = [
            json.loads(r["data"]) for r in rows if json.loads(r["data"])["kind"] != "CONTAINS"
        ]
        links = relations[:limit]
        connected = set()
        for e in links:
            connected.add(e["dst_id"] if e["src_id"] == symbol_id else e["src_id"])
        related = [self.symbol(key) for key in sorted(connected)]
        compact = [
            {
                k: s.get(k)
                for k in (
                    "id",
                    "kind",
                    "qualified_name",
                    "signature",
                    "path",
                    "start_line",
                    "end_line",
                )
            }
            for s in related
        ]
        facts = [
            json.loads(r["data"])
            for r in self.store.all(
                "SELECT data FROM facts WHERE snapshot_id=? AND (symbol_id=? OR symbol_id=?)",
                (self.snapshot_id, symbol_id, symbol.get("owner_id")),
            )
        ]
        call_rows = self.store.all(
            "SELECT data FROM calls WHERE snapshot_id=? AND caller_id=? "
            "ORDER BY path,start_line,id",
            (self.snapshot_id, symbol_id),
        )
        configs = self.facts("config_file", limit=10)
        source = self.read(symbol["path"], symbol["start_line"], symbol["end_line"])
        owner = self.symbol(symbol["owner_id"]) if symbol.get("owner_id") else None
        return {
            "symbol": symbol,
            "owner": {k: owner.get(k) for k in ("id", "qualified_name", "signature", "annotations")}
            if owner
            else None,
            "relations": page(links, len(relations), 0, limit),
            "related_symbols": compact,
            "calls": page(
                [json.loads(r["data"]) for r in call_rows[:limit]], len(call_rows), 0, limit
            ),
            "facts": facts,
            "configuration_files": configs,
            "source": source,
            "limitations": self.snapshot["capabilities"],
            "note": "Candidate relationships do not prove runtime flow or effective authorization.",
        }

    def relations(self, symbol_id, direction="both", limit=50, offset=0):
        bounded(limit, offset)
        if direction not in {"both", "incoming", "outgoing"}:
            raise ValueError("Invalid direction")
        self.symbol(symbol_id)
        rows = self.store.all(
            "SELECT data FROM edges WHERE snapshot_id=? "
            "AND (src_id=? OR dst_id=?) ORDER BY kind,id",
            (self.snapshot_id, symbol_id, symbol_id),
        )
        edges = [json.loads(r["data"]) for r in rows]
        edges = [
            e
            for e in edges
            if direction == "both"
            or (e["dst_id"] == symbol_id if direction == "incoming" else e["src_id"] == symbol_id)
        ]
        return page(edges[offset : offset + limit], len(edges), offset, limit)
