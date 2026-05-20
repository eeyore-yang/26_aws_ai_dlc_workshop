# Component Dependencies — AI 데이터 분석가 챗봇

## 의존성 매트릭스

| 컴포넌트 | 의존 대상 | 의존 유형 |
|---------|----------|----------|
| app.py | query_parser, bedrock_client, data_executor, visualizer | 직접 import |
| query_parser | prompts/*.txt, prompts/*.yaml | 파일 읽기 |
| bedrock_client | boto3 (Bedrock Runtime) | AWS SDK |
| data_executor | boto3 (Athena), pandas | AWS SDK + 라이브러리 |
| visualizer | bedrock_client | 내부 호출 (Model-2, Model-3) |

## 데이터 흐름도

```
┌──────────┐     prompt      ┌───────────────┐
│  query   │────────────────→│               │
│  parser  │                 │   bedrock     │
└──────────┘                 │   client      │
                             │               │
┌──────────┐     sql         │  Model-1      │
│   app    │←────────────────│  (Text2SQL)   │
│  (UI)    │                 └───────────────┘
│          │
│          │     sql         ┌───────────────┐
│          │────────────────→│   data        │
│          │     DataFrame   │   executor    │
│          │←────────────────│  (Athena)     │
│          │                 └───────────────┘
│          │
│          │  question + df  ┌───────────────┐
│          │────────────────→│  visualizer   │
│          │  chart + desc   │  (Model-2/3)  │
│          │←────────────────│               │
└──────────┘                 └───────────────┘
```

## 컴포넌트 간 통신 패턴

- **동기 함수 호출**: 모든 컴포넌트 간 통신은 동기 Python 함수 호출
- **데이터 전달**: 함수 인자/반환값으로 전달 (메시지 큐 없음)
- **상태 없음**: 각 요청은 독립적 (세션 상태는 Streamlit session_state에만)

## 외부 의존성 (pip packages)

| 패키지 | 용도 | 사용 컴포넌트 |
|--------|------|-------------|
| boto3 | AWS SDK (Bedrock, Athena, S3) | bedrock_client, data_executor |
| streamlit | 웹 UI 프레임워크 | app |
| pandas | DataFrame 처리 | data_executor, visualizer |
| pyyaml | YAML 파싱 | query_parser |
