# Flash Max final results — 2026-10-21

| Dataset | Cases | CodeQL | B0 (source only) | P1 (VulRIS) | P1−B0 (cases; pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vul4J | 79 | 11 (13.92%) | 13 (16.46%) | 13 (16.46%) | +0; +0.00 pp |
| VJBench | 42 | 4 (9.52%) | 16 (38.10%) | 16 (38.10%) | +0; +0.00 pp |
| Vul4J+ | 140 | 17 (12.14%) | 39 (27.86%) | 46 (32.86%) | +7; +5.00 pp |
| CWE-Bench-Java | 213 | 41 (19.25%) | 52 (24.41%) | 51 (23.94%) | -1; -0.47 pp |

The current representative setting is Flash Max (`deepseek-flash`, reasoning effort `max`). B0 reads the prepared source; P1 also queries VulRIS relation records. Vul4J uses the original multi-candidate protocol (at most 10 candidates); VJBench, Vul4J+, and CWE-Bench-Java use at most one candidate per submission.

The metric is case-level reference-cause and affected-path matching. All 213 CWE-Bench-Java cases have final binary labels, including case-173. Datasets are reported separately because Vul4J and Vul4J+ overlap. The final adopted submissions form a retrospective collection.

P1 and B0 tie on Vul4J and VJBench. P1 identifies seven more Vul4J+ cases (+5.00 pp), and one fewer CWE-Bench-Java case (−0.47 pp). These results show dataset-dependent effects of relation-assisted exploration rather than uniform improvement.

CodeQL counts come from the completed recorded baseline (CLI 2.23.2, Java pack 1.8.1, `java-security-extended.qls`, `build-mode=none`). Exact source-version parity with the corrected LLM inputs has not been established for every case. Report CodeQL values as descriptive baseline results rather than a controlled same-input estimate of the relation index's contribution.

## Files

- `results/`: dataset rows and calculated summaries. `vulris_llm` is a compatibility alias of `p1`.
- `reports/`: the 948 selected reports, without costs or local execution metadata.
- `adjudications.json`: final labels, cause/path reasons, matching candidate numbers, and reference links.
- `response-verification.json`: hashes linking the selected reports to the archived responses.
- `protocol.json`: model, candidate policies, metric, and comparison scope.
- `figures/`: English paper figures (PNG and SVG).

Older dated outputs and other model profiles are historical material, not current representative results. Upstream source trees, generated relation databases, credentials, and local working databases are not redistributed.
