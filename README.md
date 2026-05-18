# 🤖 AI 데이터 분석가 챗봇
> AWS Summit Seoul 2026 · AI-DLC Challenge · 2026-05-20

---

## 📌 프로젝트 목적

비전문가가 자연어로 질문하면 AI가 SQL을 생성하고, 데이터 마트를 조회하여 **차트와 함께 답변**을 돌려주는 챗봇

```
자연어 질문 → Bedrock (Text2SQL) → DuckDB 실행 → Plotly 차트 → Streamlit 챗봇 응답
```

**예시 질문**
- "지난주 20대 여성의 구매 전환율 보여줘"
- "헤드폰 카테고리 주차별 매출 추이 보여줘"

---

## 🗂 Abstract Tasks

| # | Task | 설명 |
|---|------|------|
| T1 | 데이터 준비 | 전처리 CSV + DuckDB 데이터 마트 구축 |
| T2 | 프롬프트 설계 | Few-shot NL↔SQL 매핑셋 + 시스템 프롬프트 구성 |
| T3 | Text2SQL 모듈 | Bedrock 호출 → SQL + chart_type 반환 |
| T4 | SQL 실행 레이어 | DuckDB로 SQL 실행 → DataFrame 반환 |
| T5 | 차트 생성 모듈 | chart_type에 따라 Plotly 차트 생성 (bar/line/pie) |
| T6 | Streamlit 챗봇 UI | 입력창 + 텍스트·차트 통합 응답 화면 |

---

## 🏗 기술 스택

| 레이어 | 도구 |
|--------|------|
| AI | Amazon Bedrock (Claude) |
| 데이터 | DuckDB + fact_events.csv |
| UI | Streamlit (단일 파일 앱) |
| 차트 | Plotly Express |
| 개발 방법론 | AI-DLC (Kiro Steering Files) |

---

## 🔄 AI-DLC Workflows 매핑

AI-DLC는 **Inception → Construction → Operations** 3단계로 구성된 개발 방법론입니다.  
Kiro가 `.kiro/steering/` 의 rules 파일을 읽고 각 단계를 안내합니다.

```
AI-DLC 단계       우리 프로젝트
────────────────────────────────────────────────────
Inception         "Using AI-DLC, 챗봇 만들래"
(기획·설계)        → Kiro가 요구사항 질문
                  → 우리가 답변 (이미 결정된 내용)
                  → aidlc-docs/ 에 자동 산출물 생성
                    ├── requirements.md
                    ├── design.md
                    ├── aidlc-state.md
                    └── audit.md

Construction      T1 ~ T6 각각에 대해 Kiro가 코드 생성
(구현·테스트)      → 단계마다 팀원이 승인
                  → aidlc-docs/audit.md 에 전 과정 자동 기록

Operations        Streamlit 로컬 실행 = 완료
(배포)            (6시간 내에서는 간략히)
────────────────────────────────────────────────────
```

> **핵심**: `aidlc-docs/` 에 쌓이는 기록이 "AI-DLC 활용도"의 증거가 됩니다.

---

## 👥 팀 역할

| 역할 | 담당 Tasks |
|------|-----------|
| A — AI·백엔드 | T3 (Text2SQL), T4 (SQL 실행), Bedrock 연동 |
| B — 데이터 | T1 (데이터 마트), T2 (프롬프트·Few-shot) |
| C — 프론트 | T5 (차트), T6 (Streamlit UI) |

---

## 🌿 브랜치 전략

```
main          ← 동작 확인된 코드만 머지
 └─ base      ← 공통 초기 세팅 (데이터, 문서, Kiro rules)
     ├─ dev/A ← A 독립 구현
     ├─ dev/B ← B 독립 구현
     └─ dev/C ← C 독립 구현
```

**막혔을 때**
```bash
# 다른 사람 브랜치에서 파일 가져오기
git checkout dev/A -- src/bedrock_client.py

# 다른 사람 브랜치 기반으로 재출발
git checkout -b dev/C-from-A origin/dev/A
```

---

## 🎬 당일 시뮬레이션

### 빌드 시작 직후

```
A  → Kiro Inception 진행 (20-30분)
B  → fact_events.csv 로드 확인, DuckDB 마트 실행 검증
C  → streamlit run app.py 기본 동작 확인
```

### A가 Inception 완료 후

```bash
git add aidlc-docs/
git commit -m "feat: AI-DLC inception artifacts"
git push origin base
```

```
B, C → git pull origin base
      → git checkout -b dev/B (또는 dev/C)
      → 각자 Kiro와 Construction 시작
```

### Construction 병렬 진행

**A의 Kiro 대화 예시**
```
"Using AI-DLC, implement bedrock_client.py.
 It should call Claude via boto3, parse the response as JSON
 containing sql and chart_type fields.
 Include MOCK_MODE fallback when Bedrock is unavailable."
→ Kiro: 코드 생성 → A 승인 → audit.md 자동 기록
```

**B의 Kiro 대화 예시**
```
"Using AI-DLC, create system_prompt.txt and few_shot_examples.yaml.
 Schema: [data_schema.md 내용]
 Few-shot 10쌍 포함. 자연어→SQL 변환 정확도 최우선."
→ Kiro: 생성 → B 승인 → 테스트 스크립트도 생성 요청
```

**C의 Kiro 대화 예시**
```
"Using AI-DLC, build app.py as a Streamlit chatbot.
 st.chat_message must display text + plotly chart + dataframe.
 visualizer.py handles bar/line/pie based on chart_type."
→ Kiro: 생성 → C 승인 → streamlit run 으로 확인
```

### 통합

```
# 가장 진행이 빠른 브랜치(A)에 나머지 머지
git checkout dev/A
git merge dev/B
git merge dev/C

# E2E 데모 쿼리 검증
"지난주 20대 여성의 구매 전환율 보여줘"  → ✅
"헤드폰 카테고리 주차별 매출 보여줘"     → ✅
```

### 마무리

```
C: 화면 녹화 (라이브 데모 실패 대비 백업 필수)
A: git push → main 머지
B: aidlc-docs/audit.md 확인 → 제출물 일부로 포함
전원: 제출
```

---

## ⚠️ 리스크 방지

| 리스크 | 대응 |
|--------|------|
| Bedrock 권한 없음 | MOCK_MODE 플래그로 즉시 전환 |
| 브랜치 충돌 | 파일 단위 책임 분리 (A=bedrock, B=prompts, C=app) |
| 라이브 데모 실패 | 동작 영상 반드시 사전 녹화 |
| 복잡도 과욕 | FastAPI·AgentCore·QuickSight는 OUT OF SCOPE |

---

## 📋 사전 준비 체크리스트 (5월 19일까지)

- [ ] `fact_events.csv` 전처리 완료
- [ ] DuckDB 데이터 마트 구축 및 검증
- [ ] Few-shot NL↔SQL 매핑 10~20쌍 작성
- [ ] GitHub 레포 생성 + 초기 구조 push
- [ ] [aidlc-workflows](https://github.com/awslabs/aidlc-workflows) clone → `.kiro/steering/` 세팅
- [ ] git, python, uv, aws cli v2, Node.js 설치 확인
- [ ] 5/19 저녁 이메일 확인 (Workshop Studio 링크 + Kiro 임시 계정)

---

## 🔗 참고 링크

- [AI-DLC Workflows (awslabs)](https://github.com/awslabs/aidlc-workflows)
- [Kiro IDE 공식](https://kiro.dev)
- [Amazon Bedrock 콘솔](https://console.aws.amazon.com/bedrock)

---

*AWS Summit Seoul 2026 AI-DLC Challenge | Team 3*
