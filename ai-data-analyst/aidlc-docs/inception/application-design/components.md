# Components — AI 데이터 분석가 챗봇

## C1: bedrock_client
- **파일**: `src/bedrock_client.py`
- **목적**: Amazon Bedrock 모델 호출 전담
- **책임**:
  - Model-1 호출: 자연어 → SQL 변환
  - Model-2 호출: DataFrame → 차트 이미지 생성
  - Model-3 호출: 데이터 + 차트 → 한국어 설명 작성
  - Bedrock 에러 처리 및 응답 파싱

## C2: query_parser
- **파일**: `src/query_parser.py`
- **목적**: Few-shot 예시 로딩 및 프롬프트 조립
- **책임**:
  - `prompts/few_shot_examples.yaml` 로드
  - `prompts/system_prompt.txt` 로드
  - Model-1용 최종 프롬프트 조립 (시스템 프롬프트 + few-shot + 사용자 질문)

## C3: data_executor
- **파일**: `src/data_executor.py`
- **목적**: Amazon Athena SQL 실행
- **책임**:
  - SQL SELECT-only 검증 (DML/DDL 차단)
  - Athena 쿼리 실행 (boto3)
  - 결과를 pandas DataFrame으로 변환
  - 쿼리 실행 에러 처리

## C4: visualizer
- **파일**: `src/visualizer.py`
- **목적**: LLM 기반 차트 이미지 생성 + Description 작성
- **책임**:
  - DataFrame을 텍스트(CSV/JSON)로 변환하여 Model-2에 전달
  - Model-2 응답에서 차트 이미지(base64) 추출
  - Model-3에 데이터 + 차트 전달하여 설명 생성
  - 이미지 디코딩 및 표시 준비

## C5: app (Streamlit UI)
- **파일**: `src/app.py`
- **목적**: 사용자 인터페이스 (챗봇)
- **책임**:
  - 채팅 입력 수신
  - 파이프라인 오케스트레이션 (C2→C1→C3→C4 순차 호출)
  - 결과 렌더링 (차트 이미지 + 설명 + 데이터 테이블)
  - 대화 히스토리 UI 유지
  - 에러 메시지 표시
