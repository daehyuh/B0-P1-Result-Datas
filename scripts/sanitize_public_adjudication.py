#!/usr/bin/env python3
"""Create portable public copies of Vul4J+ adjudication artifacts.

The research artifacts contain absolute workstation paths solely as provenance
labels. This utility replaces those paths with stable artifact URIs while
leaving verdicts, rationales, hashes, case identifiers, and model outputs
unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
import ntpath
from pathlib import Path
from typing import Any


PATH_KEYS = {"path", "source_artifact", "generator"}


def portable_path(value: str, artifact_key: str | None = None) -> str:
    name = ntpath.basename(value.replace("/", "\\"))
    prefix = f"{artifact_key}/" if artifact_key else ""
    return f"artifact://{prefix}{name}"


def sanitize_json(value: Any, parent: dict[str, Any] | None = None) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        artifact_key = value.get("source_artifact_key")
        for key, item in value.items():
            if key in PATH_KEYS and isinstance(item, str) and ":\\" in item:
                result[key] = portable_path(item, artifact_key)
            else:
                result[key] = sanitize_json(item, value)
        return result
    if isinstance(value, list):
        return [sanitize_json(item, parent) for item in value]
    if isinstance(value, str) and len(value) > 3 and value[1:3] == ":\\":
        return portable_path(value)
    return value


def sanitize_json_file(source: Path, destination: Path) -> None:
    data = json.loads(source.read_text(encoding="utf-8"))
    destination.write_text(
        json.dumps(sanitize_json(data), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sanitize_csv_file(source: Path, destination: Path) -> None:
    with source.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    for row in rows:
        raw = row.get("source_artifact", "")
        if ":\\" in raw:
            row["source_artifact"] = portable_path(
                raw, row.get("source_artifact_key") or None
            )
    with destination.open("w", encoding="utf-8", newline="") as dst:
        writer = csv.DictWriter(dst, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sanitize_json_file(args.json, args.output_dir / args.json.name)
    sanitize_csv_file(args.csv, args.output_dir / args.csv.name)


if __name__ == "__main__":
    main()
