# Application Design (통합) — AI 데이터 분석가 챗봇

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit (app.py)                        │
│                   Pipeline Orchestrator                      │
└──────┬──────────────┬──────────────┬──────────────┬─────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│  query     │ │  bedrock   │ │   data     │ │ visualizer │
│  parser    │ │  client    │ │  executor  │ │            │
│            │ │            │ │            │ │            │
│ - prompt   │ │ - Model-1  │ │ - validate │ │ - chart    │
│   assembly │ │ - Model-2  │ │ - run SQL  │ │   (Model-2)│
│ - few-shot │ │ - Model-3  │ │ - Athena   │ │ - desc     │
│   loading  │ │            │ │            │ │   (Model-3)│
└────────────┘ └────────────┘ └────────────┘ └────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│  prompts/  │ │  Bedrock   │ │ Athena+S3  │ │  Bedrock   │
│  (files)   │ │  (AWS)     │ │ +Glue(AWS) │ │  (AWS)     │
└────────────┘ └────────────┘ └────────────┘ └────────────┘
```

---

## 컴포넌트 요약

| ID | 컴포넌트 | 파일 | 핵심 책임 |
|----|---------|------|----------|
| C1 | bedrock_client | src/bedrock_client.py | Bedrock 3개 모델 호출 |
| C2 | query_parser | src/query_parser.py | 프롬프트 조립 |
| C3 | data_executor | src/data_executor.py | Athena SQL 실행 |
| C4 | visualizer | src/visualizer.py | 차트 생성 + 설명 작성 |
| C5 | app | src/app.py | UI + 오케스트레이션 |

---

## 파이프라인 실행 순서

1. **사용자 입력** → app.py 수신
2. **프롬프트 조립** → query_parser.build_prompt()
3. **SQL 생성** → bedrock_client.ask_text2sql()
4. **SQL 검증** → data_executor.validate_select_only()
5. **SQL 실행** → data_executor.run_query()
6. **차트 생성** → visualizer.generate_chart() → bedrock_client.ask_chart_generation()
7. **설명 작성** → visualizer.generate_description() → bedrock_client.ask_description()
8. **결과 렌더링** → app.py (차트 이미지 + 설명 + 테이블)

---

## 설계 원칙

- **단일 책임**: 각 모듈은 하나의 역할만 담당
- **의존성 방향**: app → (query_parser, data_executor, visualizer) → bedrock_client
- **에러 격리**: 각 단계 실패가 전체 시스템을 중단시키지 않음 (graceful degradation)
- **상태 없음**: 요청 간 상태 공유 없음 (Streamlit session_state는 UI 렌더링용)
- **설정 외부화**: 모델 ID, 리전, S3 경로 등은 환경변수/config로 관리

---

## 상세 문서 참조
- [components.md](components.md) — 컴포넌트 정의 및 책임
- [component-methods.md](component-methods.md) — 메서드 시그니처
- [services.md](services.md) — 서비스 오케스트레이션
- [component-dependency.md](component-dependency.md) — 의존성 관계
