"""Build and inspect a local source-code relation index.

This command uses the same Java syntax extraction and candidate linking modules
archived in ``src/relation_index``. It does not run a vulnerability scan or an LLM.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from relation_index.config import Settings
from relation_index.indexer import build_index
from relation_index.queries import Queries
from relation_index.storage import Store, encode


def output(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=dict))


def build(args: argparse.Namespace) -> None:
    root = args.project.resolve()
    if not root.is_dir():
        raise SystemExit(f"Project directory does not exist: {root}")
    store = Store(Settings(args.data_dir.resolve()))
    with store.connect() as db:
        row = db.execute("SELECT id FROM projects WHERE root=?", (str(root),)).fetchone()
        if row:
            project_id = row["id"]
        else:
            project_id = uuid.uuid4().hex
            db.execute(
                "INSERT INTO projects(id,name,root,created_at) VALUES(?,?,?,?)",
                (project_id, args.name or root.name, str(root), time.time()),
            )
    job = store.enqueue(project_id, "index", {})
    store.execute(
        "UPDATE jobs SET status='running',started_at=?,heartbeat=? WHERE id=?",
        (time.time(), time.time(), job["id"]),
    )
    try:
        result = build_index(store, job)
    except Exception as exc:
        store.execute(
            "UPDATE jobs SET status='failed',phase='failed',error=?,finished_at=? WHERE id=?",
            (str(exc), time.time(), job["id"]),
        )
        raise
    store.execute(
        "UPDATE jobs SET status='completed',phase='completed',result=?,finished_at=? "
        "WHERE id=?",
        (encode(result), time.time(), job["id"]),
    )
    output({"project_id": project_id, "job_id": job["id"], **result})


def query(args: argparse.Namespace) -> None:
    store = Store(Settings(args.data_dir.resolve()))
    snapshot_id = args.snapshot_id
    if snapshot_id is None:
        if args.project is None:
            raise SystemExit("Provide --snapshot-id or --project")
        root = str(args.project.resolve())
        row = store.one("SELECT active_snapshot FROM projects WHERE root=?", (root,))
        snapshot_id = row["active_snapshot"]
    if not snapshot_id:
        raise SystemExit("No completed index snapshot was found")
    index = Queries(store, snapshot_id)
    if args.action == "overview":
        result = index.overview()
    elif args.action == "files":
        result = index.files(args.text, args.limit, args.offset)
    elif args.action == "symbols":
        result = index.symbols(args.text, args.kind, args.limit, args.offset)
    elif args.action == "symbol":
        result = index.symbol(args.symbol_id)
    elif args.action == "relations":
        result = index.relations(args.symbol_id, args.direction, args.limit, args.offset)
    elif args.action == "facts":
        result = index.facts(args.kind, args.limit, args.offset)
    elif args.action == "search":
        result = index.search(args.text, args.limit, args.offset)
    elif args.action == "read":
        result = index.read(args.path, args.start_line, args.end_line)
    elif args.action == "context":
        result = index.context(args.symbol_id, args.limit)
    else:
        raise SystemExit(f"Unknown action: {args.action}")
    output(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, default=Path(".relation-index"), help="Local index storage"
    )
    parser.add_argument("--project", type=Path, help="Project source directory")
    parser.add_argument("--snapshot-id", help="Specific immutable snapshot ID for queries")
    sub = parser.add_subparsers(dest="action", required=True)
    build_cmd = sub.add_parser("build", help="Create an index from --project")
    build_cmd.add_argument("--name", help="Display name for the project")
    for name in ("overview", "files", "symbols", "symbol", "relations", "facts", "search", "read", "context"):
        cmd = sub.add_parser(name)
        if name in {"files", "symbols", "search"}:
            cmd.add_argument("text", nargs="?", default="")
        if name in {"symbols", "facts"}:
            cmd.add_argument("--kind", default="")
        if name in {"symbol", "relations", "context"}:
            cmd.add_argument("symbol_id")
        if name == "read":
            cmd.add_argument("path")
            cmd.add_argument("--start-line", type=int, default=1)
            cmd.add_argument("--end-line", type=int)
        if name == "relations":
            cmd.add_argument("--direction", choices=("both", "incoming", "outgoing"), default="both")
        if name not in {"overview", "symbol", "read"}:
            cmd.add_argument("--limit", type=int, default=50)
            cmd.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    if args.action == "build":
        if args.project is None:
            parser.error("build requires --project")
        build(args)
    else:
        query(args)


if __name__ == "__main__":
    main()
