# 형식 오류 보충 재실행 기록

이 주 실험의 원본 DB와 네 개의 원본 응답은 변경하지 않았다. 원본에서 형식 검사를 통과하지 못한 리뷰 네 건을 별도 보충 실험에서 각각 한 번씩 다시 실행했다.

- 보충 결과와 네 사례의 정답 대조: `../../deepseek-model-comparison-vjbench-format-retry-20261005/results/format-retry-adjudication.md`
- 기계 판독용 통계: `../../deepseek-model-comparison-vjbench-format-retry-20261005/results/statistics-update.json`
- 네 건의 원본-재실행 연결 및 형식 검사: 보충 폴더의 `results/format-audit.json`

핵심 수치: 원본은 84건 중 80건 형식 유효, 4건 형식 오류였다. 보충 실행은 4/4건 형식 유효했다. 두 결과를 사후 결합해 형식만 보정한 기술적 관점에서는 84/84건이 유효하지만, 이를 원본 단일 실행 통계로 표시하지 않는다. 네 보충 후보의 지정 취약점 판정은 적중 0, 불일치 3, 정답 매핑 검토 보류 1(case-039)이다. 따라서 전체 84건의 적중 통계가 갱신된 것은 아니며, 보충 보고서에서 이 네 사례만 갱신했다.
