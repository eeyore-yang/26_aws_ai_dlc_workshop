# AI 데이터 분석가 챗봇

> AWS Summit Seoul 2026 · AI-DLC Challenge · 2026-05-20 (6h build)

자연어 질문 → Bedrock Claude (Text2SQL) → Amazon Athena → LLM 차트 코드 생성 (matplotlib) → LLM 설명 생성 → Streamlit 챗봇 응답

---

## 개발환경 사전 요구사항

| 도구 | 용도 | 설치 |
|------|------|------|
| Python 3.11+ | 앱 실행 | - |
| uv (uvx) | Kiro MCP 서버 자동 실행 | `pip install uv` 또는 [설치 가이드](https://docs.astral.sh/uv/getting-started/installation/) |
| Node.js 18+ (npx) | Excalidraw MCP 서버 | [nodejs.org](https://nodejs.org/) |
| Kiro IDE | AI 개발환경 + MCP 연동 | [kiro.dev](https://kiro.dev) |
| AWS CLI | 인프라 셋업 | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |

> `.kiro/settings/mcp.json`에 팀 공용 MCP 서버 설정이 포함되어 있습니다.
> Kiro로 프로젝트를 열면 aws-docs, aws-knowledge, excalidraw 서버가 자동 연결됩니다.

---

## Quick Start

### 1. aws-aidlc-rules 설치 (첫 클론 후 1회)

```bash
git clone --depth 1 --branch v0.1.8 \
  https://github.com/awslabs/aidlc-workflows.git /tmp/aidlc-workflows

mkdir -p ai-data-analyst/.kiro/steering
cp -R /tmp/aidlc-workflows/aidlc-rules/aws-aidlc-rules/. \
  ai-data-analyst/.kiro/steering/aws-aidlc-rules/
cp -R /tmp/aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/. \
  ai-data-analyst/.kiro/aws-aidlc-rule-details/
```

> base/setup 브랜치에는 이미 설치됨 — pull 후 바로 사용 가능.

### 2. 의존성 설치

```bash
cd ai-data-analyst
pip install -r requirements.txt
```

### 3. AWS 인프라 셋업 (S3 + Glue + Athena)

```bash
# AWS credentials 설정
export AWS_DEFAULT_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

# 방법 A: 셸 스크립트
source setup_aws.sh

# 방법 B: Python 스크립트
python setup_infra.py
```

이 스크립트는 다음을 수행합니다:
1. S3 버킷 생성 (데이터 + Athena 결과)
2. `data/fact_events.csv` 업로드
3. Glue Database/Table 생성
4. 테스트 쿼리 실행

### 4. 앱 실행

```bash
# 환경변수 설정
export AWS_DEFAULT_REGION=us-east-1
export BEDROCK_TEXT2SQL_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
export BEDROCK_CHART_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
export BEDROCK_DESCRIPTION_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

streamlit run src/app.py
```

---

## 아키텍처 (3-모델 파이프라인)

```
[Streamlit UI]
     │  자연어 질문
     ▼
[query_parser.py]    ← system_prompt.txt + few_shot_examples.yaml
     │  프롬프트 조립
     ▼
[bedrock_client.py]  ← Model-1: Text2SQL (Claude Sonnet 4)
     │  {"sql": "SELECT ..."}
     ▼
[data_executor.py]   ← Amazon Athena (fact_events 테이블)
     │  pd.DataFrame
     ▼
[visualizer.py]
     ├─ [bedrock_client.py] ← Model-2: Chart Generation (matplotlib 코드 생성)
     │       │  PNG 이미지 bytes
     │       ▼
     └─ [bedrock_client.py] ← Model-3: Description (한국어 설명 작성)
              │  한국어 요약 텍스트
              ▼
[Streamlit UI]       ← 텍스트 요약 + 차트 이미지 + 데이터 테이블
```

### 모델 역할

| 모델 | 역할 | 기본 모델 ID |
|------|------|-------------|
| Model-1 | 자연어 → SQL 변환 | `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| Model-2 | 데이터 → matplotlib 차트 코드 생성 | `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| Model-3 | 데이터 → 한국어 설명 작성 | `us.anthropic.claude-sonnet-4-20250514-v1:0` |

---

## 데이터 스키마 (fact_events)

| 컬럼 | 타입 | 값 예시 |
|------|------|---------|
| Customer ID | BIGINT | 1000 |
| Age | INT | 53 |
| Gender | VARCHAR | Male / Female |
| Loyalty Member | VARCHAR | Yes / No |
| Product Type | VARCHAR | Smartphone / Laptop / Tablet |
| SKU | VARCHAR | SKU1004 |
| Rating | INT | 1~5 |
| Order Status | VARCHAR | Completed / Cancelled |
| Payment Method | VARCHAR | Cash / Credit Card / Paypal |
| Total Price | DOUBLE | 5538.33 |
| Unit Price | DOUBLE | 791.19 |
| Quantity | INT | 7 |
| Purchase Date | DATE | 2024-03-20 |
| Shipping Type | VARCHAR | Standard / Overnight / Express |
| Add-ons Purchased | VARCHAR | Accessory / Extended Warranty / Impulse Item (쉼표 구분) |
| Add-on Total | DOUBLE | 40.21 |

> 주의: Athena에서 OpenCSVSerde 사용 시 모든 컬럼이 STRING으로 저장됨.
> SQL에서 숫자 연산 시 반드시 `CAST()` 사용 필요.

---

## 프로젝트 구조

```
ai-data-analyst/
├── src/
│   ├── app.py              # Streamlit 챗봇 UI (진입점)
│   ├── bedrock_client.py   # Bedrock 3-모델 호출 (Text2SQL, Chart, Description)
│   ├── data_executor.py    # Athena SQL 실행 레이어
│   ├── query_parser.py     # 프롬프트 조립 (system + few-shot + user)
│   └── visualizer.py       # 차트 생성 + 설명 생성 래퍼
├── prompts/
│   ├── system_prompt.txt       # Text2SQL 시스템 프롬프트
│   ├── few_shot_examples.yaml  # NL↔SQL 매핑 예시
│   ├── chart_prompt.txt        # 차트 코드 생성 프롬프트
│   └── description_prompt.txt  # 한국어 설명 생성 프롬프트
├── data/
│   └── fact_events.csv     # 원본 데이터
├── config.yaml             # AWS/Bedrock/Athena 설정
├── setup_infra.py          # AWS 인프라 셋업 (Python)
├── setup_aws.sh            # AWS 인프라 셋업 (Shell)
└── requirements.txt        # Python 의존성
```

---

## 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `AWS_DEFAULT_REGION` | `us-east-1` | AWS 리전 |
| `BEDROCK_TEXT2SQL_MODEL_ID` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Text2SQL 모델 |
| `BEDROCK_CHART_MODEL_ID` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | 차트 생성 모델 |
| `BEDROCK_DESCRIPTION_MODEL_ID` | `us.anthropic.claude-sonnet-4-20250514-v1:0` | 설명 생성 모델 |
| `BEDROCK_MAX_TOKENS` | `4096` | 최대 토큰 수 |
| `ATHENA_DATABASE` | `aidlc_workshop` | Athena 데이터베이스 |
| `ATHENA_WORKGROUP` | `primary` | Athena 워크그룹 |
| `ATHENA_OUTPUT_LOCATION` | `s3://aidlc-workshop-athena-results-{ACCOUNT_ID}/query-results/` | 쿼리 결과 저장 위치 |

---

---

## 완성 기준 (데모 합격선)

- [ ] "제품 유형별 총 매출을 보여줘" → bar 차트 + 수치 테이블
- [ ] "월별 매출 추이를 보여줘" → line 차트 + 한국어 요약
- [ ] "연령대별 평균 구매 금액은?" → 차트 + 데이터 테이블
- [ ] Athena 쿼리 실행 → DataFrame → 차트 이미지 → 설명 전체 파이프라인 동작

---

*AWS Summit Seoul 2026 AI-DLC Challenge*
