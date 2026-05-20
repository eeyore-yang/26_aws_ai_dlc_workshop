# Requirements Verification Questions

아래 질문에 답변해 주세요. 각 질문의 `[Answer]:` 태그 뒤에 선택지 문자를 입력해 주세요.
적합한 선택지가 없으면 마지막 옵션(Other)을 선택하고 설명을 추가해 주세요.

---

## Question 1
fact_events.csv 데이터는 이미 준비되어 있나요? 대략적인 행 수는?

A) 예, 준비됨 — 1만 행 이하
B) 예, 준비됨 — 1만~10만 행
C) 예, 준비됨 — 10만 행 이상
D) 아직 미준비 — 샘플 데이터 생성 필요
E) Other (please describe after [Answer]: tag below)

[Answer]: B (2만행)

---

## Question 2
Bedrock 호출 실패 시 에러 처리 전략은?

A) MOCK_MODE 자동 전환 (Bedrock 실패 → 하드코딩된 mock 응답 반환)
B) 사용자에게 에러 메시지만 표시하고 재시도 유도
C) 3회 재시도 후 실패 시 에러 메시지 표시
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 3
챗봇 대화 히스토리를 Bedrock에 전달해야 하나요? (멀티턴 컨텍스트)

A) 아니오 — 매 질문을 독립적으로 처리 (단일 턴)
B) 예 — 최근 3~5개 대화를 컨텍스트로 전달
C) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 4
차트 생성 시 DataFrame 컬럼 매핑 규칙은?

A) 첫 번째 컬럼 = X축(카테고리), 두 번째 컬럼 = Y축(값) — 단순 규칙
B) Bedrock 응답에 x_col, y_col 필드를 추가하여 명시적 매핑
C) 컬럼 타입 자동 감지 (문자열 → 카테고리, 숫자 → 값)
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 5
SQL 실행 레이어는?

A) Athena + S3 + Glue Catalog
B) Other (please describe after [Answer]: tag below)

[Answer]: A 

---

## Question 6
현재 담당하시는 역할 브랜치는?

A) dev/A — AI·백엔드 (T3: Text2SQL 모듈, T4: SQL 실행 레이어)
B) dev/B — 데이터·프롬프트 (T1: CSV 전처리 + S3/Glue 마트, T2: Few-shot + 시스템 프롬프트)
C) dev/C — 프론트·차트 (T5: 차트 생성 모듈, T6: Streamlit 챗봇 UI)
D) 전체 통합 — 모든 태스크를 한 번에 구현
E) Other (please describe after [Answer]: tag below)

[Answer]: D

---

## Question 7: Security Extensions
이 프로젝트에 보안 확장 규칙을 적용해야 하나요?

A) 예 — 모든 SECURITY 규칙을 블로킹 제약으로 적용 (프로덕션 수준 앱에 권장)
B) 아니오 — SECURITY 규칙 건너뛰기 (PoC, 프로토타입, 실험 프로젝트에 적합)
C) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 8: Property-Based Testing Extension
이 프로젝트에 속성 기반 테스트(PBT) 규칙을 적용해야 하나요?

A) 예 — 모든 PBT 규칙을 블로킹 제약으로 적용 (비즈니스 로직, 데이터 변환이 있는 프로젝트에 권장)
B) 부분 적용 — 순수 함수와 직렬화 라운드트립에만 PBT 규칙 적용
C) 아니오 — PBT 규칙 건너뛰기 (단순 CRUD, UI 전용 프로젝트에 적합)
D) Other (please describe after [Answer]: tag below)

[Answer]: C
