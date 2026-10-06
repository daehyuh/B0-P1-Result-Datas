# Static Source-Code Relation Information Builder

This folder contains the program used to build and query static relation information for Java projects. It is separate from the benchmark source snapshots and result tables in the parent research workspace.

The tool collects source-file metadata and hashes, parses Java declarations and call sites, and stores relation candidates and selected configuration/input-role clues in SQLite. It does not call an LLM, run SAST, build the project, prove runtime reachability, or decide that a vulnerability exists.

## Requirements and tests

Python 3.12 is the tested environment. Install the pinned-compatible dependencies and run the unit tests:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

The test fixture is a small, non-benchmark example. Test output is generated locally and is not part of this repository.

## Build and query

Always give `--data-dir` a **new, empty directory**. Do not point it at an existing research database or a benchmark input directory.

```powershell
python relation_index.py --data-dir "D:\work\relation-data" --project "D:\work\sample-project" build
python relation_index.py --data-dir "D:\work\relation-data" --project "D:\work\sample-project" overview
python relation_index.py --data-dir "D:\work\relation-data" --project "D:\work\sample-project" symbols find
python relation_index.py --data-dir "D:\work\relation-data" --project "D:\work\sample-project" facts
```

`build` records an input snapshot. Queries may use `--project` or a previously created `--snapshot-id`; see `relation_index.py --help` and [`데이터구조.md`](데이터구조.md) for supported commands and fields.

## What the relations mean

Calls and other links are static candidates based on syntax, names, argument counts, and available local context. They are not compiler-resolved call graphs. Role and configuration clues are also candidates, not proof of input validation, authorization, reachability, or exploitability. The analyzer is not a SAST product.

The implementation was extracted from the research workspace and adjusted for standalone use. The exact source relationship and known differences are described in [`구현출처.md`](구현출처.md).

## Data and licensing

This repository does not include benchmark source snapshots or the generated per-case relation databases. Those must be obtained from their upstream datasets, with their original license and citation terms respected. The recorded experiment results include source/relation hashes where available so that the evaluated inputs can be identified without republishing the source code.
