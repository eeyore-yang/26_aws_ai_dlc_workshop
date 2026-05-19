# 🤖 AI 데이터 분석가 챗봇
> AWS Summit Seoul 2026 · AI-DLC Challenge · 2026-05-20

---

## 📌 프로젝트 목적

비전문가가 자연어로 질문하면 AI가 SQL을 생성하고, 데이터 마트를 조회하여 **차트와 함께 답변**을 돌려주는 챗봇

```
자연어 질문 → Bedrock (Text2SQL) → DuckDB 실행 → Plotly 차트 → Streamlit 챗봇 응답
```

---

## 🗂 공통 초기 정렬 (GitHub + 프로젝트 기준선)

초기에 팀이 함께 아래 항목을 **한 번만 확정**합니다.

1. 프로젝트 목적/범위 (In/Out Scope)
2. Task 개수와 우선순위/순서
3. 기반 데이터셋 (`fact_events.csv`)과 스키마
4. 공통 산출물 구조 (`aidlc-docs/`, `src/`, `app.py`)
5. 브랜치 네이밍 규칙과 병합 규칙

> 핵심: 시작점은 같이 맞추고, 구현은 각자 독립적으로 빠르게 실험합니다.

---

## 🧩 작업 단위 (공통 목표)

| # | Task | 설명 |
|---|------|------|
| T1 | 데이터 준비 | 전처리 CSV + DuckDB 데이터 마트 구축 |
| T2 | 프롬프트 설계 | Few-shot NL↔SQL 매핑셋 + 시스템 프롬프트 구성 |
| T3 | Text2SQL 모듈 | Bedrock 호출 → SQL + chart_type 반환 |
| T4 | SQL 실행 레이어 | DuckDB SQL 실행 → DataFrame 반환 |
| T5 | 차트 생성 모듈 | chart_type별 Plotly 시각화 |
| T6 | Streamlit 챗봇 UI | 텍스트·차트·테이블 통합 응답 |

---

## 🚀 협업 방식 변경: 3인 1팀 역할분담 → 1인 1팀 병렬 개발

기존 방식에서는 역할 경계에서 충돌이 발생하거나, 특정 인원만 Kiro Pro+ 경험이 깊어질 위험이 있었습니다.
그래서 다음 방식으로 전환합니다.

- **기존**: A/B/C 역할을 고정 분담해서 한 기능씩 나눔
- **변경**: 각자 동일 목표를 가진 **독립 실행 브랜치**에서 end-to-end로 진행

### 왜 이 방식인가?

- 병목 구간(특정 담당자 대기)이 줄어듦
- 각자 전체 파이프라인 경험 축적 가능
- 한 브랜치가 막히면, 다른 브랜치 성과를 즉시 흡수 가능
- 충돌은 “역할 경계”가 아니라 “검증된 결과물” 중심으로 해결 가능

---

## 🌿 브랜치 전략 (1인 1팀 병렬)

```
main
 └─ init/baseline                # 공통 기준선(목표/태스크/데이터셋 확정)
     ├─ solo/A-e2e               # A의 독립 구현 브랜치
     ├─ solo/B-e2e               # B의 독립 구현 브랜치
     └─ solo/C-e2e               # C의 독립 구현 브랜치
```

### 브랜치 네이밍 규칙

- 개인 실험: `solo/<name>-<focus>`
- 다른 브랜치 성과 흡수 후 재시작: `solo/<name>-from-<source>`
- 빠른 핫픽스: `hotfix/<topic>`

예시:
- `solo/A-e2e`
- `solo/B-prompt-first`
- `solo/C-from-A`

---

## 🔁 막혔을 때 운영 규칙 (핵심)

### 1) 다른 브랜치의 특정 파일만 가져오기

```bash
git checkout solo/A-e2e -- src/bedrock_client.py
```

### 2) 잘 진행되는 브랜치를 기반으로 새로 분기

```bash
git checkout solo/A-e2e
git checkout -b solo/C-from-A
```

### 3) Cherry-pick으로 커밋 단위 흡수

```bash
git checkout solo/B-e2e
git cherry-pick <A의_유효_커밋_SHA>
```

---

## 🧭 실행 시나리오

### Step 0. 공통 합의 (짧고 명확하게)

- GitHub 이슈/프로젝트 보드에 목표와 Task(T1~T6) 등록
- 데이터셋/스키마 확정
- 평가 기준 확정 (정확도, 응답속도, 데모 안정성)

### Step 1. 기준선 브랜치 생성

```bash
git checkout main
git checkout -b init/baseline
```

- README, 데이터 경로, 기본 폴더 구조, `.kiro/steering` 기준만 반영
- 이후 각자 분기

### Step 2. 각자 1인 1팀 병렬 진행

```bash
git checkout -b solo/A-e2e
git checkout -b solo/B-e2e
git checkout -b solo/C-e2e
```

- 모두 동일한 최종 목표(질문→SQL→실행→차트→챗봇 응답)를 독립적으로 달성 시도
- 중간 산출물은 자주 push하고 커밋 메시지를 작게 유지

### Step 3. 교차 활용

- 누구든 블로커 발생 시, 가장 앞선 브랜치의 파일/커밋을 흡수
- 필요하면 흡수 브랜치 기반으로 새 브랜치 재시작

### Step 4. 최종 통합

- 데모 기준 충족 브랜치를 기준 브랜치로 선정
- 나머지 브랜치에서 필요한 커밋만 선택 병합
- `main`에는 검증 완료본만 머지

---

## ✅ 운영 원칙

1. **문제 공유는 빠르게, 구현은 독립적으로**
2. **충돌 최소화보다 실험 속도 우선**
3. **좋은 결과를 표준으로 채택** (사람 기준이 아니라 결과 기준)
4. **모든 브랜치는 E2E 데모 가능 상태를 목표**

---

## 📋 체크리스트

- [ ] 공통 목표/Task/데이터셋 합의 완료
- [ ] `init/baseline` 생성 및 공유
- [ ] 개인별 `solo/*` 브랜치 생성
- [ ] 블로커 대응 규칙(`checkout -- file`, `cherry-pick`) 팀 내 합의
- [ ] 최종 통합 기준(정확도/안정성/시연성) 합의

---

*AWS Summit Seoul 2026 AI-DLC Challenge | Team 3*
