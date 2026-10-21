# B0–P1 Java vulnerability detection results

| Dataset | Cases | CodeQL | B0 | P1 | P1−B0 (cases; pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| VJBench | 42 | 4 (9.52%) | 16 (38.10%) | 16 (38.10%) | +0; +0.00 pp |
| Vul4J+ | 140 | 17 (12.14%) | 39 (27.86%) | 46 (32.86%) | +7; +5.00 pp |
| CWE-Bench-Java | 213 | 41 (19.25%) | 52 (24.41%) | 51 (23.94%) | -1; -0.47 pp |

All paired LLM submissions use Flash Max (`deepseek-flash`, reasoning effort `max`) and permit at most one candidate. B0 reads prepared source; P1 also queries read-only VulRIS relations. The metric is reference-cause and affected-path matching. CodeQL is the recorded baseline; exact source-version parity with every corrected LLM input has not been established.

Legacy Vul4J multi-candidate responses and their derived comparisons have been removed from the current tree. The separate Vul4J P1 Top1 experiment (79 completed reviews, October 9–10) remains preserved. It has no matching Top1 B0 in the recorded experiment and is not substituted with old multi-candidate B0 results.

[Case rows, reports, labels and hashes](results/final-flash-max-20261021/).

[Relation builder](analyzer/) · [Prompts](prompts/) · [CodeQL baseline](results/codeql/)
