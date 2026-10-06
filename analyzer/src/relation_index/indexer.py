import json
import time
from pathlib import Path

from . import java
from .snapshot import collect
from .storage import Cancelled, atomic_write, digest, encode

CAPABILITIES = {
    "syntax": "Java classes, methods, fields, annotations, call sites",
    "relations": "Syntax containment; name/type/arity-based call and inheritance candidates",
    "semantic_resolution": "not_implemented",
    "data_flow": "not_implemented",
    "control_flow": "not_implemented",
    "spring": "Annotation-name candidates; runtime DI, profiles and security enforcement unverified",
    "incremental": "Unchanged files reuse syntax cache; all cross-file candidates are rebuilt",
    "parser_version": java.VERSION,
}


def build_index(store, job):
    job_id = job["id"]
    project = store.one("SELECT * FROM projects WHERE id=?", (job["project_id"],))
    started = time.monotonic()
    cpu = time.process_time()
    store.phase(job_id, "collecting", "원본 파일을 수집하고 버전별 사본을 보관합니다.")
    manifest = collect(
        Path(project["root"]),
        store,
        lambda: store.checkpoint(job_id),
        on_file=lambda current, total, path: store.progress(job_id, current, total, path),
    )
    snapshot_id = digest([project["id"], manifest["content_hash"], java.VERSION])
    existing = store.all("SELECT id FROM snapshots WHERE id=?", (snapshot_id,))
    if existing:
        store.checkpoint(job_id)
        with store.connect() as db:
            if db.execute("SELECT cancel_requested FROM jobs WHERE id=?", (job_id,)).fetchone()[0]:
                raise Cancelled()
            db.execute(
                "UPDATE projects SET active_snapshot=? WHERE id=?", (snapshot_id, project["id"])
            )
        return {"snapshot_id": snapshot_id, "reused": True}
    store.phase(job_id, "parsing", "Java 선언과 호출 위치를 추출합니다.")
    parsed, hit, miss, errors = [], 0, 0, []
    extra_facts = []
    file_total = len(manifest["files"])
    for current, file in enumerate(manifest["files"], start=1):
        store.checkpoint(job_id)
        path, key = file["path"], file["hash"]
        store.progress(job_id, current, file_total, path)
        if file["language"] == "java":
            cache = (
                store.settings.data_dir
                / "parse_cache"
                / (digest([path, key, java.VERSION]) + ".json")
            )
            if cache.exists():
                try:
                    entry = json.loads(cache.read_text())
                    if (
                        not isinstance(entry, dict)
                        or not {
                            "symbols",
                            "calls",
                            "facts",
                            "parse_error",
                        }
                        <= entry.keys()
                    ):
                        raise ValueError("Incomplete parse cache")
                    hit += 1
                except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
                    entry = java.extract(path, store.get_blob(key))
                    atomic_write(cache, encode(entry).encode())
                    miss += 1
            else:
                entry = java.extract(path, store.get_blob(key))
                atomic_write(cache, encode(entry).encode())
                miss += 1
            if entry["parse_error"]:
                errors.append(path)
            parsed.append(entry)
        elif Path(path).name.startswith(
            ("application.", "application-", "pom.xml", "build.gradle")
        ):
            extra_facts.append(
                {
                    "id": digest([path, "config"])[:24],
                    "path": path,
                    "symbol_id": None,
                    "kind": "config_file",
                    "start_line": 1,
                    "end_line": file["line_count"],
                    "status": "candidate",
                    "note": "Related configuration file; active profile unverified",
                }
            )
    store.phase(job_id, "resolving", "호출·상속 후보를 연결하고 불확실성을 기록합니다.")
    symbols, calls, edges = java.link(
        parsed,
        lambda: store.checkpoint(job_id),
        lambda current, total, path: store.progress(job_id, current, total, path),
    )
    facts = [f for item in parsed for f in item["facts"]] + extra_facts
    metrics = {
        "files": len(manifest["files"]),
        "java_files": len(parsed),
        "symbols": len(symbols),
        "calls": len(calls),
        "edges": len(edges),
        "facts": len(facts),
        "unresolved_calls": sum(not c["targets"] for c in calls),
        "parse_errors": errors,
        "cache_hits": hit,
        "parsed_files": miss,
        "source_bytes": sum(f["size"] for f in manifest["files"]),
        "omitted_files": len(manifest["omitted"]),
        "build_seconds": round(time.monotonic() - started, 4),
        "cpu_seconds": round(time.process_time() - cpu, 4),
    }
    store.phase(job_id, "indexing", "검색 인덱스를 저장하고 새 버전을 활성화합니다.")
    published = False
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT cancel_requested FROM jobs WHERE id=?", (job_id,)).fetchone()[0]:
            raise Cancelled()
        # Another worker can finish the same immutable snapshot while this one parses.
        if not db.execute("SELECT 1 FROM snapshots WHERE id=?", (snapshot_id,)).fetchone():
            db.execute(
                "INSERT INTO snapshots VALUES(?,?,?,?,?,?)",
                (
                    snapshot_id,
                    project["id"],
                    time.time(),
                    encode(manifest),
                    encode(metrics),
                    encode(CAPABILITIES),
                ),
            )
            published = True
        for f in manifest["files"] if published else []:
            db.execute(
                "INSERT INTO files VALUES(?,?,?,?,?,?)",
                (snapshot_id, f["path"], f["hash"], f["size"], f["language"], f["line_count"]),
            )
            db.execute(
                "INSERT INTO file_search VALUES(?,?,?)",
                (snapshot_id, f["path"], store.get_blob(f["hash"]).decode()),
            )
        for s in symbols if published else []:
            db.execute(
                "INSERT INTO symbols VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    snapshot_id,
                    s["id"],
                    s["path"],
                    s["kind"],
                    s["name"],
                    s["qualified_name"],
                    s["owner_id"],
                    s["signature"],
                    s["start_line"],
                    s["end_line"],
                    encode(s),
                ),
            )
        for c in calls if published else []:
            db.execute(
                "INSERT INTO calls VALUES(?,?,?,?,?,?)",
                (snapshot_id, c["id"], c["caller_id"], c["path"], c["start_line"], encode(c)),
            )
        for e in edges if published else []:
            db.execute(
                "INSERT INTO edges VALUES(?,?,?,?,?,?)",
                (snapshot_id, e["id"], e["src_id"], e["dst_id"], e["kind"], encode(e)),
            )
        for f in facts if published else []:
            db.execute(
                "INSERT INTO facts VALUES(?,?,?,?,?,?)",
                (snapshot_id, f["id"], f["symbol_id"], f["path"], f["kind"], encode(f)),
            )
        db.execute("UPDATE projects SET active_snapshot=? WHERE id=?", (snapshot_id, project["id"]))
    if not published:
        return {"snapshot_id": snapshot_id, "reused": True}
    metrics["build_seconds"] = round(time.monotonic() - started, 4)
    metrics["cpu_seconds"] = round(time.process_time() - cpu, 4)
    store.execute("UPDATE snapshots SET metrics=? WHERE id=?", (encode(metrics), snapshot_id))
    return {"snapshot_id": snapshot_id, "reused": False, "metrics": metrics}
