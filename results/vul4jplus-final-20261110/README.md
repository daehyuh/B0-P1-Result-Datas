# Final Vul4J+ paper evidence (2026-11-10)

This directory is the authoritative result set for the final VulRIS paper. The
evaluation cohort is the same 140-case Vul4J+ set in every condition.

## Final results

| Method/model | Condition | Hits | Rate |
| --- | --- | ---: | ---: |
| CodeQL CLI 2.23.2 | source | 19/140 | 13.57% |
| DeepSeek 4.1 Flash (Max) | B0 | 39/140 | 27.86% |
| DeepSeek 4.1 Flash (Max) | P1 | 48/140 | 34.29% |
| Gemini 3.8 Flash (High) | B0 | 52/140 | 37.14% |
| Gemini 3.8 Flash (High) | P1 | 49/140 | 35.00% |
| GPT-6 Luna (High) | B0 | 15/140 | 10.71% |
| GPT-6 Luna (High) | P1 | 18/140 | 12.86% |
| GPT-6 Luna (Max) | B0 | 20/140 | 14.29% |
| GPT-6 Luna (Max) | P1 | 23/140 | 16.43% |

GPT-5.6 Luna is excluded from the paper and from this final comparison.

## Files

- `ALL-MODEL-VUL4JPLUS-BINARY-ADJUDICATION-20261101.{json,csv}`:
  1,260 final binary decisions (CodeQL plus eight LLM conditions).
- `REPORT.md`: final counts and source-artifact hashes.
- `model-condition-metrics.csv`: paper Table 3 in machine-readable form.
- `p1-relation-tool-metrics.csv`: paper Table 4 in machine-readable form.
- `DATA_DICTIONARY.md`: field and denominator definitions.
- `RAW-LEDGER-MANIFEST.md`: release asset contents and checksum.
- `SHA256SUMS.txt`: hashes for the files tracked in this directory.

The raw SQLite ledgers are distributed as a GitHub Release asset because the
ZIP is larger than GitHub's ordinary 100 MB Git object limit:

<https://github.com/daehyuh/B0-P1-Result-Datas/releases/tag/vul4jplus-paper-evidence-20261110>

The legacy multi-dataset material elsewhere in this repository predates the
final Vul4J+-only manuscript and is not used for the reported final results.
