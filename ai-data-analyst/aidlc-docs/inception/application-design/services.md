# Services — AI 데이터 분석가 챗봇

## 서비스 아키텍처 개요

이 프로젝트는 별도의 서비스 레이어 없이 **app.py가 직접 오케스트레이션**하는 단순 구조입니다.
Streamlit 앱이 파이프라인 컨트롤러 역할을 수행합니다.

---

## S1: Pipeline Orchestrator (app.py 내장)

### 역할
- 사용자 입력을 받아 3-모델 파이프라인을 순차 실행
- 각 단계의 결과를 다음 단계에 전달
- 에러 발생 시 graceful degradation 처리

### 오케스트레이션 흐름

```
┌─────────────────────────────────────────────────────────┐
│  app.py (_run_pipeline)                                 │
│                                                         │
│  1. query_parser.build_prompt(question)                 │
│     └─→ prompt                                          │
│                                                         │
│  2. bedrock_client.ask_text2sql(question, prompt)       │
│     └─→ {"sql": "..."}                                 │
│                                                         │
│  3. data_executor.validate_select_only(sql)             │
│     data_executor.run_query(sql)                        │
│     └─→ DataFrame                                      │
│                                                         │
│  4. visualizer.generate_chart(question, df)             │
│     └─→ chart_image (bytes | None)                     │
│                                                         │
│  5. visualizer.generate_description(question, df, img)  │
│     └─→ description (str)                              │
│                                                         │
│  6. Render: description + chart_image + dataframe       │
└─────────────────────────────────────────────────────────┘
```

### 에러 처리 전략

| 실패 지점 | 대응 |
|-----------|------|
| Model-1 (Text2SQL) 실패 | 에러 메시지 표시, 파이프라인 중단 |
| SQL 검증 실패 (non-SELECT) | "위험한 쿼리가 감지되었습니다" 메시지 |
| Athena 실행 실패 | "쿼리 실행에 실패했습니다" 메시지 |
| Model-2 (차트) 실패 | 차트 없이 설명 + 테이블만 표시 |
| Model-3 (설명) 실패 | 차트 + 테이블만 표시 (설명 없이) |

---

## 외부 서비스 의존성

| 외부 서비스 | 용도 | 호출 컴포넌트 |
|------------|------|-------------|
| Amazon Bedrock | LLM 호출 (3개 모델) | bedrock_client |
| Amazon Athena | SQL 실행 | data_executor |
| Amazon S3 | 데이터 저장 + Athena 결과 | data_executor |
| AWS Glue Catalog | 테이블 스키마 | data_executor (간접) |
