# Data dictionary

## Final binary adjudication

Each row in `ALL-MODEL-VUL4JPLUS-BINARY-ADJUDICATION-20261101.csv`
represents one method/model condition on one Vul4J+ case. The public verdict
vocabulary is exactly `적중` or `미적중`.

- `condition_id`: stable condition identifier.
- `tool`, `model`, `reasoning`: evaluated analyzer or model profile.
- `condition`, `input_condition`: B0 source-only or P1 VulRIS-assisted input.
- `case_id`, `cve`, `repository`: benchmark identifiers.
- `ground_truth`, `ground_truth_vulnerability`: reference vulnerability cause.
- `claim_*`, `model_or_alert_claim`, `claim_paths`: submitted candidate evidence.
- `verdict`, `rationale`: final binary decision and case-level justification.
- `source_artifact_sha256`, `source_artifact_key`: provenance of the adjudicated input.

Absolute workstation paths from the internal artifacts are replaced with
portable `artifact://` references. No verdict, rationale, hash, identifier, or
model response is changed by that transformation.

## `model-condition-metrics.csv`

- Turn and tool-call columns are per-case means over 140 cases.
- `total_output_tokens` is the aggregate output token count for the condition.
- `reasoning_tokens_within_output` is the reasoning-token subset reported by
  the provider.
- `total_tokens` is the aggregate input-plus-output total for the condition.

## `p1-relation-tool-metrics.csv`

- `total_calls` is the aggregate tool-call count over 140 P1 cases.
- `mean_calls_per_case` is `total_calls / 140`.
- `cases_using_tool*` reports tool coverage over all 140 cases.
- `hit_cases_using_tool*` reports coverage among the condition's hit cases.
- `hit_rate_among_tool_users_pct` is descriptive and does not establish causal
  contribution by a tool.

## Raw ledgers

The GitHub Release asset contains the SQLite ledgers and four adjudication
criteria artifacts used for log-level analysis. The ZIP member list is recorded
in `RAW-LEDGER-MANIFEST.md`.
