# B0·P1 실험 결과 요약

기준일: 2026-10-06. 아래 주 결과는 **원본 LLM 응답**을 기준으로 하며, VJBench case-039의 정답 연결은 공식 보안 수정 근거로 사후 정정했다. 형식 오류 보충 실행은 원본을 덮어쓰지 않고 별도로 보고한다.

## 데이터셋별 지정 타깃 적중

| 데이터셋·모델 설정 | 평가 분모 | B0 적중 | P1 적중 | 차이 (P1−B0) |
|---|---:|---:|---:|---:|
| Vul4J · Flash High | 78 | 9 (11.54%) | 14 (17.95%) | +5 |
| Vul4J · Flash Max | 78 | 9 (11.54%) | 10 (12.82%) | +1 |
| Vul4J · Pro Max | 78 | 10 (12.82%) | 12 (15.38%) | +2 |
| VJBench · Flash Max Top-1 | 42 | 18 (42.86%) | 19 (45.24%) | +1 |
| Vul4J+ · Flash Max Top-1 | 140 | 45 (32.14%) | 58 (41.43%) | +13 |

### Denominators and scoring

- **Vul4J:** 79 benchmark cases were prepared; 78 are scored per model-condition pair. `VUL4J-1` is excluded because its CVE reference conflicts with the linked patch/test target. The adjudication history and sensitivity notes are documented in the case-level evidence.
- **VJBench:** 42 cases. The original-format-valid-only rates are B0 18/39 (46.15%) and P1 19/41 (46.34%). In the fixed 42-case end-to-end view, a malformed response is not a valid successful submission. The case-039 target mapping was corrected after inspecting outputs; this is post-hoc and a limitation.
- **Vul4J+:** 191 cases were available; 50 SpotBugs-warning-only cases and one target conflict are excluded from the designated-vulnerability denominator, leaving 140.
- **CWE-Bench-Java:** retained as a separate result because B0 had more target matches than P1. It is intentionally excluded from the primary comparison table below, not erased from the public result package. The separate result file records 213 cases, 212 scoreable after excluding unresolved case-173, and both content-level and strict-format P1 scores.

## Format-retry results are supplementary

Retries do not replace original model outputs in the table above. They are separate sensitivity analyses:

| Experiment | Original result | Retry-inclusive view | What changed |
|---|---:|---:|---|
| VJBench Flash Max Top-1 | B0 18/42, P1 19/42 | B0 19/42, P1 19/42 | B0 case-039 was format-invalid originally; a separate valid retry candidate matched the corrected SSRF target. |
| Vul4J+ Flash Max Top-1 | B0 45/140, P1 58/140 | B0 45/140, P1 59/140 | One P1 format-retry candidate added a target match. |
| CWE-Bench-Java Flash Max Top-1 | B0 97/212, P1 92 content-level (91 strict) | No additional P1 target match | Eight P1 retry cases were adjudicated; none added a target match. |

The VJBench case-039 result is not a runtime reproduction. The candidate identified the SSRF component, while the adjudication did not independently establish every impact detail of the CVE. The target correction was post-hoc. Consult the case-level correction and retry files before using the retry-inclusive view.

## Interpretation

In the primary comparison table, P1 has more designated-target matches in each listed setting. This is a descriptive summary of selected experiments, not evidence of general superiority: the separate CWE-Bench-Java result goes in the opposite direction and is retained below precisely for transparency. VJBench's original format-valid-only rates are close but use different denominators (18/39 and 19/41); the retry-inclusive view is a separate sensitivity analysis and yields 19/42 for both. These single-run observations do not establish a general P1 advantage or a causal effect of relation data. A target non-match is not an adjudication that every other model candidate is false or harmless. No false-positive rate or recall over all real vulnerabilities is claimed.

## Separate experiment excluded from the primary comparison

The user-directed primary scope excludes CWE-Bench-Java Flash Max Top-1 because B0 had more designated-target matches. The complete adjudication remains published in [`cwe-bench-java/benchmark-hit-summary.md`](cwe-bench-java/benchmark-hit-summary.md) and [`cwe-bench-java/top1-adjudication.csv`](cwe-bench-java/top1-adjudication.csv): among 212 scoreable cases B0 has 97/212 (45.75%); P1 has 92/212 content matches (43.40%) or 91/212 (42.92%) under strict format qualification. This counter-result should be disclosed wherever the primary-scope table is used.

The row totals are not pooled into a single accuracy: Vul4J repeats the same 79 cases under three model settings, Vul4J+ overlaps with Vul4J, and the datasets use different prompts and submission protocols.
