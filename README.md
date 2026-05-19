# AI 데이터 분석가 챗봇

> AWS Summit Seoul 2026 · AI-DLC Challenge · 2026-05-20 (6h build)

자연어 질문 → Bedrock Claude (Text2SQL) → DuckDB → Plotly 차트 → Streamlit 챗봇 응답

---

## 개발환경 사전 요구사항

| 도구 | 용도 | 설치 |
|------|------|------|
| Python 3.11+ | 앱 실행 | - |
| uv (uvx) | Kiro MCP 서버 자동 실행 | `pip install uv` 또는 [설치 가이드](https://docs.astral.sh/uv/getting-started/installation/) |
| Node.js 18+ (npx) | Excalidraw MCP 서버 | [nodejs.org](https://nodejs.org/) |
| Kiro IDE | AI 개발환경 + MCP 연동 | [kiro.dev](https://kiro.dev) |

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

### 2. 의존성 설치 및 앱 실행

```bash
cd ai-data-analyst
pip install -r requirements.txt

# 로컬 테스트 (Bedrock 없이)
MOCK_MODE=true streamlit run src/app.py

# 실제 실행
AWS_REGION=ap-northeast-2 \
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0 \
streamlit run src/app.py
```

### 3. 데이터 마트 초기화

```bash
# data/fact_events.csv 배치 후
python src/data_executor.py
```

---

## 아키텍처

```
[Streamlit UI]
     │  자연어 질문
     ▼
[bedrock_client.py]  ← system_prompt.txt + few_shot_examples.yaml
     │  {sql, chart_type, summary}
     ▼
[data_executor.py]   ← DuckDB (fact_events 마트)
     │  pd.DataFrame
     ▼
[visualizer.py]      ← Plotly Figure (bar / line / pie)
     ▼
[Streamlit UI]       ← 텍스트 요약 + 차트 + 테이블
```

---

## 데이터 스키마 (fact_events)

| 컬럼 | 타입 | 값 예시 |
|------|------|---------|
| customer_id | str | C0001 |
| age_group | str | 10s / 20s / 30s / 40s / 50s / 60s+ |
| gender | str | male / female / non-binary |
| event_date | date | 2023-09-01 |
| week_label | str | 2023-W35 |
| event_type | str | visit / purchase |
| product_category | str | Headphones / Earbuds / Portable_Speaker / Soundbar / Home_Audio / Wireless_Speaker |
| sku | str | SKU-001 |
| loyalty_member | str | yes / no |
| amount | float | purchase만 유효, visit은 0.0 |

---

## 작업 단위 및 역할 분담

| Task | 설명 | 담당 브랜치 |
|------|------|------------|
| T1 | fact_events.csv 전처리 + DuckDB 마트 구축 | dev/B |
| T2 | Few-shot NL↔SQL 매핑 + 시스템 프롬프트 | dev/B |
| T3 | Text2SQL 모듈 — Bedrock 호출 → JSON | dev/A |
| T4 | SQL 실행 레이어 — DuckDB → DataFrame | dev/A |
| T5 | 차트 생성 모듈 — chart_type 기반 Plotly | dev/C |
| T6 | Streamlit 챗봇 UI — 통합 응답 | dev/C |

---

## 브랜치 전략

```
main                 ← 데모 합격 확인본만 머지
 └─ base/setup       ← 공통 초기 세팅 (지금 이 브랜치)
     ├─ dev/A        ← AI·백엔드 (T3, T4)
     ├─ dev/B        ← 데이터·프롬프트 (T1, T2)
     └─ dev/C        ← 프론트·차트 (T5, T6)
```

```bash
# 각자 실행
git checkout base/setup && git pull origin base/setup
git checkout -b dev/A   # 또는 dev/B, dev/C
```

---

## AI-DLC 운영 순서

```
[T=0]    base/setup pull → Kiro 열기 → Inception 시작 (20-30분)
          └─ aidlc-docs/: spec.md, data-model.md, audit.md 생성
          └─ base/setup push → 팀원 pull

[T+30m]  dev/A, B, C 분기 → 각자 Construction 시작

[T-1h]   블로커 발생 시 아래 규칙 적용

[T=6h]   최선 브랜치 → main 머지 → 데모
          └─ aidlc-docs/audit.md → 제출 증거
```

---

## 막혔을 때 협업 규칙

```bash
# 다른 브랜치 파일만 가져오기
git checkout dev/A -- src/bedrock_client.py

# 앞선 브랜치 기반으로 재분기
git checkout dev/A && git checkout -b dev/C-from-A

# 커밋 단위 흡수
git cherry-pick <커밋 SHA>
```

---

## 완성 기준 (데모 합격선)

- [ ] "지난달 카테고리별 매출은?" → bar 차트 + 수치 테이블
- [ ] "30대 여성 전환율 추이를 보여줘" → line 차트 + 요약
- [ ] MOCK_MODE=true 로 Bedrock 없이 동일 UI 흐름 동작

---

*AWS Summit Seoul 2026 AI-DLC Challenge | Team 3*
