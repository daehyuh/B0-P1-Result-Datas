import hashlib
import json
import os
import sqlite3
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .config import Settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects(
 id TEXT PRIMARY KEY, name TEXT NOT NULL, root TEXT NOT NULL UNIQUE,
 created_at REAL NOT NULL, active_snapshot TEXT
);
CREATE TABLE IF NOT EXISTS snapshots(
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 created_at REAL NOT NULL, manifest TEXT NOT NULL, metrics TEXT NOT NULL,
 capabilities TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS files(
 snapshot_id TEXT NOT NULL REFERENCES snapshots(id), path TEXT NOT NULL,
 hash TEXT NOT NULL, size INTEGER NOT NULL, language TEXT NOT NULL,
 line_count INTEGER NOT NULL, PRIMARY KEY(snapshot_id,path)
);
CREATE VIRTUAL TABLE IF NOT EXISTS file_search USING fts5(
 snapshot_id UNINDEXED, path UNINDEXED, content, tokenize='unicode61'
);
CREATE TABLE IF NOT EXISTS symbols(
 snapshot_id TEXT NOT NULL REFERENCES snapshots(id), id TEXT NOT NULL,
 path TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL,
 qualified_name TEXT NOT NULL, owner_id TEXT, signature TEXT NOT NULL,
 start_line INTEGER NOT NULL, end_line INTEGER NOT NULL,
 data TEXT NOT NULL, PRIMARY KEY(snapshot_id,id)
);
CREATE INDEX IF NOT EXISTS symbol_name ON symbols(snapshot_id,name);
CREATE INDEX IF NOT EXISTS symbol_owner ON symbols(snapshot_id,owner_id);
CREATE TABLE IF NOT EXISTS calls(
 snapshot_id TEXT NOT NULL, id TEXT NOT NULL, caller_id TEXT,
 path TEXT NOT NULL, start_line INTEGER NOT NULL, data TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,id)
);
CREATE TABLE IF NOT EXISTS edges(
 snapshot_id TEXT NOT NULL, id TEXT NOT NULL, src_id TEXT NOT NULL,
 dst_id TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,id)
);
CREATE INDEX IF NOT EXISTS edge_src ON edges(snapshot_id,src_id);
CREATE INDEX IF NOT EXISTS edge_dst ON edges(snapshot_id,dst_id);
CREATE TABLE IF NOT EXISTS facts(
 snapshot_id TEXT NOT NULL, id TEXT NOT NULL, symbol_id TEXT,
 path TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL,
 PRIMARY KEY(snapshot_id,id)
);
CREATE TABLE IF NOT EXISTS jobs(
 id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
 kind TEXT NOT NULL, status TEXT NOT NULL, phase TEXT NOT NULL,
 payload TEXT NOT NULL, result TEXT, error TEXT,
 created_at REAL NOT NULL, started_at REAL, finished_at REAL,
 cancel_requested INTEGER NOT NULL DEFAULT 0, owner TEXT,
 heartbeat REAL, idempotency_key TEXT UNIQUE,
 progress_current INTEGER NOT NULL DEFAULT 0,
 progress_total INTEGER NOT NULL DEFAULT 0,
 current_file TEXT,
 progress_files TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS events(
 id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL REFERENCES jobs(id),
 created_at REAL NOT NULL, kind TEXT NOT NULL, message TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workers(
 id TEXT PRIMARY KEY, heartbeat REAL NOT NULL, pid INTEGER NOT NULL
);
"""

LATEST_SCHEMA_VERSION = 1


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    if not isinstance(value, bytes):
        value = encode(value).encode()
    return hashlib.sha256(value).hexdigest()


def new_id():
    return uuid.uuid4().hex


def unpack(row, fields=()):
    result = dict(row)
    for key in fields:
        if result.get(key) is not None:
            result[key] = json.loads(result[key])
    return result


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._progress_last = {}
        settings.initialize()
        with self.connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version > LATEST_SCHEMA_VERSION:
                raise RuntimeError(
                    f"Database schema {version} is newer than supported version "
                    f"{LATEST_SCHEMA_VERSION}"
                )
            db.executescript(SCHEMA)
            if version < 1:
                db.execute("PRAGMA user_version=1")

    @contextmanager
    def connect(self):
        timeout = max(1.0, float(os.environ.get("RELATION_SQLITE_TIMEOUT", "20")))
        db = sqlite3.connect(self.settings.database, timeout=timeout)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        db.execute(f"PRAGMA busy_timeout={int(timeout * 1000)}")
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def all(self, sql, args=()):
        with self.connect() as db:
            return [dict(row) for row in db.execute(sql, args)]

    def one(self, sql, args=()):
        rows = self.all(sql, args)
        if not rows:
            raise KeyError("Requested record does not exist")
        return rows[0]

    def execute(self, sql, args=()):
        with self.connect() as db:
            db.execute(sql, args)

    def put_blob(self, content: bytes):
        key = digest(content)
        atomic_write(self.settings.data_dir / "blobs" / key, content)
        return key

    def get_blob(self, key):
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("Invalid content hash")
        content = (self.settings.data_dir / "blobs" / key).read_bytes()
        if digest(content) != key:
            raise ValueError("Stored source blob failed integrity verification")
        return content

    def event(self, job_id, message, kind="progress"):
        self.execute(
            "INSERT INTO events(job_id,created_at,kind,message) VALUES(?,?,?,?)",
            (job_id, time.time(), kind, message),
        )

    def enqueue(self, project_id, kind, payload, idempotency_key=None):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if idempotency_key:
                old = db.execute(
                    "SELECT * FROM jobs WHERE idempotency_key=?", (idempotency_key,)
                ).fetchone()
                if old:
                    if (old["project_id"], old["kind"], old["payload"]) != (
                        project_id,
                        kind,
                        encode(payload),
                    ):
                        raise ValueError("Idempotency key already used for a different request")
                    return unpack(old, ("payload", "result", "progress_files"))
            job_id = new_id()
            db.execute(
                "INSERT INTO jobs(id,project_id,kind,status,phase,payload,created_at,"
                "idempotency_key) VALUES(?,?,?,'queued','queued',?,?,?)",
                (job_id, project_id, kind, encode(payload), time.time(), idempotency_key),
            )
        self.event(job_id, "작업이 대기열에 등록되었습니다.")
        return self.job(job_id)

    def job(self, job_id):
        return unpack(
            self.one("SELECT * FROM jobs WHERE id=?", (job_id,)),
            ("payload", "result", "progress_files"),
        )

    def claim(self, owner):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM jobs WHERE status='queued' "
                "AND cancel_requested=0 ORDER BY created_at LIMIT 1"
            ).fetchone()
            if not row:
                return None
            db.execute(
                "UPDATE jobs SET status='running',phase='preparing',started_at=?,"
                "owner=?,heartbeat=? WHERE id=?",
                (time.time(), owner, time.time(), row["id"]),
            )
        return self.job(row["id"])

    def checkpoint(self, job_id):
        row = self.one("SELECT cancel_requested FROM jobs WHERE id=?", (job_id,))
        if row["cancel_requested"]:
            raise Cancelled("작업이 취소되었습니다.")

    def phase(self, job_id, phase, message):
        self.checkpoint(job_id)
        self.execute(
            "UPDATE jobs SET phase=?,progress_current=0,progress_total=0,current_file=NULL,"
            "progress_files='[]' WHERE id=?",
            (phase, job_id),
        )
        self._progress_last.pop(job_id, None)
        self.event(job_id, message)

    def progress(self, job_id, current, total=0, path=None, *, force=False):
        now = time.monotonic()
        if not force and now - self._progress_last.get(job_id, 0) < 0.25:
            return
        current_file = str(path)[:1000] if path else None
        with self.connect() as db:
            row = db.execute(
                "SELECT progress_files FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
            if row is None:
                return
            recent = json.loads(row["progress_files"] or "[]")
            if current_file and (not recent or recent[-1] != current_file):
                recent = (recent + [current_file])[-4:]
            db.execute(
                "UPDATE jobs SET progress_current=?,progress_total=?,current_file=?,"
                "progress_files=? WHERE id=?",
                (max(0, int(current)), max(0, int(total)), current_file, encode(recent), job_id),
            )
        self._progress_last[job_id] = now


class Cancelled(Exception):
    pass


def atomic_write(path: Path, content: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
