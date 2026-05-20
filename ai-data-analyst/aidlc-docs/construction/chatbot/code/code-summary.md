# Code Summary — AI 데이터 분석가 챗봇

## 개요
3-모델 파이프라인 기반 AI 데이터 분석가 챗봇. 자연어 질문을 SQL로 변환하고, Athena에서 실행한 결과를 차트와 한국어 설명으로 제공한다. 추가로 동적 데이터 마트(VIEW) 생성 기능을 포함한다.

## 아키텍처

```
자연어 입력
    │
    ▼
┌─────────────────┐
│  Intent 분류    │ ← mart_agent.classify_intent()
│  (Model-1)      │
└────┬───────┬────┘
     │       │
     ▼       ▼
[simple]  [mart_creation]
     │       │
     │       ▼
     │  ┌──────────────┐
     │  │ VIEW 생성    │ ← mart_agent.create_mart_view() + execute_mart_creation()
     │  │ (Model-1)    │
     │  └──────┬───────┘
     │         │
     ▼         ▼
┌─────────────────┐
│  Text2SQL       │ ← bedrock_client.ask_text2sql()
│  (Model-1)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Athena 실행    │ ← data_executor.run_query()
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────────┐
│Model-2 │ │   Model-3    │
│ Chart  │ │ Description  │
└───┬────┘ └──────┬───────┘
    │              │
    ▼              ▼
┌─────────────────────────┐
│   Streamlit UI          │
│ (차트 + 설명 + 테이블)  │
└─────────────────────────┘
```

## 파일 목록

### 설정 파일
| 파일 | 역할 |
|------|------|
| `config.yaml` | AWS 리전, Bedrock 모델 ID, Athena/S3/Glue 설정 |
| `requirements.txt` | Python 의존성 (boto3, streamlit, pandas, pyyaml, matplotlib) |

### 프롬프트 파일 (`prompts/`)
| 파일 | 역할 |
|------|------|
| `system_prompt.txt` | Model-1 Text2SQL 시스템 프롬프트 (CSV 스키마 포함) |
| `few_shot_examples.yaml` | 10개 few-shot 예시 (실제 컬럼 기반) |
| `chart_prompt.txt` | Model-2 차트 생성 프롬프트 (matplotlib 코드 생성) |
| `description_prompt.txt` | Model-3 한국어 설명 작성 프롬프트 |
| `intent_prompt.txt` | 의도 분류 프롬프트 (simple_analysis / mart_creation) |
| `mart_prompt.txt` | 데이터 마트 VIEW SQL 생성 프롬프트 |

### 소스 코드 (`src/`)
| 파일 | 역할 | 주요 함수 |
|------|------|-----------|
| `query_parser.py` | 프롬프트 조립 | `build_prompt()`, `build_chart_prompt()`, `build_description_prompt()` |
| `bedrock_client.py` | Bedrock 3-모델 호출 | `ask_text2sql()`, `ask_chart_generation()`, `ask_description()` |
| `data_executor.py` | Athena SQL 실행 | `run_query()`, `run_ddl()`, `validate_select_only()` |
| `visualizer.py` | 차트+설명 래퍼 | `generate_chart()`, `generate_description()` |
| `mart_agent.py` | 동적 마트 에이전트 | `classify_intent()`, `create_mart_view()`, `run_mart_pipeline()` |
| `app.py` | Streamlit UI + 파이프라인 통합 | `main()`, `_run_simple_analysis()`, `_run_mart_creation()` |

## 모듈별 상세

### query_parser.py
- YAML에서 few-shot 예시 로드
- 시스템 프롬프트 + few-shot + 사용자 질문을 결합하여 최종 프롬프트 생성
- Model-2/3용 프롬프트도 템플릿 치환 방식으로 조립

### bedrock_client.py
- Anthropic / Qwen 모델 형식 자동 분기
- `_invoke_model()`: 공통 호출 함수 (temperature=0.0)
- `_extract_python_code()`: LLM 응답에서 코드 블록 추출
- `_execute_chart_code()`: matplotlib 코드를 exec()로 실행하여 PNG 생성

### data_executor.py
- SELECT 전용 검증 (`validate_select_only`)
- DDL 검증 (`validate_view_ddl`) — CREATE OR REPLACE VIEW만 허용
- Athena 비동기 폴링 (최대 60초)
- 결과를 pandas DataFrame으로 변환 (숫자 컬럼 자동 캐스팅)

### visualizer.py
- `generate_chart()`: DataFrame → CSV → Model-2 호출 → PNG bytes
- `generate_description()`: DataFrame → CSV → Model-3 호출 → 한국어 텍스트

### mart_agent.py
- 의도 분류: simple_analysis vs mart_creation
- VIEW SQL 생성 + Athena DDL 실행
- 마트 기반 분석 프롬프트 조립
- `run_mart_pipeline()`: 전체 마트 생성 파이프라인 오케스트레이션

### app.py
- Streamlit 챗봇 UI (사이드바 예시 질문 포함)
- 대화 히스토리 관리 (`st.session_state`)
- 에러 처리: 각 단계 실패 시 graceful degradation
- 마트 생성 결과 표시 (VIEW SQL 확장 패널)

## Story Traceability

| Story | 구현 위치 |
|-------|-----------|
| US-1~US-9 (정상 분석 흐름) | query_parser + bedrock_client + data_executor + visualizer + app |
| US-10 (에러 처리) | app.py `_show_error()`, bedrock_client 예외 처리 |
| US-11 (Athena 에러) | data_executor `validate_select_only()`, app.py try/except |

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `AWS_DEFAULT_REGION` | us-east-1 | AWS 리전 |
| `BEDROCK_TEXT2SQL_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | Model-1 |
| `BEDROCK_CHART_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | Model-2 |
| `BEDROCK_DESCRIPTION_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | Model-3 |
| `BEDROCK_MAX_TOKENS` | 4096 | 최대 토큰 |
| `ATHENA_DATABASE` | aidlc_workshop | Athena DB |
| `ATHENA_WORKGROUP` | primary | Athena 워크그룹 |
| `ATHENA_OUTPUT_LOCATION` | s3://aidlc-workshop-athena-results-.../query-results/ | 결과 저장 |

## 실행 방법

```bash
cd ai-data-analyst
pip install -r requirements.txt
streamlit run src/app.py
```
