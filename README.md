# B0–P1 Java Vulnerability Detection Results

This repository publishes the analysis program and the case-level results used in the study of static source-code relation information for LLM-assisted vulnerability detection.

## Contents

- [`analyzer/`](analyzer/): source code and tests for the static relation-information builder. It does not call an LLM or determine whether code is vulnerable.
- [`results/summary.md`](results/summary.md): dataset-level comparison, scoring rules, and limitations.
- [`results/`](results/): case-level model submissions and target-match adjudications for Vul4J, VJBench, Vul4J+, and CWE-Bench-Java.
- [`results/codeql/`](results/codeql/): case-level CodeQL target-match adjudications and the comparison with P1 LLM. The large SARIF and working databases remain local.
- [`results/vul4j/README.md`](results/vul4j/README.md): explains how the original 75-case ledger and four-case supplement combine into the 79-case Vul4J result.
- [`prompts/`](prompts/): the B0/P1 and common prompts used by the recorded experiments.
- [`figures/`](figures/): figures accompanying the summary.

## Result files

The main summary reports one final score for each case and condition. The VJBench final case table and Vul4J+ final score table are linked from [`results/summary.md`](results/summary.md). Initial responses and separate format-repair executions remain distinct in the audit records; the final score table does not overwrite either source. The VJBench case-039 target correction is documented and linked to its evidence; it was made after reviewing the outputs and must be treated as a post-hoc correction.

The repository does **not** redistribute benchmark source snapshots, generated per-case relation databases, or the large working SQLite database. Dataset source commit/hash information is retained in the result records where available. Obtain benchmark code from its upstream source and follow its license and citation requirements. Rebuild relation data locally with the included analyzer if needed.

## Reproduction

See [`analyzer/README.md`](analyzer/README.md) for installation, commands, data format, and tests. Recreating the recorded LLM results is not automatic: the original prompts and evaluation configuration are included, but access to the upstream datasets and the corresponding model/API service is required.

## Citation

Kang, D. (2026). *B0–P1 Java Vulnerability Detection Results*. GitHub repository: <https://github.com/daehyuh/B0-P1-Result-Datas>.

## Scope and limitations

The reported metric is agreement with a benchmark-designated vulnerability target. A non-match does not establish that a model's other candidate is harmless or false. These adjudications are source- and patch-based reviews, not independent multi-rater reviews or runtime reproductions. Results from different datasets and prompt protocols should not be pooled as one accuracy estimate. See [`results/summary.md`](results/summary.md).

No blanket license is asserted for third-party datasets or code. The licenses and citation terms of the upstream projects remain applicable.
