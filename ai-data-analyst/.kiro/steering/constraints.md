# 프로젝트 제약 (IN / OUT SCOPE)

## IN SCOPE
- Amazon Bedrock Claude 단일 AI 호출 (Text2SQL + chart_type + summary JSON 반환)
- DuckDB 로컬 인메모리 실행 (fact_events.csv 기반 사전 정적 마트)
- Streamlit 단일 파일 챗봇 UI (app.py)
- Plotly Express 차트 3종: bar / line / pie
- MOCK_MODE 플래그: Bedrock 연결 실패 시 자동 전환
- aidlc-docs/ 폴더: Inception 산출물 + audit.md 포함

## OUT OF SCOPE
- FastAPI, REST API 계층
- Amazon AgentCore / QuickSight
- 실시간 데이터 수집 / 동적 마트 생성
- 사용자 인증/세션 관리
- 다중 AI 모델 or 멀티 에이전트 구조
- Docker / 컨테이너 배포
- 외부 DB 연결 (RDS, Redshift 등)

## 코드 규칙
- Python 3.11+
- 모든 Bedrock 호출은 bedrock_client.py 에만
- DuckDB 연결/쿼리는 data_executor.py 에만
- 차트 생성은 visualizer.py 에만
- app.py 는 UI 레이어만 (비즈니스 로직 없음)

## 환경 변수
AWS_REGION=ap-northeast-2
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
MOCK_MODE=false
