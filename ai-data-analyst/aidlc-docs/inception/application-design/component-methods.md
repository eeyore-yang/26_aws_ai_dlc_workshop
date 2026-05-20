# Component Methods — AI 데이터 분석가 챗봇

## C1: bedrock_client

### `ask_text2sql(question: str, prompt: str) -> dict`
- **목적**: Model-1 호출 — 자연어를 SQL로 변환
- **입력**: 사용자 질문, 조립된 프롬프트 (시스템 + few-shot + 질문)
- **출력**: `{"sql": "SELECT ..."}`
- **에러**: Bedrock 호출 실패 시 예외 발생

### `ask_chart_generation(question: str, data_text: str) -> bytes`
- **목적**: Model-2 호출 — 데이터 기반 차트 이미지 생성
- **입력**: 원본 질문, DataFrame을 텍스트로 변환한 데이터
- **출력**: 차트 이미지 (bytes, PNG)
- **에러**: 생성 실패 시 None 반환

### `ask_description(question: str, data_text: str, chart_image: bytes) -> str`
- **목적**: Model-3 호출 — 데이터 + 차트 취합하여 한국어 설명 작성
- **입력**: 원본 질문, 데이터 텍스트, 차트 이미지
- **출력**: 한국어 설명 문자열
- **에러**: 생성 실패 시 기본 메시지 반환

---

## C2: query_parser

### `load_few_shot_examples() -> list[dict]`
- **목적**: YAML 파일에서 few-shot 예시 로드
- **입력**: 없음 (파일 경로 고정)
- **출력**: 예시 리스트 `[{"question": ..., "output": ...}, ...]`

### `build_prompt(question: str) -> str`
- **목적**: Model-1용 최종 프롬프트 조립
- **입력**: 사용자 질문
- **출력**: 시스템 프롬프트 + few-shot 예시 + 사용자 질문이 결합된 문자열

---

## C3: data_executor

### `validate_select_only(sql: str) -> None`
- **목적**: SQL이 SELECT 문인지 검증
- **입력**: SQL 문자열
- **출력**: 없음 (통과) 또는 ValueError 발생

### `run_query(sql: str) -> pd.DataFrame`
- **목적**: Athena에서 SQL 실행 후 결과 반환
- **입력**: SELECT SQL 문자열
- **출력**: pandas DataFrame
- **에러**: Athena 실행 실패 시 예외 발생

---

## C4: visualizer

### `generate_chart(question: str, df: pd.DataFrame) -> bytes | None`
- **목적**: Model-2를 통해 차트 이미지 생성
- **입력**: 원본 질문, Athena 결과 DataFrame
- **출력**: PNG 이미지 bytes 또는 None (실패 시)

### `generate_description(question: str, df: pd.DataFrame, chart_image: bytes | None) -> str`
- **목적**: Model-3를 통해 한국어 설명 생성
- **입력**: 원본 질문, DataFrame, 차트 이미지 (없을 수 있음)
- **출력**: 한국어 설명 문자열

---

## C5: app

### `main() -> None`
- **목적**: Streamlit 앱 진입점
- **입력**: 없음
- **출력**: 없음 (UI 렌더링)

### `_run_pipeline(question: str) -> None`
- **목적**: 3-모델 파이프라인 실행 및 결과 렌더링
- **입력**: 사용자 질문
- **출력**: 없음 (Streamlit에 직접 렌더링)
- **흐름**: build_prompt → ask_text2sql → validate+run_query → generate_chart → generate_description → 렌더링
