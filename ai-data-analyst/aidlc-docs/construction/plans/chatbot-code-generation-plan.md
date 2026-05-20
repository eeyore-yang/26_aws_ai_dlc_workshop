# Code Generation Plan — AI 데이터 분석가 챗봇

## Unit Context
- **Unit**: 전체 통합 (단일 유닛)
- **Workspace Root**: /Users/yangchanghwan/AWS-AI-DLC-2026/26_aws_ai_dlc_workshop/ai-data-analyst
- **Project Type**: Brownfield (skeleton stubs)
- **Stories**: US-1 ~ US-11

## Generation Steps

- [x] Step 1: config.yaml 생성 (환경 설정)
- [x] Step 2: prompts/system_prompt.txt 업데이트 (실제 CSV 스키마 반영)
- [x] Step 3: prompts/few_shot_examples.yaml 업데이트 (실제 CSV 컬럼 반영)
- [x] Step 4: prompts/chart_prompt.txt 생성 (Model-2 차트 생성 프롬프트)
- [x] Step 5: prompts/description_prompt.txt 생성 (Model-3 설명 작성 프롬프트)
- [x] Step 6: src/query_parser.py 구현 (Few-shot 로더 + 프롬프트 조립)
- [x] Step 7: src/bedrock_client.py 구현 (Model-1/2/3 호출)
- [x] Step 8: src/data_executor.py 구현 (Athena SQL 실행)
- [x] Step 9: src/visualizer.py 구현 (차트 생성 + 설명 작성 래퍼)
- [x] Step 10: src/app.py 구현 (Streamlit UI + 파이프라인 통합)
- [x] Step 11: requirements.txt 업데이트
- [x] Step 12: 코드 요약 문서 생성 → `aidlc-docs/construction/chatbot/code/code-summary.md`

## Story Traceability
| Step | Stories | Status |
|------|---------|--------|
| Step 6-7 | US-1~US-9 (정상 흐름 기반) | ✅ |
| Step 8 | US-1~US-9 + US-11 (Athena 실행 + 에러) | ✅ |
| Step 9 | US-1~US-9 (차트+설명) | ✅ |
| Step 10 | US-1~US-11 (전체 통합 + 에러 처리) | ✅ |
