# Operations Guide — AI 데이터 분석가 챗봇

## 실행 방법

### 사전 요구사항
- Python 3.7+
- AWS 자격 증명 설정 (`~/.aws/credentials` 또는 환경 변수)
- Athena 데이터베이스 `aidlc_workshop` + `fact_events` 테이블 존재
- Bedrock Claude Sonnet 4 모델 접근 권한

### 로컬 실행
```bash
cd ai-data-analyst
pip install -r requirements.txt
streamlit run src/app.py --server.port 8501
```

### 환경 변수 (선택)
| 변수 | 기본값 | 설명 |
|------|--------|------|
| `AWS_DEFAULT_REGION` | us-east-1 | AWS 리전 |
| `BEDROCK_TEXT2SQL_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | Text2SQL 모델 |
| `BEDROCK_CHART_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | 차트 생성 모델 |
| `BEDROCK_DESCRIPTION_MODEL_ID` | us.anthropic.claude-sonnet-4-20250514-v1:0 | 설명 생성 모델 |
| `ATHENA_DATABASE` | aidlc_workshop | Athena 데이터베이스 |
| `ATHENA_WORKGROUP` | primary | Athena 워크그룹 |
| `ATHENA_OUTPUT_LOCATION` | s3://aidlc-workshop-athena-results-251165958261/query-results/ | 쿼리 결과 S3 경로 |

## 아키텍처 개요

```
[Streamlit UI] → [의도 분류] → [Text2SQL / 마트 생성] → [Athena] → [차트+설명] → [렌더링]
```

### 모듈 구성
| 모듈 | 파일 | 역할 |
|------|------|------|
| UI | `src/app.py` | Streamlit 챗봇 인터페이스 |
| LLM 호출 | `src/bedrock_client.py` | Bedrock Claude 호출 (3개 모델) |
| SQL 실행 | `src/data_executor.py` | Athena 쿼리 실행 + DDL |
| 프롬프트 | `src/query_parser.py` | 프롬프트 조립 |
| 시각화 | `src/visualizer.py` | 차트 + 설명 생성 래퍼 |
| 마트 에이전트 | `src/mart_agent.py` | 동적 VIEW 생성 오케스트레이션 |

## 운영 주의사항

### 비용
- **Bedrock**: 질문당 3~4회 모델 호출 (의도분류 + SQL + 차트 + 설명)
- **Athena**: 스캔 기반 과금. fact_events ~20K행이므로 미미
- **마트 생성**: VIEW는 비용 0 (실행 시점에만 스캔)

### 보안
- `validate_select_only()`: SELECT 외 SQL 차단
- `validate_view_ddl()`: CREATE OR REPLACE VIEW만 허용
- LLM 생성 코드 실행: `_execute_chart_code()`에서 제한된 네임스페이스로 실행

### 알려진 제약
1. Python 3.7 환경에서 Streamlit 1.23 사용 (chat_input 미지원 → form 기반)
2. matplotlib 스타일 호환성 이슈 → 자동 fallback 처리
3. 임시 세션 토큰 사용 시 만료 후 재설정 필요
4. 생성된 VIEW는 자동 삭제되지 않음 (수동 관리)

### 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| Unable to locate credentials | AWS 자격 증명 미설정 | `~/.aws/credentials` 파일 확인 |
| ResourceNotFoundException | 모델 EOL | 모델 ID를 inference profile로 변경 |
| COLUMN_NOT_FOUND | VIEW 컬럼 불일치 | 분석 프롬프트에 VIEW SQL 포함 확인 |
| 차트 생성 실패 | pd.StringIO / 스타일 에러 | bedrock_client.py 호환성 패치 확인 |
| Port already in use | 기존 프로세스 점유 | `lsof -ti:8501 | xargs kill -9` |

## 모니터링 (프로토타입 수준)

현재는 별도 모니터링 시스템 없이 Streamlit 로그로 확인:
```bash
# 로그 확인
streamlit run src/app.py 2>&1 | tee app.log
```

### 향후 개선 시 추가할 것
- CloudWatch Logs 연동
- Bedrock 호출 지연시간 메트릭
- Athena 쿼리 비용 추적
- 에러율 알림 (SNS)
