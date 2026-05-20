# User Stories — AI 데이터 분석가 챗봇 (프로토타입)

> 프로토타입 특성: 사전 정의된 질문 예시(20~30개)를 사용하며, `data/fact_events.csv` 데이터만 활용한다.

## 데이터 스키마 (fact_events.csv 실제 컬럼)
| 컬럼 | 타입 | 값 예시 |
|------|------|---------|
| Customer ID | int | 1000 |
| Age | int | 53 |
| Gender | str | Male / Female |
| Loyalty Member | str | Yes / No |
| Product Type | str | Smartphone / Tablet / Laptop / Smartwatch |
| SKU | str | SKU1001~SKU1005 |
| Rating | int | 1~5 |
| Order Status | str | Completed / Cancelled |
| Payment Method | str | Credit Card / Paypal / Cash / Debit Card |
| Total Price | float | 주문 총액 |
| Unit Price | float | 단가 |
| Quantity | int | 수량 |
| Purchase Date | date | YYYY-MM-DD |
| Shipping Type | str | Standard / Express / Overnight |
| Add-ons Purchased | str | Accessory / Impulse Item / Extended Warranty |
| Add-on Total | float | 부가 상품 금액 |

---

## US-1: 제품 유형별 매출 조회
**As a** 데모 운영자  
**I want to** "제품 유형별 총 매출을 보여줘"라고 질문하면  
**So that** 제품 카테고리별 매출 비교 차트와 설명을 받을 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Product Type별 SUM(Total Price) WHERE Order Status='Completed'를 생성한다
- [ ] Athena에서 실행되어 DataFrame을 반환한다
- [ ] Model-2가 차트 이미지를 생성한다
- [ ] Model-3가 한국어 설명을 작성한다
- [ ] Streamlit에 차트 + 설명 + 테이블이 표시된다

---

## US-2: 월별 매출 추이 조회
**As a** 데모 운영자  
**I want to** "월별 매출 추이를 보여줘"라고 질문하면  
**So that** 시간에 따른 매출 변화를 시각적으로 확인할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 월별 SUM(Total Price)를 생성한다
- [ ] 시계열 차트 이미지가 생성된다
- [ ] 설명에 증감 추이가 포함된다

---

## US-3: 성별 구매 비중 조회
**As a** 데모 운영자  
**I want to** "성별 구매 비중은?"이라고 질문하면  
**So that** 남녀 구매 비율을 파이 차트로 확인할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Gender별 COUNT 또는 SUM을 생성한다
- [ ] 비중을 나타내는 차트 이미지가 생성된다
- [ ] 설명에 비율 수치가 포함된다

---

## US-4: 연령대별 평균 구매 금액 조회
**As a** 데모 운영자  
**I want to** "연령대별 평균 구매 금액은?"이라고 질문하면  
**So that** 연령 그룹별 소비 패턴을 비교할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 연령 구간(10대/20대/30대...)별 AVG(Total Price)를 생성한다
- [ ] 비교 차트 이미지가 생성된다
- [ ] 설명에 가장 높은/낮은 연령대가 언급된다

---

## US-5: 로열티 멤버 vs 일반 고객 비교
**As a** 데모 운영자  
**I want to** "로열티 멤버와 일반 고객의 매출 차이는?"이라고 질문하면  
**So that** 멤버십 효과를 수치로 확인할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Loyalty Member별 집계를 생성한다
- [ ] 비교 차트 이미지가 생성된다
- [ ] 설명에 차이 비율이 포함된다

---

## US-6: 결제 수단별 분석
**As a** 데모 운영자  
**I want to** "결제 수단별 주문 건수를 보여줘"라고 질문하면  
**So that** 선호 결제 수단을 파악할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Payment Method별 COUNT를 생성한다
- [ ] 차트 이미지가 생성된다
- [ ] 설명에 가장 많이 사용된 결제 수단이 언급된다

---

## US-7: 주문 취소율 분석
**As a** 데모 운영자  
**I want to** "제품별 주문 취소율은?"이라고 질문하면  
**So that** 취소가 많은 제품을 식별할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Product Type별 Cancelled 비율을 계산한다
- [ ] 차트 이미지가 생성된다
- [ ] 설명에 취소율이 높은 제품이 언급된다

---

## US-8: 배송 유형별 매출 분석
**As a** 데모 운영자  
**I want to** "배송 유형별 평균 주문 금액은?"이라고 질문하면  
**So that** 배송 옵션과 주문 금액의 관계를 파악할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Shipping Type별 AVG(Total Price)를 생성한다
- [ ] 비교 차트 이미지가 생성된다
- [ ] 설명에 인사이트가 포함된다

---

## US-9: 부가 상품(Add-on) 분석
**As a** 데모 운영자  
**I want to** "부가 상품 매출 비중은?"이라고 질문하면  
**So that** Add-on 판매 기여도를 확인할 수 있다

**Acceptance Criteria:**
- [ ] SQL이 Add-on Total 관련 집계를 생성한다
- [ ] 차트 이미지가 생성된다
- [ ] 설명에 부가 상품 비중 수치가 포함된다

---

## US-10: 에러 처리 — 잘못된 질문
**As a** 데모 운영자  
**I want to** 데이터와 무관한 질문("오늘 날씨 어때?")을 입력하면  
**So that** 친절한 에러 메시지가 표시되고 시스템이 중단되지 않는다

**Acceptance Criteria:**
- [ ] Model-1이 SQL 생성 불가 시 적절한 응답을 반환한다
- [ ] UI에 "이 질문은 데이터 범위를 벗어납니다" 류의 메시지가 표시된다
- [ ] 시스템이 정상 상태를 유지한다

---

## US-11: 에러 처리 — Athena 실행 실패
**As a** 데모 운영자  
**I want to** SQL 실행이 실패하면  
**So that** 사용자에게 친절한 에러 메시지가 표시된다

**Acceptance Criteria:**
- [ ] Athena 에러 시 사용자에게 "쿼리 실행에 실패했습니다" 메시지 표시
- [ ] 에러 상세는 로그에만 기록
- [ ] 다음 질문을 정상적으로 받을 수 있다

---

## 사전 정의 질문 예시 (20개)

프로토타입에서 사용할 질문 목록:

| # | 질문 | 기대 분석 유형 |
|---|------|--------------|
| 1 | 제품 유형별 총 매출을 보여줘 | 카테고리별 합계 |
| 2 | 월별 매출 추이를 보여줘 | 시계열 |
| 3 | 성별 구매 비중은? | 비율 |
| 4 | 연령대별 평균 구매 금액은? | 그룹별 평균 |
| 5 | 로열티 멤버와 일반 고객의 매출 차이는? | 그룹 비교 |
| 6 | 결제 수단별 주문 건수를 보여줘 | 카테고리별 건수 |
| 7 | 제품별 주문 취소율은? | 비율 계산 |
| 8 | 배송 유형별 평균 주문 금액은? | 그룹별 평균 |
| 9 | 부가 상품 매출 비중은? | 비율 |
| 10 | 가장 많이 팔린 제품은? | TOP-N |
| 11 | 평점 4 이상인 주문의 평균 금액은? | 필터 + 집계 |
| 12 | 분기별 주문 건수 추이를 보여줘 | 시계열 |
| 13 | 고객당 평균 주문 횟수는? | 고객별 집계 |
| 14 | 단가가 가장 높은 제품 TOP 3는? | TOP-N |
| 15 | 2024년 상반기 vs 하반기 매출 비교 | 기간 비교 |
| 16 | Overnight 배송 고객의 평균 주문 금액은? | 필터 + 집계 |
| 17 | 남성 로열티 멤버의 제품별 매출은? | 다중 필터 |
| 18 | 주문 수량이 5개 이상인 주문 비율은? | 필터 + 비율 |
| 19 | 월별 취소 건수 추이를 보여줘 | 시계열 + 필터 |
| 20 | 제품별 평균 평점은? | 그룹별 평균 |

---

## 페르소나-스토리 매핑

| 페르소나 | 관련 스토리 |
|---------|-----------|
| 데모 운영자 | US-1 ~ US-11 (전체) |
| 데모 관객 | US-1 ~ US-9 (정상 흐름 관람) |
