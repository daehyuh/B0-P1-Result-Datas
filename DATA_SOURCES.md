# 데이터 출처와 공개 범위

이 저장소는 연구에서 사용한 원본 benchmark 프로젝트 소스와 생성된 per-case 관계 DB를 재배포하지 않는다. 해당 자료는 용량이 크고 여러 upstream 프로젝트의 라이선스가 각각 다르다.

| 데이터셋 | 실험 범위 | 출처 및 식별 |
|---|---|---|
| Vul4J | 79개 PoV 사례; Flash High, Flash Max, Pro Max | [Vul4J upstream](https://github.com/tuhh-softsec/Vul4J). 행 단위 CSV에 사례/CVE와 판정 근거가 있다. |
| VJBench | 42개 사례; Flash Max Top-1 | [VJBench upstream artifact](https://github.com/lin-tan/llm-vul) 및 [case-039 correction](results/vjbench/case-039-adjudication-correction-20261006.json). |
| Vul4J+ | 191개 준비 사례 중 140개 평가; Flash Max Top-1 | [Vul4J+ Zenodo record](https://zenodo.org/records/13752193). SpotBugs-only와 정답 충돌 사례는 지정 취약점 적중률 분모에서 제외했다. |
| CWE-Bench-Java | 213개 중 212개 평가; Flash Max Top-1 | [고정된 IRIS 저장소의 v2 데이터](https://github.com/iris-sast/iris/tree/v2). 평가 사례별 소스·관계 자료 해시는 CSV에 기록했다. |

결과 파일에 포함된 응답 후보, 적중 판정, CVE/CWE 및 해시는 분석 재현과 인용을 위한 것이다. 소스 코드는 각 데이터셋의 공식 출처에서 내려받아 원래 라이선스와 인용 규정을 따라야 한다. 이 저장소에는 제3자 코드에 대한 별도 라이선스를 부여하지 않는다.
