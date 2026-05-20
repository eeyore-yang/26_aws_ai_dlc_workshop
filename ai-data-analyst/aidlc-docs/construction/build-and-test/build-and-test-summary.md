# Build and Test Summary

## 빌드 상태

| 항목 | 상태 | 비고 |
|------|:---:|------|
| 의존성 설치 | ✅ | boto3, streamlit, pandas, pyyaml, matplotlib |
| AWS 인프라 셋업 | ✅ | S3 + Glue + Athena (setup_infra.py) |
| Bedrock 모델 접근 | ✅ | Claude Sonnet 4 + Qwen3 Coder Next |
| Athena 테이블 | ✅ | 20,000행, 모든 컬럼 STRING |
| Streamlit 앱 실행 | ✅ | localhost:8501 |

## 테스트 결과 (CLI E2E)

| 단계 | 상태 | 결과 |
|------|:---:|------|
| Text2SQL (Claude) | ✅ | CAST 포함 SQL 정상 생성 |
| Athena 실행 | ✅ | 5행 반환 (제품 유형별 매출) |
| 차트 생성 (Qwen3 Coder) | ✅ | 32KB PNG 이미지 |
| Description (Claude) | ✅ | 한국어 3문장 설명 |

## 알려진 이슈

| # | 이슈 | 심각도 | 상태 |
|---|------|:---:|------|
| 1 | 차트 한글 폰트 깨짐 | 낮음 | 해결 (영어 레이블 사용) |
| 2 | pandas 3.0 to_numeric 호환 | - | 해결 |
| 3 | Claude 3.5 Sonnet v2 EOL | - | 해결 (Sonnet 4로 교체) |
| 4 | OpenCSVSerde 타입 캐스팅 | - | 해결 (모든 컬럼 STRING + CAST) |

## 데모 준비 상태

- [x] 파이프라인 end-to-end 동작 확인
- [x] 에러 시 graceful degradation
- [ ] 사이드바 예시 질문 버튼 (다음 polish 단계)
- [ ] 10개 질문 전수 테스트 (Streamlit UI에서)
