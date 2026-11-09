#!/usr/bin/env python3
"""Scan a ZIP release asset for common credential signatures.

The script reports only the member name and signature class. It never prints
the matched credential text.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


PATTERNS = {
    "google_api_key": re.compile(rb"(?<![0-9A-Za-z_-])AIza[0-9A-Za-z_-]{30,}"),
    "openai_api_key": re.compile(
        rb"(?<![0-9A-Za-z_-])sk-(?:proj-)?[0-9A-Za-z_-]{20,}"
    ),
    "github_token": re.compile(
        rb"(?<![0-9A-Za-z_-])(?:gh[pousr]_[0-9A-Za-z]{20,}|github_pat_[0-9A-Za-z_]{40,})"
    ),
    "aws_access_key": re.compile(rb"(?<![0-9A-Z])AKIA[0-9A-Z]{16}"),
    "slack_token": re.compile(rb"(?<![0-9A-Za-z-])xox[baprs]-[0-9A-Za-z-]{20,}"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def scan_member(archive: zipfile.ZipFile, name: str) -> set[str]:
    matches: set[str] = set()
    tail = b""
    with archive.open(name) as stream:
        while chunk := stream.read(1024 * 1024):
            data = tail + chunk
            for label, pattern in PATTERNS.items():
                if pattern.search(data):
                    matches.add(label)
            tail = data[-256:]
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    findings: list[tuple[str, str]] = []
    with zipfile.ZipFile(args.archive) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            for label in sorted(scan_member(archive, info.filename)):
                findings.append((info.filename, label))
    if findings:
        print("Credential-like signatures detected:")
        for member, label in findings:
            print(f"- {member}: {label}")
        return 1
    print("PASS: no common credential signatures detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
