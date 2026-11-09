# Vul4J+ 논문 포함 모델 이진 판정

판정값은 적중/미적중 두 값뿐이며 완료된 140건 조건만 성능을 산정했다.

> B0 네 조건은 2026-11-03 응답 무결성 점검과 원본 데이터셋 기준 재판정을 거친 최종값이다.

> GPT-5.6 Luna High/Max의 B0·P1은 사용자 결정에 따라 논문 및 비교 실험에서 제외했다.

| condition_id | 방법·모델 | 추론 | 조건 | 적중 | 미적중 | 적중률 |
|---|---|---|---:|---:|---:|---:|
| `codeql_b0` | CodeQL | N/A | B0 | 19/140 | 121 | 13.57% |
| `deepseek_flash_max_b0` | DeepSeek 4.1 Flash Max | Max | B0 | 39/140 | 101 | 27.86% |
| `deepseek_flash_max_p1` | DeepSeek Flash Max | Max | P1 | 48/140 | 92 | 34.29% |
| `gemini_3_8_flash_high_b0` | Gemini 3.8 Flash | High | B0 | 52/140 | 88 | 37.14% |
| `gemini_3_8_flash_high_p1` | Gemini 3.8 Flash | High | P1 | 49/140 | 91 | 35.00% |
| `gpt_6_luna_high_b0` | GPT-6 Luna | High | B0 | 15/140 | 125 | 10.71% |
| `gpt_6_luna_high_p1` | GPT-6 Luna | High | P1 | 18/140 | 122 | 12.86% |
| `gpt_6_luna_max_b0` | GPT-6 Luna | Max | B0 | 20/140 | 120 | 14.29% |
| `gpt_6_luna_max_p1` | GPT-6 Luna | Max | P1 | 23/140 | 117 | 16.43% |

## QA

- 완료 조건 9개 × 140건 = 1,260개 판정
- 각 조건의 사례 ID 집합이 동일하며 누락·중복 0건
- 판정값은 적중/미적중만 사용

## 입력 산출물 검증

| 입력 | 원본 행수 | 사용 행수 | 누락 | 중복 | SHA-256 |
|---|---:|---:|---:|---:|---|
| `codeql` | 140 | 140 | 0 | 0 | `9fe5ee2f87e29dabef68a0ddf5f49880fa9fc1b9868a34413e4e5ca1b0815419` |
| `b0_final` | 560 | 560 | 0 | 0 | `5ce24147486c27248d0a99140a3abde9d34e23a17ca0c34058db70d867b3c6c5` |
| `deepseek_p1` | 140 | 140 | 0 | 0 | `ed534020ed7498f512cc2cec136cf22cf200b94d51b64aad4b91daeb2443c6dd` |
| `gemini_p1` | 140 | 140 | 0 | 0 | `1d4bca93cf905b9316f011158edbd870521d7d4cd55ac27f22dd81c16cd915bc` |
| `gpt_high` | 560 | 140 | 0 | 0 | `a6194efcb5442b4057b98507c72a59379362f2a9971840cea46695e3fe1be5d3` |
| `gpt_max` | 560 | 140 | 0 | 0 | `25fdf65e98ebac1c8ab5071dcd51a24d9d457799e5d4d4adc8a4cbdeccd2cdd7` |

## 출력 해시

- JSON: `930c2b087eff08229ac81a4684d53f913622bf4e1e84c8cf7a3920ec510c8f8f`
- CSV: `6d537949d411f965dda47592ef5c316d109b28474d776a09099d0fe53cac3866`
- QA: `2bcc75650e3753f1f0583aee5db4e38b2d6edafd62a1f75ff1cb38c9f0fba3df`
