# CodeQL과 P1 LLM의 지정 취약점 대조

기준일: 2026-10-08. CodeQL 2.23.2의 Java `java-security-extended.qls` 쿼리를 수정 전 소스에 적용했다. 사례별 SARIF 경고의 규칙, 위치와 데이터 흐름을 데이터셋이 지정한 취약점 원인과 대조했다. 경고가 있다는 이유만으로 적중 처리하지 않았다. 완료된 실행에서 지정 원인과의 일치 근거가 확인되지 않으면 미적중으로 산정한다. 이는 다른 CodeQL 경고 전부가 오탐이라는 뜻이 아니다.

| 데이터셋 | CodeQL 실행 | CodeQL 적중 | P1 LLM 적중 | 비교 조건 |
| --- | ---: | ---: | ---: | --- |
| Vul4J | 79/79 완료 | 11/79 (13.92%) | Flash High 15/79 (18.99%), Flash Max 11/79 (13.92%), Pro Max 13/79 (16.46%) | 각 모델 설정의 동일한 79개 사례 |
| Vul4J+ | 140/140 완료 | 17/140 (12.14%) | Flash Max Top-1 59/140 (42.14%) | 동일한 140개 사례 |
| VJBench | 42/42 완료 | 4/42 (9.52%) | Flash Max Top-1 20/42 (47.62%) | 수정된 case-019 입력을 CodeQL·P1 모두 사용 |
| CWE-Bench-Java | 211/213 완료 | 공통 판정 210건 중 40건 (19.05%) | 같은 210건 중 Flash Max Top-1 91건 (43.33%) | CodeQL 실행 미완료 2건과 정답 미확정 1건 제외; 잠정 수치 |

Vul4J의 `VUL4J-1`은 연결 패치와 CVE가 서로 다른 문제를 가리켜 CVE 설명을 정답으로 정하고 재판정했다. `VUL4J-1`과 `VUL4J-29`의 CodeQL 경고는 지정 원인 적중 근거가 부족해 미적중으로 산정했다. Vul4J+의 종전 근거 부족 3건도 같은 기준으로 미적중에 포함했다. 실행 실패나 정답 자체가 불명확한 사례는 미적중으로 바꾸지 않는다.

CWE-Bench-Java에서 `case-184`는 이 기록 시점에 재실행 중이고 `case-101`은 실패 기록이 남아 있다. 둘 다 경고 0건으로 처리하지 않았다. `case-173`은 지정 CVE 정답의 신뢰성이 확정되지 않아 비교 분모에서 제외했다. 현재의 CWE 수치는 전체 213건의 최종 비교가 아니다.

사례별 판정과 근거:

- [Vul4J 사례별 판정](vul4j-target-review.csv), [판정 설명](vul4j-target-review.md), [VUL4J-1 CVE 재대조](vul4j-1-cve-review.md)
- [Vul4J+ 사례별 판정](vul4j-plus-target-review.csv), [추가 사례 근거](vul4j-plus-extra-review.json)
- [VJBench 사례별 판정](vjbench-target-review.csv), [판정 설명](vjbench-target-review.md)
- [CWE-Bench-Java 사례별 판정](cwe-bench-java-target-review.csv), [사례 검토 근거](cwe-bench-java-review.json)

이 저장소에는 결과 판정표를 보존한다. 대용량 작업 DB와 SARIF 원본은 포함하지 않는다. 따라서 이 자료만으로 모든 CodeQL 경고를 독립 재판정할 수는 없다. 사례 판정은 모델 보조 정적 검토이며 독립적인 2인 블라인드 검토나 동적 재현이 아니다. P1의 Top-1 제출과 CodeQL의 다중 경고 출력은 형식이 다르며, 여기서는 지정 취약점을 사례당 한 번이라도 맞혔는지만 비교한다. 서로 겹치는 데이터셋과 다른 모델 설정을 합쳐 하나의 정확도로 만들지 않는다. 비용·시간 우위도 이 표로 판단하지 않는다.
