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
