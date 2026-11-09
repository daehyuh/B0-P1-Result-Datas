#!/usr/bin/env python3
"""Locate credential-like signatures in ZIP-contained SQLite ledgers safely.

Matched values are replaced before context is printed. This distinguishes
benchmark fixture strings from credentials stored in configuration fields.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from scan_release_archive import PATTERNS


def quoted(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def redact_context(text: str, pattern: re.Pattern[bytes], label: str) -> str:
    raw = text.encode("utf-8", errors="ignore")
    match = pattern.search(raw)
    if not match:
        return ""
    start = max(0, match.start() - 100)
    end = min(len(raw), match.end() + 100)
    fragment = raw[start:match.start()] + f"<REDACTED:{label}>".encode() + raw[match.end():end]
    return fragment.decode("utf-8", errors="replace").replace("\r", " ").replace("\n", " ")


def inspect_database(path: Path, member: str) -> int:
    count = 0
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        for table in tables:
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({quoted(table)})")]
            for column in columns:
                query = f"SELECT {quoted(column)} FROM {quoted(table)} WHERE {quoted(column)} IS NOT NULL"
                try:
                    cursor = connection.execute(query)
                except sqlite3.Error:
                    continue
                for row_number, (value,) in enumerate(cursor, start=1):
                    if isinstance(value, bytes):
                        text = value.decode("utf-8", errors="ignore")
                    elif isinstance(value, str):
                        text = value
                    else:
                        continue
                    for label, pattern in PATTERNS.items():
                        context = redact_context(text, pattern, label)
                        if context:
                            count += 1
                            print(
                                f"{member} | table={table} | column={column} | "
                                f"row={row_number} | {label} | {context}"
                            )
    finally:
        connection.close()
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    total = 0
    with zipfile.ZipFile(args.archive) as archive, tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for info in archive.infolist():
            if not info.filename.endswith(".sqlite3"):
                continue
            destination = root / Path(info.filename).name
            with archive.open(info) as source, destination.open("wb") as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
            total += inspect_database(destination, info.filename)
            destination.unlink()
    print(f"TOTAL_MATCH_CONTEXTS={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
