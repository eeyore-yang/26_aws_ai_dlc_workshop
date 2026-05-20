# Build Instructions — AI 데이터 분석가 챗봇

## 사전 요구사항

| 도구 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 앱 실행 |
| pip | 최신 | 의존성 설치 |
| AWS Credentials | Workshop Studio 제공 | Bedrock + Athena + S3 접근 |

## 1. 의존성 설치

```bash
cd ai-data-analyst
pip install -r requirements.txt
```

필수 패키지: `boto3`, `streamlit`, `pandas`, `pyyaml`, `matplotlib`

## 2. AWS Credentials 설정

Workshop Studio에서 제공받은 credentials를 환경변수로 설정:

```bash
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

## 3. 인프라 셋업 (최초 1회)

```bash
python setup_infra.py
```

이 스크립트가 수행하는 작업:
- S3 버킷 생성 (data + athena-results)
- fact_events.csv S3 업로드
- Glue Database + Table 생성 (OpenCSVSerde, 모든 컬럼 STRING)
- 테스트 쿼리 실행 확인

## 4. 앱 실행

```bash
streamlit run src/app.py --server.headless true
```

접속: http://localhost:8501

## 5. 환경 변수 (선택)

| 변수 | 기본값 | 설명 |
|------|--------|------|
| AWS_DEFAULT_REGION | us-east-1 | AWS 리전 |
| BEDROCK_TEXT2SQL_MODEL_ID | us.anthropic.claude-sonnet-4-20250514-v1:0 | Model-1 |
| BEDROCK_CHART_MODEL_ID | qwen.qwen3-coder-next | Model-2 (차트 코드 생성) |
| BEDROCK_DESCRIPTION_MODEL_ID | us.anthropic.claude-sonnet-4-20250514-v1:0 | Model-3 |
| ATHENA_DATABASE | aidlc_workshop | Athena DB |
| ATHENA_OUTPUT_LOCATION | s3://aidlc-workshop-athena-results-{account}/query-results/ | 쿼리 결과 저장 |
