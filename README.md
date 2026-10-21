# B0–P1 Java Vulnerability Detection Results

Current representative results use **Flash Max only**. [Final tables, 948 selected reports, judgments, and hashes](results/final-flash-max-20261021/).

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

## Contents

- [`analyzer/`](analyzer/): source code and tests for the static relation-information builder. It does not call an LLM or determine whether code is vulnerable.
- [`results/summary.md`](results/summary.md): dataset-level comparison, scoring rules, and limitations.
- [`results/`](results/): case-level model submissions and target-match adjudications for Vul4J, VJBench, Vul4J+, and CWE-Bench-Java.
- [`results/codeql/`](results/codeql/): case-level CodeQL target-match adjudications and the comparison with P1 LLM. The large SARIF and working databases remain local.
- [`results/vul4j/README.md`](results/vul4j/README.md): explains how the original 75-case ledger and four-case supplement combine into the 79-case Vul4J result.
- [`prompts/`](prompts/): the B0/P1 and common prompts used by the recorded experiments.
- [`figures/`](figures/): figures accompanying the summary.


## Provenance and reproduction

The current snapshot supersedes earlier score tables while preserving original responses and dated records. Other model profiles are archival, not current paper results. [Current protocol](results/final-flash-max-20261021/protocol.json) and [analyzer instructions](analyzer/README.md) describe the inputs and settings. Upstream benchmark sources and generated relation databases are not redistributed. AI-assisted source/patch matching underlies the labels; independent multi-rater agreement and repeated-run variation have not been measured.

No blanket license is asserted for third-party datasets or code. Respect upstream license and citation terms.
