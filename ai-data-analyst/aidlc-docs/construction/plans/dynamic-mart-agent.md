# 동적 데이터 마트 에이전트 설계 문서

## 개요

사용자의 자연어 질의를 분석하여, 단순 조회가 아닌 **재사용 가능한 분석용 데이터 마트(VIEW)**를 동적으로 생성하고, 그 위에서 인사이트를 도출하는 에이전트입니다.

## 아키텍처

```
[사용자 질문]
    │
    ▼
[Model-0: 의도 분류] ─── intent_prompt.txt
    │
    ├─ "simple_analysis" → 기존 Text2SQL 파이프라인
    │
    └─ "mart_creation"
          │
          ▼
    [Model-1a: VIEW SQL 생성] ─── mart_prompt.txt
          │
          ▼
    Athena: CREATE OR REPLACE VIEW
          │
          ▼
    [Model-1b: 분석 SQL 생성] (VIEW 기반)
          │
          ▼
    Athena: SELECT ... FROM mart_xxx
          │
          ▼
    [Model-2: 차트 생성] + [Model-3: 설명 생성]
          │
          ▼
    Streamlit 렌더링
```

## 파일 구조

| 파일 | 역할 |
|------|------|
| `src/mart_agent.py` | 오케스트레이션: 의도분류 → VIEW 생성 → 분석 프롬프트 조립 |
| `src/data_executor.py` | `run_ddl()`: CREATE OR REPLACE VIEW 실행 (안전장치 포함) |
| `src/app.py` | Streamlit UI: 마트 생성 분기 + 결과 렌더링 |
| `prompts/intent_prompt.txt` | 의도 분류 프롬프트 |
| `prompts/mart_prompt.txt` | VIEW 생성 SQL 프롬프트 |

## 의도 분류 기준

| 분류 | 트리거 조건 |
|------|-------------|
| `simple_analysis` | 단순 조회/집계 질문 (월별 매출, 제품별 판매량 등) |
| `mart_creation` | "마트", "뷰", "분석용 테이블" 언급 / 3개 이상 차원 조합 / 세그먼트·코호트·RFM 등 |

## 안전장치

1. **DDL 제한**: `CREATE OR REPLACE VIEW`만 허용. DROP, DELETE, INSERT 등 차단.
2. **SELECT 검증**: 분석 SQL은 기존 `validate_select_only()` 통과 필수.
3. **VIEW 네이밍**: `mart_` 접두사 강제로 일반 테이블과 구분.

## 사용 예시

### 입력
```
연령대별 제품유형별 월간 매출 마트를 만들어줘
```

### 출력
1. VIEW 생성: `aidlc_workshop.mart_age_group_product_type_month`
2. 분석 SQL: LAG 윈도우 함수로 월간 성장률 계산
3. 설명: "60대 이상이 스마트폰에서 최고 매출, 40대 월간 성장률 251.3% 최고"

## 제약사항 (프로토타입)

- 스키마는 `fact_events` 단일 테이블 하드코딩
- VIEW 라이프사이클 관리 없음 (수동 삭제 필요)
- 멀티턴 대화 미지원 (1턴에 자동 판단)
- Glue Catalog 동적 조회 미구현

## 향후 개선 방향 (Phase 2+)

1. Glue Catalog 연동으로 동적 스키마 인식
2. CTAS 기반 물리적 마트 생성 + TTL 자동 정리
3. ReAct 에이전트 루프 (계획 → 실행 → 검증 → 수정)
4. 멀티턴 대화로 마트 설계 확인/수정
5. 비용 제어 (스캔량 제한, 파티션 활용)
