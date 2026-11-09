# VulRIS Vul4J+ evaluation data

This repository publishes the evidence used by the final VulRIS paper. The
final experiment evaluates one fixed 140-case Vul4J+ cohort under a source-only
baseline (B0) and a VulRIS-assisted condition (P1).

## Final paper results

| Method/model | B0 | P1 | P1−B0 |
| --- | ---: | ---: | ---: |
| DeepSeek 4.1 Flash (Max) | 39/140 (27.86%) | 48/140 (34.29%) | +9 (+6.43 pp) |
| Gemini 3.8 Flash (High) | 52/140 (37.14%) | 49/140 (35.00%) | -3 (-2.14 pp) |
| GPT-6 Luna (High) | 15/140 (10.71%) | 18/140 (12.86%) | +3 (+2.14 pp) |
| GPT-6 Luna (Max) | 20/140 (14.29%) | 23/140 (16.43%) | +3 (+2.14 pp) |

The CodeQL CLI 2.23.2 reference baseline reports 19/140 (13.57%). GPT-5.6
Luna is excluded from the final paper and comparative experiment.

## Authoritative release

- [Final binary adjudication, paper tables, and data dictionary](results/vul4jplus-final-20261110/)
- [Raw SQLite ledgers and criteria artifacts](https://github.com/daehyuh/B0-P1-Result-Datas/releases/tag/vul4jplus-paper-evidence-20261110)
- [VulRIS relation builder](analyzer/)
- [Evaluation prompts](prompts/)

The release asset preserves the seven DeepSeek ledger/repair overlays, six
Gemini and GPT-6 B0/P1 ledgers, and four mapping/criteria artifacts used for
log-level analysis. It is distributed as a release asset rather than a Git
object because it is larger than 100 MB.

## Scope of older material

Folders outside `results/vul4jplus-final-20261110` are historical experiment
artifacts from earlier manuscript iterations. They are retained for provenance
but are not part of the final Vul4J+-only result table above.

Benchmark source trees are not redistributed. Obtain Vul4J+ from its upstream
Zenodo record and follow the upstream projects' licenses. See
[DATA_SOURCES.md](DATA_SOURCES.md).
