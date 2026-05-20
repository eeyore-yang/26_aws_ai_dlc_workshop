# Requirements Document — AI 데이터 분석가 챗봇

## Intent Analysis Summary
| 항목 | 값 |
|------|-----|
| User Request | AI-DLC 워크플로우로 AI 데이터 분석가 챗봇 전체 구현 |
| Request Type | New Project (스켈레톤 완성) |
| Scope | Multiple Components (5개 모듈 전체) |
| Complexity | Moderate |
| Role | 전체 통합 (T1~T6 모든 태스크) |

---

## Functional Requirements

### FR-1: Text2SQL (Model-1)
- 사용자가 자연어 질문을 입력하면 Bedrock Model-1이 SQL을 생성하여 반환한다
- 시스템 프롬프트(`prompts/system_prompt.txt`)와 Few-shot 예시(`prompts/few_shot_examples.yaml`)를 포함하여 호출한다
- 각 질문은 독립적으로 처리한다 (단일 턴, 멀티턴 컨텍스트 없음)
- 반환 형식: `{"sql": "SELECT ..."}`

### FR-2: SQL 실행 레이어 (Athena)
- Bedrock이 생성한 SQL을 Amazon Athena에서 실행한다
- 데이터는 S3에 저장되고 Glue Catalog로 스키마를 관리한다
- SELECT 문만 허용한다 (INSERT/UPDATE/DELETE/DROP/CREATE 차단)
- 실행 결과를 pandas DataFrame으로 반환한다

### FR-3: 데이터 마트
- fact_events.csv (약 2만 행)를 S3에 업로드한다
- Glue Catalog에 fact_events 테이블 스키마를 등록한다 (OpenCSVSerde, 모든 컬럼 STRING)
- 스키마: customer_id, age, gender, loyalty_member, product_type, sku, rating, order_status, payment_method, total_price, unit_price, quantity, purchase_date, shipping_type, add_ons_purchased, add_on_total
- SQL에서 숫자 컬럼 사용 시 CAST 필수 (예: CAST(total_price AS DOUBLE))

### FR-4: 차트 생성 (Model-2)
- Athena 쿼리 결과(DataFrame)를 Bedrock Model-2에 전달한다
- Model-2가 matplotlib 코드를 생성하고, 로컬에서 실행하여 차트 이미지를 생성한다
- 생성된 차트 이미지(PNG bytes)를 다음 단계(Model-3)에 전달한다
- matplotlib은 LLM 코드 실행 도구로만 사용 (사람이 직접 차트 코드를 작성하지 않음)

### FR-5: Description 작성 (Model-3)
- Athena 쿼리 결과 + Model-2가 생성한 차트 이미지를 함께 Bedrock Model-3에 전달한다
- Model-3가 데이터와 차트를 종합하여 한국어 설명(description)을 작성한다
- 최종 응답: 차트 이미지 + description + 데이터 테이블을 Streamlit에 표시한다

### FR-6: Streamlit 챗봇 UI
- 채팅 인터페이스로 질문을 입력받는다
- 응답: Model-3 작성 description + LLM 생성 차트 이미지 + 데이터 테이블을 함께 표시한다
- 대화 히스토리를 UI에 유지한다 (렌더링용, Bedrock 전달 아님)

---

## Non-Functional Requirements

### NFR-1: 성능
- Athena 쿼리 응답 시간: 10초 이내 (2만 행 기준)
- Bedrock Model-1 응답 시간: 15초 이내
- Bedrock Model-2 차트 생성 시간: 30초 이내
- Bedrock Model-3 Description 작성 시간: 15초 이내

### NFR-2: 에러 처리
- Bedrock Model-1 호출 실패 → 사용자에게 에러 메시지 표시 + 재시도 유도
- Bedrock Model-2 호출 실패 → 차트 없이 Model-3에 데이터만 전달하여 description 작성
- Bedrock Model-3 호출 실패 → 차트 이미지 + 데이터 테이블만 표시 (description 없이)
- SQL 실행 실패 → 사용자에게 친절한 에러 메시지 표시
- SELECT 외 SQL 감지 → 즉시 차단 + 에러 메시지

### NFR-3: 코드 구조
- bedrock_client.py: 모든 Bedrock 호출 (Model-1 Text2SQL + Model-2 차트 생성 + Model-3 Description)
- data_executor.py: Athena 쿼리 실행
- query_parser.py: Few-shot 로더 + 프롬프트 조립
- visualizer.py: LLM 차트 이미지 처리 (Model-2 호출 래퍼 + 이미지 디코딩)
- app.py: UI 레이어만 (비즈니스 로직 없음)

### NFR-4: 환경 변수
- AWS_DEFAULT_REGION=us-east-1
- BEDROCK_TEXT2SQL_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
- BEDROCK_CHART_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
- BEDROCK_DESCRIPTION_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
- EXECUTOR_MODE=athena

---

## Acceptance Criteria

1. "제품 유형별 총 매출을 보여줘" → LLM 생성 차트 이미지 + 수치 테이블 + Model-3 한국어 설명
2. "연령대별 평균 구매 금액은?" → LLM 생성 차트 이미지 + Model-3 한국어 설명

---

## Bedrock 응답 JSON 스키마

### Model-1 (Text2SQL) 응답:
```json
{
  "sql": "SELECT ..."
}
```

### Model-2 (Chart Generation) 입력/출력:
- **입력**: 원본 질문 + Athena 쿼리 결과 (DataFrame → CSV/JSON 텍스트)
- **출력**: 차트 이미지 (base64 인코딩)

### Model-3 (Description) 입력/출력:
- **입력**: 원본 질문 + Athena 쿼리 결과 + Model-2 생성 차트 이미지
- **출력**: 한국어 설명 (description 텍스트)

---

## Out of Scope
- FastAPI / REST API 계층
- Amazon AgentCore / QuickSight
- 실시간 데이터 수집 / 동적 마트 생성
- 사용자 인증/세션 관리
- 멀티 에이전트 오케스트레이션 (3개 모델 사용은 허용)
- Docker / 컨테이너 배포
- 로컬 데이터베이스 (DuckDB, SQLite 등)
- 외부 DB (RDS, Redshift 등)
- Plotly 등 인터랙티브 차트 라이브러리 (matplotlib은 LLM 코드 실행용으로 허용)
