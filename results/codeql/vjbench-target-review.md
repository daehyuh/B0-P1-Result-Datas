> Historical snapshot. Current CodeQL/B0/P1 statistics are in [the current summary](../summary.md).

# VJBench 42사례 CodeQL 지정 취약점 대조

기준일: 2026-10-08. CodeQL 2.23.2, Java security-extended 쿼리 묶음, build-mode none. P1은 DeepSeek V4.1 Flash Max Top-1의 2026-10-08 정정판을 사용했다.

CodeQL은 42/42 사례를 정상 분석해 SARIF 경고 3,658건을 냈다. 지정 취약점과 직접 일치한 사례는 **4/42 (9.52%)**다. P1 LLM은 **20/42 (47.62%)**다. 차이는 16건, 38.10%p다.

| 쌍대 판정 | 사례 수 |
| --- | ---: |
| 둘 다 적중 | 3 |
| CodeQL만 적중 | 1 |
| P1만 적중 | 17 |
| 둘 다 미적중 | 21 |

판정은 사례가 지정한 CVE와 공식 수정 커밋의 원인·코드 경로를 CodeQL 경고의 규칙·위치·데이터 흐름과 대조했다. 경고 수, CWE 이름, 같은 파일이라는 사실만으로 적중 처리하지 않았다. 경고가 지정 취약점과 다르다는 판정은 그 경고가 실제로 안전하다는 뜻이 아니다.

case-035의 경로 입력 경고는 수정된 정적 파일 처리 흐름과 관련 있지만, 기존 경로 검사에서 인코딩된 상위 디렉터리 이동을 놓치는 구체적 결함을 지적하지 않는다. 엄격한 주 판정에서는 미적중이다. 이 관련 흐름을 적중으로 보는 완화 기준을 택하면 CodeQL은 5/42(11.90%)이며, P1의 20/42는 변하지 않는다.

경고가 0건인 사례는 8건(case-008, case-013, case-016, case-017, case-020, case-028, case-033, case-034)이다. 완료 상태와 Java 파일 수가 모두 확인된 분석이며, 경고 0건을 분석 실패로 바꾸지 않았다.

## 사례별 판정

| 사례 | CVE | CodeQL 경고 | CodeQL | P1 | 근거 |
| --- | --- | ---: | --- | --- | --- |
| case-001 Netty-1 | CVE-2019-16869 | 456 | 미적중 | 미적중 | 헤더 이름의 콜론 앞 공백을 허용하는 HttpObjectDecoder 경고가 없다. 표시된 HTTP 분할 경고는 다른 헤더 검증 비활성화 위치다. (검토 경고 #18;19) |
| case-002 Netty-2 | CVE-2019-20444 | 427 | 미적중 | 미적중 | 콜론 누락 헤더를 파싱하는 HttpObjectDecoder 경고가 없다. 표시된 HTTP 분할 경고는 다른 위치다. (검토 경고 #18;19) |
| case-003 Jenkins-1 | CVE-2017-2600 | 202 | 미적중 | 미적중 | Computer.java 경고는 역직렬화 위치 1457행이며 NodeMonitor API 접근 권한 검사와 다르다. (검토 경고 #76) |
| case-004 Jenkins-2 | CVE-2017-2606 | 207 | 미적중 | 미적중 | Jenkins.java의 경로·리다이렉트 경고는 작업 목록의 READ 권한 검사 누락과 다르다. (검토 경고 #49;86) |
| case-005 Jenkins-3 | CVE-2017-2609 | 202 | 미적중 | 미적중 | Jenkins.java의 경로·리다이렉트 경고는 검색 결과의 View 권한 필터링과 다르다. (검토 경고 #45;82) |
| case-006 Jinjava-1 | CVE-2018-18893 | 1 | 미적중 | 적중 | getClass() 호출 제한을 빠뜨린 BeanELResolver 경고가 없다. |
| case-007 Halo-1 | CVE-2020-21522 | 90 | 미적중 | 적중 | FileUtils의 다른 파일 작업에 경로 입력 경고가 있지만, checkDirectoryTraversal의 정규화 순서 오류를 가리키지 않는다. (검토 경고 #18;21;22;23) |
| case-008 Retrofit-1 | CVE-2018-1000844 | 0 | 미적중 | 미적중 | JAXB 응답 파서의 외부 엔터티 문제에 관한 경고가 없다. |
| case-009 Quartz-1 | CVE-2019-13990 | 29 | 미적중 | 적중 | 작업 XML 파서의 외부 엔터티 처리 경고가 없다. |
| case-010 Flow-1 | CVE-2021-33604 | 35 | 미적중 | 미적중 | DevModeHandler의 XSS·SSRF·로그 경고는 지정된 개발 모드 URL 문자 처리 문제와 다르다. (검토 경고 #10;12;24) |
| case-011 Flow-2 | CVE-2021-31412 | 35 | 미적중 | 미적중 | RouteNotFoundError의 라우트 정보 처리 경고가 없다. |
| case-012 BC-Java-1 | CVE-2016-1000338 | 73 | 미적중 | 미적중 | DSASigner의 서명 시퀀스 길이 검사 경고가 없다. |
| case-013 Json-sanitizer-1 | CVE-2020-13973 | 0 | 미적중 | 미적중 | JsonSanitizer의 HTML 주석과 script 경계 이스케이프 경고가 없다. |
| case-014 Ratpack-1 | CVE-2019-17513 | 11 | 적중 | 미적중 | NettyHandlerAdapter.java:159에서 DefaultHttpHeaders(false)를 통한 헤더 검증 비활성화를 정확히 경고한다. 수정 커밋도 같은 문장을 바꾼다. (검토 경고 #1) |
| case-015 Pulsar-1 | CVE-2021-41571 | 509 | 미적중 | 미적중 | PersistentTopicsBase의 많은 로그 경고는 메시지 ID 조회 권한 검사 누락과 다르다. (검토 경고 #39) |
| case-016 TorpedoQuery-1 | CVE-2019-11343 | 0 | 미적중 | 적중 | LIKE 값의 SQL/JPQL 이스케이프 문제에 관한 경고가 없다. |
| case-017 Nmap4j-1 | CVE-2018-17228 | 0 | 미적중 | 적중 | nmap 호스트 인자의 입력 검증 문제에 관한 경고가 없다. |
| case-018 Pac4j-1 | CVE-2021-44878 | 64 | 미적중 | 미적중 | OIDC 설정 및 사용자 정보 검증 수정 위치의 경고가 없다. |
| case-019 JAI-EXT-1 | CVE-2022-24816 | 40 | 미적중 | 적중 | Jiffle 입력이 생성 Java 주석을 벗어나는 코드 주입 경고가 없다. |
| case-020 Jackson-Modules-1 | CVE-2018-1000873 | 0 | 미적중 | 적중 | JSR-310 BigDecimal 변환의 자원 사용 문제에 관한 경고가 없다. |
| case-021 Apollo-1 | CVE-2020-15170 | 31 | 미적중 | 미적중 | Apollo 경고는 포털 SSRF와 ConfigService 로그에 관한 것으로 AdminService 인증 누락과 다르다. (검토 경고 #7;22) |
| case-022 Openfire-1 | CVE-2019-18394 | 316 | 적중 | 적중 | FaviconServlet.java:119의 요청 매개변수가 191행의 외부 URL 요청에 도달하는 SSRF 흐름을 경고한다. (검토 경고 #44) |
| case-023 Jooby-1 | CVE-2019-15477 | 18 | 미적중 | 미적중 | 지정 수정은 Err 오류 페이지의 HTML 이스케이프다. CodeQL의 로그·응답 분할 경고는 그 반사 XSS와 다르다. (검토 경고 #6;12;13;14) |
| case-024 Emissary-1 | CVE-2021-32634 | 240 | 적중 | 적중 | WorkSpaceAdapter·WorkSpaceClientEnqueueAction·PayloadUtil에서 요청 값이 ObjectInputStream으로 전달되는 역직렬화 흐름을 경고한다. (검토 경고 #27;28;29) |
| case-025 Spark-1 | CVE-2016-9177 | 17 | 적중 | 적중 | 정적 파일 요청 경로가 ExternalResourceHandler·ClassPathResourceHandler를 지나 파일 작업에 도달한다. 수정 커밋은 바로 이 흐름에 디렉터리 경계 검사를 추가한다. (검토 경고 #1;3;9) |
| case-026 Xwiki-commons-1 | CVE-2022-24898 | 4 | 미적중 | 미적중 | XXE 경고는 XWikiExtensionRepository.java:322에 있다. 지정 수정 위치인 XMLUtils의 기본 XML 파서 설정과 다르다. (검토 경고 #1) |
| case-027 Elide-1 | CVE-2020-5289 | 4 | 미적중 | 미적중 | 필터 정규식 성능 경고는 사용자 필터식의 ReadPermission 검사 누락과 다르다. (검토 경고 #3;4) |
| case-028 GoCD-1 | CVE-2022-24832 | 0 | 미적중 | 적중 | LDAP 검색 필터 값의 이스케이프 문제에 관한 경고가 없다. |
| case-029 BC-Java-2 | CVE-2016-1000344 | 73 | 미적중 | 미적중 | IES/ECIES의 비-CBC 암호 모드 허용 문제를 지적한 경고가 없다. |
| case-030 Flow-3 | CVE-2018-25007 | 14 | 미적중 | 미적중 | ElementPropertyMap의 클라이언트 속성 갱신 제한 문제에 관한 경고가 없다. |
| case-031 XStream-1 | CVE-2020-26217 | 2 | 미적중 | 적중 | 두 경고는 정규식 성능 문제이며 XStream 기본 타입 허용 목록 누락과 다르다. (검토 경고 #1;2) |
| case-032 XStream-2 | CVE-2021-43859 | 2 | 미적중 | 미적중 | 두 경고는 정규식 성능 문제이며 재귀 컬렉션·맵 해시 계산 DoS와 다르다. (검토 경고 #1;2) |
| case-033 Jackson-databind-1 | CVE-2017-15095 | 0 | 미적중 | 적중 | BeanDeserializerFactory의 다형 역직렬화 타입 차단 누락 경고가 없다. |
| case-034 Jackson-databind-2 | CVE-2018-7489 | 0 | 미적중 | 적중 | SubTypeValidator의 다형 역직렬화 타입 차단 누락 경고가 없다. |
| case-035 Flow-4 | CVE-2020-36321 | 38 | 미적중 | 미적중 | 정적 파일 경로에 일반적인 경로 입력 경고가 있으나, 기존 isPathSafe가 인코딩된 상위 디렉터리 이동을 놓치는 지정 원인을 식별하지 못한다. 관련 흐름으로 별도 표시한다. (검토 경고 #1;2) |
| case-036 Netty-3 | CVE-2021-43797 | 453 | 미적중 | 적중 | 헤더 검증 비활성화 경고는 프록시·벤치마크 위치에 있다. 지정된 HTTP 헤더 이름 문자 검증 결함과 다르다. (검토 경고 #19) |
| case-037 Lemminx-1 | CVE-2022-0673 | 2 | 미적중 | 적중 | 캐시 자원의 경로 순회와 관련된 경고가 없다. |
| case-038 Jdom-1 | CVE-2021-33813 | 3 | 미적중 | 적중 | SAXBuilder의 외부 엔터티 처리 경고가 없다. |
| case-039 Lemminx-2 | CVE-2022-0671 | 2 | 미적중 | 적중 | 수정된 CVE 정답은 외부 스키마 다운로드의 SSRF/DoS다. 해당 자원 요청 경고가 없다. |
| case-040 Lemminx-3 | CVE-2022-0672 | 2 | 미적중 | 미적중 | 외부 자원 다운로드의 허용 스킴·리다이렉트 제한 결함 경고가 없다. |
| case-041 TwelveMonkeys-1 | CVE-2021-23792 | 49 | 미적중 | 적중 | XMPReader의 외부 XML 자원 처리 경고가 없다. 다른 모듈의 XSS·경로 경고는 별개다. |
| case-042 CometD-1 | CVE-2022-24721 | 7 | 미적중 | 적중 | Oort·Seti 채널 구독과 게시 권한 검사 경고가 없다. |

## 재현 근거와 제한

- 행 단위 원장: `VJBench-CodeQL-42사례-지정취약점-판정.csv`. 각 행에 CVE, 공식 수정 커밋 URL, CodeQL 원본 SARIF 해시, 검토 경고 번호를 기록했다.
- 원본 CodeQL 결과: `../runs/vjbench/case-XXX/result.json`과 `alerts.sarif.gz`. 경고 번호는 압축을 푼 SARIF의 첫 번째 `runs[0].results`에서 1부터 센 순서다.
- P1 비교 자료: `../../deepseek-model-comparison-vjbench-top1-flash-max-20261001/results/top1-full-adjudication-20261008.csv`. case-019는 수정한 소스로 다시 실행한 P1 선택 결과다. CodeQL도 Java 파일 415개가 있는 수정된 소스를 분석했다.
- case-023의 기존 P1 결과표에는 대상이 ApiTool theme XSS로 요약돼 있지만, 데이터셋 CSV가 지정한 CVE-2019-15477 수정 커밋은 오류 페이지의 HTML 이스케이프를 고친다. 여기서는 공식 수정 커밋을 기준으로 CodeQL을 판정했다. P1의 기존 미적중 여부는 바뀌지 않는다.
- case-039의 CSV 수정 커밋은 CVE-2022-0671의 보안 수정이 아니므로 기존 `case-039-adjudication-correction-20261006.json`에 기록된 실제 보안 수정 커밋을 적용했다.
- CodeQL은 사례당 경고 여러 건을 냈고 P1은 Top-1 후보 하나를 제출했다. 이 표는 지정 취약점을 한 건이라도 맞혔는지에 관한 사례 단위 비교다. 경고 전체의 정밀도나 모든 실제 취약점에 대한 재현율은 측정하지 않았다. CodeQL의 build-mode none 분석 범위와 P1의 소스·관계 조회 범위도 완전히 같지는 않다.
- 이 대조는 연구 보조 검토이며 독립된 인간 평가자 두 명의 블라인드 판정이나 동적 재현은 아니다.
