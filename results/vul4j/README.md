# Vul4J result files

The 79-case evaluation combines two preserved result batches. `VUL4J-1` is included among the 79 prepared cases but excluded from each model-condition score because its designated CVE conflicts with the linked patch/test target. The primary denominator is therefore 78 for each of the six model-condition combinations.

## Case-level model submissions and adjudications

- [`candidate-verdicts-original-75.csv`](candidate-verdicts-original-75.csv) contains the 799 candidate submissions and candidate-level adjudications from the original 75-case batch.
- [`candidate-adjudication-79.csv`](candidate-adjudication-79.csv) contains the 16 candidate submissions from the four-case supplement. It is not a 79-row case table: runs with no candidate do not create candidate rows.
- [`condition-run-results-474.csv`](condition-run-results-474.csv) contains one row per B0/P1 run, including empty submissions, target-hit outcomes, token usage, elapsed time, and recorded estimated cost. It combines 450 original-batch runs and 24 supplemental runs.
- [`run-results-original-75.csv`](run-results-original-75.csv) contains the 450 original-batch run records.
- [`paired-results-original-75.csv`](paired-results-original-75.csv) contains the 225 original-batch B0/P1 paired comparisons.
- [`evaluation-summary-79.json`](evaluation-summary-79.json) and [`evaluation-summary-79.md`](evaluation-summary-79.md) report the combined totals, exclusions, paired results, and limitations.

The combined evaluation has 474 runs, 815 candidate submissions, and 468 scoreable runs (234 B0 and 234 P1). Its designated-target hit totals are B0 28/234 and P1 36/234. This combined total pools three model settings and is descriptive, not an independent-sample estimate. The primary per-setting comparison is in [`../summary.md`](../summary.md).

## Interpretation limits

Candidate verdicts compare each submitted candidate with the dataset-designated target. `NO_TARGET_MATCH` does not establish that a candidate is harmless or a false positive. `PARTIAL` is not a designated-target hit. These are source/patch/test-based adjudications, not dynamic reproductions or independent multi-rater judgments. The files preserve the earlier 75-case adjudication and the later four-case supplement rather than rewriting the provenance of either batch.
