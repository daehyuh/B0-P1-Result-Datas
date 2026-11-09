#!/usr/bin/env python3
"""Report common credential signatures in a repository working tree."""

from __future__ import annotations

import argparse
from pathlib import Path

from scan_release_archive import PATTERNS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    findings: list[tuple[str, str]] = []
    for path in args.root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        data = path.read_bytes()
        for label, pattern in PATTERNS.items():
            if pattern.search(data):
                findings.append((path.relative_to(args.root).as_posix(), label))
    if findings:
        for name, label in findings:
            print(f"{name}: {label}")
        return 1
    print("PASS: no common credential signatures detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
