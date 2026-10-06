# P1 형식 오류 재실행 대상 선별 기록

작성일: 2026-10-06

## 선별 기준

원래 응답이 데이터셋에서 지정한 취약점과 의미상 일치하면, 응답 형식이 엄격한 도구 스키마를 통과하지 못했더라도 재실행 대상에서 제외한다. 빈 후보 목록이나 후보 필드가 빠진 경우는 기존 판정자료와 응답 내용을 함께 확인한다. B0와 원본 결과는 변경하지 않는다.

## 제외한 적중 사례 10건

| 데이터셋·조건 | 사례 | 판단 근거 | 재실행 상태 |
|---|---|---|---|
| VJBench, Flash High, P1 | case-008 | 원래 후보의 JAXB 응답 XML 외부 엔티티 주장이 데이터셋의 XML 외부 엔티티 수정 대상과 일치 | 대기열 제외 |
| VJBench, Flash High, P1 | case-033 | 원래 후보의 Jackson 다형성 역직렬화 제한 우회 주장이 지정된 역직렬화 취약점과 일치 | 일부 재실행 요청 후 중단; 부분 로그 보존 |
| VJBench, Pro High, P1 | case-038 | 원래 서술형 응답의 JDOM 기본 XML 파서 외부 엔티티 주장이 지정된 외부 엔티티 취약점과 일치 | 선별 전에 재실행 완료; 결과는 보존하되 추가 재실행 성과에서 제외 |
| Vul4J+, Flash Max, P1 | case-051 | `candidate-adjudication-191.csv`의 P1 판정 `target_match` | 대기열 제외 |
| Vul4J+, Flash Max, P1 | case-159 | `candidate-adjudication-191.csv`의 P1 판정 `target_match` | 대기열 제외 |
| CWE-Bench-Java, Flash Max, P1 | case-035 | `top1-adjudication.csv`의 의미 판정은 `hit`; 형식 제한을 적용한 판정은 `miss` | 대기열 제외 |
| CWE-Bench-Java, Flash Max, P1 | case-055 | `top1-adjudication.csv`의 P1 의미 판정 `hit` | 대기열 제외 |
| CWE-Bench-Java, Flash Max, P1 | case-056 | `top1-adjudication.csv`의 P1 의미 판정 `hit` | 대기열 제외 |
| CWE-Bench-Java, Flash Max, P1 | case-159 | `top1-adjudication.csv`의 P1 의미 판정 `hit` | 대기열 제외 |
| CWE-Bench-Java, Flash Max, P1 | case-170 | `top1-adjudication.csv`의 P1 의미 판정 `hit` | 대기열 제외 |

## 집계

- 엄격 스키마 오류로 처음 선별한 사례: 29건 (VJBench 7, Vul4J+ 9, CWE-Bench-Java 13)
- 원래 응답에서 지정 취약점 적중으로 판정되어 제외: 10건
- 적중이 확인되지 않아 재실행 대상으로 남긴 사례: 19건
- 선별 전에 완료된 불필요한 재실행: VJBench Pro High P1 case-038 1건
- 재실행 진행 중 적중 사실이 확인되어 중단한 건: VJBench Flash High P1 case-033 1건. 요청·토큰·비용 기록은 삭제하지 않았다.
- VJBench Flash High P1 case-035, Flash Max P1 case-027, Vul4J+ Flash Max P1 case-002/case-034는 원래 응답이 지정 취약점과 불일치해 재실행 대상에 유지했다.
- Vul4J+ Flash Max P1 case-132의 재실행은 적중 제외 선별 전에 끝났으며 원본 및 재실행 기록을 그대로 보존한다.

판정 근거 자료는 원본 결과 폴더의 `deepseek-model-comparison-vjbench-top1-flash-max-20261001/results/top1-full-adjudication-20261006.csv`, `deepseek-model-comparison-vul4jplus-top1-flash-max-review-20261003/candidate-adjudication-191.csv`, `deepseek-model-comparison-cwebench-java-top1-flash-max-20261003/results/top1-adjudication.csv` 및 해당 원래 P1 응답이다. 이 선별은 별도의 독립 인간 검토를 뜻하지 않는다.

## 2026-10-06 진행 스냅샷

- VJBench Flash High/Flash Max와 Vul4J+ Flash Max의 적중 제외 후 미적중 대상은 기존 실험 조건으로 진행 중이다.
- CWE-Bench-Java의 적중 제외 후 미적중 대상 8건은 실행기가 P1 변환 안전 여유 공간을 확보하지 못해 API 호출 전 대기 또는 일시정지했다. 실행기는 최소 6 GiB 여유를 요구했으며, 확인 시 D: 여유 공간은 1.51 GiB였다. 공간 확인을 우회하거나 안전 여유 설정을 낮추지 않았다.
- VJBench Flash High case-033은 적중 제외 판정 전에 재실행 작업이 시작되어 139개 API 요청 기록이 남았다. 실행을 중단하고 해당 행을 `excluded_prior_hit_interrupted`로 표시했다. 기록은 삭제하거나 재전송하지 않는다.
- VJBench Pro High case-038은 적중 제외 선별보다 먼저 완료되었다. 63개 API 요청을 포함한 완료 결과를 보존하고, 의도한 미적중 대상 성과에서는 제외한다.
- Vul4J+ case-132는 적중 제외 선별 전에 완료되었으며 기존 판정상 미적중이므로 재실행 대상에 포함한다.
- 2026-10-06 최근 확인 시 보충 원장 누적 추정 비용은 약 USD 1.288이다. 이는 원장 가격 스냅샷에 따른 추정치이며 실제 청구액을 뜻하지 않는다.
- 현재 적중 제외 후 남긴 19건 중 VJBench 4건과 Vul4J+ 7건, 총 11건의 재실행이 완료되었다. CWE-Bench-Java 8건은 D: 공간 부족으로 API 요청 없이 대기/일시정지 상태이며, 실행 프로세스는 현재 없다.
- 전체 보충 원장 합계는 987개 API 요청, 129,958,611 토큰이다. 이 수치에는 적중 사례로 확인되기 전에 시작한 VJBench case-033 부분 실행과 case-038 완료 실행도 들어 있다.
