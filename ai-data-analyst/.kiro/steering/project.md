# Project: AI 데이터 분석가 챗봇

## 목적
비전문가가 자연어로 데이터 질문을 하면 AI가 SQL을 생성하고, Athena로 조회한 뒤
LLM이 차트 이미지를 직접 생성하여 텍스트 요약과 함께 돌려주는 챗봇.

## 파이프라인
자연어 질문 → Bedrock Model-1 (Text2SQL) → Athena → Bedrock Model-2 (차트 이미지 생성) → Bedrock Model-3 (Athena 결과 + 차트 취합 → Description 작성) → Streamlit

## 기술 스택
| 컴포넌트 | 기술 |
|---------|------|
| AI/LLM (Text2SQL) | Amazon Bedrock Model-1 (자연어→SQL) |
| AI/LLM (Chart Gen) | Amazon Bedrock Model-2 (데이터→차트 이미지 생성) |
| AI/LLM (Description) | Amazon Bedrock Model-3 (데이터+차트 취합→한국어 설명 작성) |
| Data Layer | Athena + S3 + Glue Catalog |
| Storage | S3 |
| Query Engine | Athena |
| Schema Registry | Glue Catalog |
| UI | Streamlit (app.py 단일 파일) |
| 차트 | Bedrock LLM 생성 이미지 (Plotly 미사용) |
| 방법론 | AI-DLC (Inception → Construction) |

## fact_events.csv 스키마
| 컬럼 | 타입 | 설명 |
|------|------|------|
| customer_id | str | 고객 식별자 |
| age_group | str | 10s / 20s / 30s / 40s / 50s / 60s+ |
| gender | str | male / female / non-binary |
| event_date | date | YYYY-MM-DD |
| week_label | str | YYYY-WNN |
| event_type | str | visit / purchase |
| product_category | str | Headphones / Earbuds / Portable_Speaker / Soundbar / Home_Audio / Wireless_Speaker |
| sku | str | 상품 코드 |
| loyalty_member | str | yes / no |
| amount | float | purchase만 유효, visit은 0.0 |

## 전환율 공식
conversion_rate = COUNT(*) FILTER (WHERE event_type='purchase')
                / NULLIF(COUNT(*) FILTER (WHERE event_type='visit'), 0)

## 완성 기준
1. "지난달 카테고리별 매출은?" → LLM 차트 이미지 + 수치 테이블 + 한국어 설명
2. "30대 여성 전환율 추이를 보여줘" → LLM 차트 이미지 + 한국어 설명

## 빌드 제약
- 총 6시간 (AWS Summit Seoul 2026-05-20)
- 팀원 3인, 역할 브랜치 (dev/A, dev/B, dev/C)
- aidlc-docs/audit.md 를 AI-DLC 활용 증거로 제출
