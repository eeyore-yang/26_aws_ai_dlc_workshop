# AI-DLC Audit Log

## Workflow Start
**Timestamp**: 2026-05-20T09:00:00Z
**User Input**: "AI-DLC 워크플로우를 시작해봅시다."
**AI Response**: Displayed welcome message and initiated Workspace Detection
**Context**: New AI-DLC workflow initiated for AI 데이터 분석가 챗봇 project

---

## INCEPTION - Workspace Detection
**Timestamp**: 2026-05-20T09:01:00Z
**User Input**: (initial request - same as above)
**AI Response**: Completed workspace scan. Findings:
- Brownfield project with skeleton stubs (all modules have NotImplementedError)
- Python 3.11+, pip build system
- Prompts (system_prompt.txt, few_shot_examples.yaml) already complete
- Data directory contains fact_events.csv (S3 업로드 대상)
- Decision: Skip Reverse Engineering (code is stub-level), proceed to Requirements Analysis
**Context**: Workspace Detection stage completed. Next: Requirements Analysis

---

## INCEPTION - Requirements Analysis (Start)
**Timestamp**: 2026-05-20T09:02:00Z
**AI Response**: Intent analysis completed:
- Request Clarity: Clear (project purpose, schema, tech stack, acceptance criteria well-defined)
- Request Type: New Project (complete skeleton implementation)
- Scope: Multiple Components (5 modules)
- Complexity: Moderate (Text2SQL pipeline + chart + UI integration)
- Depth: Standard
- Created requirement-verification-questions.md with 8 questions (including extension opt-ins)
- Awaiting user answers
**Context**: Requirements Analysis stage - Step 6 (Clarifying Questions) created

---

## Architecture Decision Record (ADR-001)
**Timestamp**: 2026-05-20T09:10:00Z
**Decision**: 데이터 레이어 = Athena + S3 + Glue Catalog
**Status**: Accepted

### 배경
Kiro skeleton이 DuckDB 기반으로 생성되었으나 프로젝트 원래 의도와 불일치. DuckDB 관련 내용 전체 제거 후 Athena 단일 아키텍처로 확정.

### 아키텍처
자연어 입력 → Bedrock (Text2SQL) → Athena → S3 + Glue Catalog → 결과 반환

### 영향 범위
- T4 (SQL 실행 레이어): Athena executor 구현
- T1 (데이터 마트): S3 업로드 + Glue Crawler 실행
- T3 (Text2SQL): 변경 없음
- T5/T6 (차트/UI): 변경 없음

### 다음 액션
1. src/data_executor.py에 AthenaExecutor 클래스 구현
2. S3 버킷 경로 및 Glue Database 이름을 config.yaml에 정의
3. 환경변수 EXECUTOR_MODE=athena 로 고정

---

## INCEPTION - Requirements Analysis (Answers Received)
**Timestamp**: 2026-05-20T09:15:00Z
**User Input**: "Requirements Verification Questions 에 답변 달았어. 이 다음은 뭐지?"
**AI Response**: Answers validated (no contradictions). Generated requirements.md.
**Answers Summary**:
- Q1: B (fact_events.csv 준비됨, 2만행)
- Q2: A (Bedrock 실패 → MOCK_MODE 자동 전환)
- Q3: A (단일 턴)
- Q4: B (x_col, y_col 명시적 매핑)
- Q5: A (Athena + S3 + Glue Catalog)
- Q6: D (전체 통합)
- Q7: B (Security 규칙 건너뛰기)
- Q8: C (PBT 규칙 건너뛰기)
**Context**: Requirements Analysis completed. Extensions disabled (Security: No, PBT: No). Next: Approval gate.

---

## Architecture Decision Record (ADR-002)
**Timestamp**: 2026-05-20T09:25:00Z
**Decision**: 차트 생성 = Bedrock LLM 직접 생성 (Plotly 제거) + 2개 모델 아키텍처
**Status**: Accepted

### 배경
사용자 요구사항 변경: Plotly로 x_col/y_col 매핑하여 차트를 로컬 생성하는 대신, Bedrock LLM이 차트 이미지를 직접 생성하도록 변경. 자연어 처리(Text2SQL)와 차트 생성을 각각 별도 모델이 담당하는 2-모델 아키텍처로 확정.

### 변경 전
자연어 → Bedrock (단일 모델: SQL + chart_type + x_col + y_col) → Athena → Plotly 차트 → Streamlit

### 변경 후
자연어 → Bedrock Model-1 (SQL + summary) → Athena → Bedrock Model-2 (차트 이미지 생성) → Streamlit

### 영향 범위
- FR-1: chart_type, x_col, y_col 필드 제거 → SQL + summary만 반환
- FR-4: Plotly 제거 → Model-2가 차트 이미지 직접 생성
- FR-5: Plotly 차트 → LLM 생성 이미지 표시
- constraints.md: Plotly OUT OF SCOPE로 이동, 2개 모델 허용
- 환경변수: BEDROCK_MODEL_ID → BEDROCK_TEXT2SQL_MODEL_ID + BEDROCK_CHART_MODEL_ID

### 수정된 파일
1. .kiro/steering/project.md
2. .kiro/steering/constraints.md
3. aidlc-docs/inception/requirements/requirements.md

---

## Architecture Decision Record (ADR-003)
**Timestamp**: 2026-05-20T09:30:00Z
**Decision**: MOCK_MODE 제거
**Status**: Accepted

### 배경
MOCK_MODE는 Bedrock 미연결 시 UI 흐름 테스트용이었으나, 2-모델 아키텍처에서 mock 구현 부담이 커지고 AWS Summit 워크샵 환경에서 Bedrock 접근이 보장되므로 제거.

### 근거
1. AWS Summit 환경에서 Bedrock 접근 보장됨
2. 2-모델 mock (Text2SQL + 차트 이미지) 구현 비용 > 실익
3. 에러 처리(graceful degradation)로 대체 가능
4. 6시간 제약 내 핵심 기능 집중이 우선

### 대체 전략
- Model-1 실패 → 에러 메시지 + 재시도 유도
- Model-2 실패 → 차트 없이 텍스트 요약 + 테이블만 표시

### 영향 범위
- FR-6 (MOCK_MODE) 전체 삭제
- 완성 기준 3번 항목 삭제
- 환경변수 MOCK_MODE 삭제
- constraints.md IN SCOPE에서 MOCK_MODE 항목 삭제

---

## INCEPTION - Requirements Analysis (Approved)
**Timestamp**: 2026-05-20T09:35:00Z
**User Input**: "승인. 이제 밥먹을 거임."
**AI Response**: Requirements approved. Proceeding to Workflow Planning.
**Context**: Requirements Analysis stage completed. Next: Workflow Planning

---

## Architecture Decision Record (ADR-004)
**Timestamp**: 2026-05-20T09:40:00Z
**Decision**: 3-모델 파이프라인 확정 (Text2SQL → Chart → Description)
**Status**: Accepted

### 배경
기존 2-모델(Text2SQL+Chart)에서 Description 작성을 별도 모델로 분리. Athena 결과와 차트 이미지를 취합하여 한국어 설명을 작성하는 Model-3 추가.

### 확정 파이프라인
```
자연어 → Model-1 (Text2SQL) → Athena → Model-2 (차트 이미지 생성) → Model-3 (데이터+차트 취합 → Description) → Streamlit
```

### 각 모델 역할
- Model-1: 자연어 → SQL 변환만 담당 (summary 제거)
- Model-2: Athena 결과 → 차트 이미지 생성
- Model-3: Athena 결과 + 차트 이미지 → 한국어 설명(description) 작성

### 영향 범위
- FR-1: summary 필드 제거, SQL만 반환
- FR-4: 차트 이미지를 Model-3에 전달하는 흐름 추가
- FR-5: 신규 (Description 작성)
- FR-6: UI에서 description + 차트 + 테이블 표시
- 환경변수: BEDROCK_DESCRIPTION_MODEL_ID 추가

---

## INCEPTION - Workflow Planning (User Override)
**Timestamp**: 2026-05-20T09:50:00Z
**User Input**: "건너 뛰지 말고, inception에서 requirement analysis를 했으니, user stories부터 진행해줘."
**AI Response**: Execution plan updated. User requested full Inception execution starting from User Stories.
**Context**: User overrode skip recommendations. Proceeding with User Stories → Application Design → Units Generation → full Construction.

---

## INCEPTION - User Stories
**Timestamp**: 2026-05-20T09:55:00Z
**User Input**: "유저의 자연어 입력은 예시(20~30개)를 미리 만들어 사용하는 프로토 타입 프로젝트야. data/fact_events.csv 데이터만 사용할거야. 유저 스토리를 이 내용을 참고해서 다시 작성해줘."
**AI Response**: User Stories generated based on actual CSV schema (전자제품 주문 데이터):
- 2 personas: 데모 운영자, 데모 관객
- 11 user stories (US-1~US-11): 9개 정상 흐름 + 2개 에러 처리
- 20개 사전 정의 질문 예시 포함
- Acceptance Criteria: 체크리스트 형식
- CSV 실제 컬럼 기반 (Customer ID, Age, Gender, Product Type, Total Price 등)
**Context**: User Stories Part 2 (Generation) completed. Awaiting approval.

---

## INCEPTION - User Stories (Approved)
**Timestamp**: 2026-05-20T10:00:00Z
**User Input**: "Application Design 진행해줘."
**AI Response**: User Stories implicitly approved. Proceeding to Application Design.
**Context**: User Stories stage completed.

---

## INCEPTION - Application Design
**Timestamp**: 2026-05-20T10:01:00Z
**User Input**: (continuation from above)
**AI Response**: Application Design artifacts generated:
- components.md: 5 components (bedrock_client, query_parser, data_executor, visualizer, app)
- component-methods.md: 9 method signatures
- services.md: Pipeline orchestrator (app.py 내장), 에러 처리 전략
- component-dependency.md: 의존성 매트릭스 + 데이터 흐름도
- application-design.md: 통합 문서
**Context**: Application Design completed. Awaiting approval.

---

## CONSTRUCTION - Code Generation
**Timestamp**: 2026-05-20T10:10:00Z
**User Input**: "코더 모델을 사용해서 code generation을 진행해줘"
**AI Response**: Code Generation Part 1 (Planning) + Part 2 (Generation) completed in single pass.
- Generated 11 files total:
  - config.yaml (환경 설정)
  - prompts/system_prompt.txt (실제 CSV 스키마 반영)
  - prompts/few_shot_examples.yaml (10개 예시, 실제 컬럼 기반)
  - prompts/chart_prompt.txt (Model-2 프롬프트)
  - prompts/description_prompt.txt (Model-3 프롬프트)
  - src/query_parser.py (프롬프트 조립)
  - src/bedrock_client.py (3-모델 호출)
  - src/data_executor.py (Athena 실행)
  - src/visualizer.py (차트+설명 래퍼)
  - src/app.py (Streamlit UI + 파이프라인)
  - requirements.txt (의존성 업데이트)
**Context**: Code Generation completed. All 12 plan steps marked [x].

---

## Documentation Correction (ADR-005)
**Timestamp**: 2026-05-20T15:20:00Z
**Decision**: 문서 정정 — 실제 구현과 문서 불일치 해소
**Status**: Accepted

### 정정 항목
1. 리전: ap-northeast-2 → us-east-1
2. 모델 ID: claude-3-5-sonnet-v2 (EOL) → us.anthropic.claude-sonnet-4-20250514-v1:0
3. CSV 스키마: 구 스키마(event_type 기반) → 실제 CSV(전자제품 주문 데이터)
4. 차트 생성: "LLM이 직접 이미지 생성" → "LLM이 matplotlib 코드 생성 → 로컬 실행"
5. OUT OF SCOPE: matplotlib 제거 (LLM 코드 실행 도구로 허용)
6. Athena 제약: OpenCSVSerde 모든 컬럼 STRING, CAST 필수 추가
7. 전환율 공식 → 취소율 공식으로 변경
8. 완성 기준: 실제 데이터에 맞는 질문으로 교체

### 영향
- 코드 변경 없음 (이미 올바르게 구현됨)
- 문서만 현실에 맞춤

---
