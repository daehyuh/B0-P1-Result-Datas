# Data sources and publication scope

## Final paper cohort

The final paper uses only the fixed 140-case Vul4J+ validation cohort. Vul4J+
is available from the upstream Zenodo record:

- Yu et al., *Vul4J+: A Dataset of Real Java Vulnerabilities*, version 2.0,
  DOI: <https://doi.org/10.5281/zenodo.13752193>

The 140 rows are held constant across CodeQL and all eight B0/P1 LLM
conditions. Case identifiers, CVEs, repositories, reference causes, candidate
claims, final binary verdicts, and provenance hashes are published in
`results/vul4jplus-final-20261110`.

## What is not redistributed

This repository does not redistribute benchmark project source trees or
generated per-case VulRIS relation databases. Those artifacts are large and
remain subject to the individual upstream projects' licenses. Use the published
case identifiers and hashes to obtain and verify the corresponding upstream
source.

The raw release asset contains experiment ledgers, prompts exchanged during the
runs, model responses, tool-call records, and token usage. It does not contain
API environment files or private coordinated-disclosure repositories.

## Historical folders

Older VJBench, Vul4J, CWE-Bench-Java, and multi-candidate files remain in the
Git history and historical result folders. They are not used by the final
Vul4J+-only paper results.
