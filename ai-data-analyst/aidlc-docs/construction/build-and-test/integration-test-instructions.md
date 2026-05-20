# Integration Test Instructions — AI 데이터 분석가 챗봇

## 테스트 전제 조건
- `setup_infra.py` 실행 완료 (Athena 테이블 존재)
- AWS credentials 유효
- Bedrock 모델 접근 가능 (Claude Sonnet 4 + Qwen3 Coder)

## End-to-End 테스트 (CLI)

아래 스크립트로 전체 파이프라인을 UI 없이 검증:

```bash
python -c "
import sys; sys.path.insert(0, 'src')
from query_parser import build_prompt
from bedrock_client import ask_text2sql
from data_executor import run_query, validate_select_only
from visualizer import generate_chart, generate_description

question = '제품 유형별 총 매출을 보여줘'
prompt = build_prompt(question)
result = ask_text2sql(question, prompt)
sql = result['sql']
print(f'SQL: {sql}')

validate_select_only(sql)
df = run_query(sql)
print(f'Rows: {len(df)}')

chart = generate_chart(question, df)
print(f'Chart: {len(chart)} bytes' if chart else 'Chart: FAILED')

desc = generate_description(question, df, chart)
print(f'Description: {desc[:100]}')
print('=== PASS ===')
"
```

## 질문별 검증 매트릭스

| # | 질문 | 검증 항목 | 예상 결과 |
|---|------|----------|----------|
| 1 | 제품 유형별 총 매출을 보여줘 | SQL 생성 + Athena 실행 + 차트 + 설명 | 5행 (Smartphone, Smartwatch, Laptop, Tablet, Headphones) |
| 2 | 월별 매출 추이를 보여줘 | DATE_PARSE + DATE_TRUNC 사용 | 시계열 데이터 |
| 3 | 성별 구매 비중은? | Gender 그룹핑 | 2행 (Male, Female) |
| 4 | 연령대별 평균 구매 금액은? | CASE WHEN + CAST(age AS INT) | 6행 (10대~60대+) |
| 5 | 결제 수단별 주문 건수를 보여줘 | COUNT + GROUP BY | 4행 |
| 6 | 제품별 주문 취소율은? | Cancelled 비율 계산 | 5행 |
| 7 | 배송 유형별 평균 주문 금액은? | AVG + CAST | 3행 |
| 8 | 로열티 멤버와 일반 고객의 매출 차이는? | loyalty_member 그룹핑 | 2행 |
| 9 | 가장 많이 팔린 제품은? | SUM(quantity) + LIMIT | 5행 |
| 10 | 분기별 주문 건수 추이를 보여줘 | DATE_TRUNC quarter | 시계열 |

## 에러 시나리오 테스트

| # | 입력 | 예상 동작 |
|---|------|----------|
| E1 | "오늘 날씨 어때?" | Model-1이 SQL 생성 시도 → 에러 메시지 또는 빈 결과 |
| E2 | (빈 입력) | 아무 동작 없음 |
| E3 | credentials 만료 상태 | "SQL 생성에 실패했습니다" 에러 메시지 |

## 성공 기준

- [ ] 질문 1~10 중 최소 8개 이상 정상 동작 (SQL + Athena + 차트 + 설명)
- [ ] 차트 이미지가 PNG로 생성됨 (0 bytes가 아님)
- [ ] 한국어 설명이 2~4문장으로 생성됨
- [ ] 에러 시 앱이 중단되지 않고 메시지 표시
