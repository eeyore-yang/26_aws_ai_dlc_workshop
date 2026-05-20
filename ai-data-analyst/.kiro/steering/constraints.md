# 프로젝트 제약 (IN / OUT SCOPE)

## IN SCOPE
- Amazon Bedrock 2개 모델 호출:
  - Model-1: Text2SQL + summary JSON 반환 (자연어 처리)
  - Model-2: 데이터 기반 차트 이미지 직접 생성 (차트 생성)
- Athena + S3 + Glue Catalog (데이터 레이어)
- Streamlit 단일 파일 챗봇 UI (app.py)
- LLM 생성 차트 이미지 표시 (Plotly 미사용)
- aidlc-docs/ 폴더: Inception 산출물 + audit.md 포함

## OUT OF SCOPE
- FastAPI, REST API 계층
- Amazon AgentCore / QuickSight
- 실시간 데이터 수집 / 동적 마트 생성
- 사용자 인증/세션 관리
- 멀티 에이전트 구조 (2개 모델은 허용, 에이전트 오케스트레이션은 불가)
- Docker / 컨테이너 배포
- 로컬 데이터베이스 (DuckDB, SQLite 등)
- 외부 DB 연결 (RDS, Redshift 등)
- Plotly / Matplotlib 등 로컬 차트 라이브러리

## 코드 규칙
- Python 3.11+
- 모든 Bedrock 호출은 bedrock_client.py 에만 (Model-1, Model-2 모두)
- Athena 쿼리 실행은 data_executor.py 에만
- 차트 생성(LLM 호출 + 이미지 처리)은 visualizer.py 에만
- app.py 는 UI 레이어만 (비즈니스 로직 없음)

## Data Layer Constraints
- SQL 실행 엔진은 Athena로 고정한다
- 데이터 파일은 S3에 저장한다
- 테이블 스키마는 Glue Catalog로 관리한다
- 로컬 데이터베이스(DuckDB, SQLite 등)는 사용하지 않는다

## 환경 변수
AWS_REGION=ap-northeast-2
BEDROCK_TEXT2SQL_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_CHART_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
EXECUTOR_MODE=athena
