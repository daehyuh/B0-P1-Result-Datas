# 형식 오류 보충 실행

이 폴더의 자료는 원본 응답과 분리된 후속 실행 기록이다. 표의 주 적중률을 만들기 위해 원본 응답을 소급 교체하지 않는다.

- `format-retry-adjudication.md` and `format-audit.json`: VJBench의 형식 재실행과 판정.
- `retry-adjudication.md` and `.json`: CWE-Bench-Java P1 형식 재실행 판정.
- `deepseek-p1-format-retry-hit-screening-20261006.md`: 원래 응답이 이미 지정 타깃에 적중한 사례를 재실행 대상에서 제외한 선별 기록. 이 문서에는 서로 다른 모델 설정의 후속 작업도 포함되므로 Flash Max Top-1 주 실행과 혼합하지 않는다.

개별 원본·보충 후보는 데이터셋별 adjudication 결과 파일에서 구분한다. 원시 API 트랜스크립트, 실행 DB, 로그, 소스 코드 복사본은 공개하지 않는다.
