"""동적 데이터 마트 에이전트 — 의도 분류 → VIEW 생성 → 분석 파이프라인."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from bedrock_client import _invoke_model, TEXT2SQL_MODEL_ID
from data_executor import run_ddl, run_query, ATHENA_DATABASE

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
_INTENT_PROMPT_PATH = _PROMPTS_DIR / "intent_prompt.txt"
_MART_PROMPT_PATH = _PROMPTS_DIR / "mart_prompt.txt"
_SYSTEM_PROMPT_PATH = _PROMPTS_DIR / "system_prompt.txt"


def classify_intent(question: str) -> Dict[str, Any]:
    """사용자 질문의 의도를 분류한다.

    Returns:
        {"intent": "simple_analysis"} 또는
        {"intent": "mart_creation", "dimensions": [...], "metrics": [...], "description": "..."}
    """
    template = _INTENT_PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.replace("{question}", question)
    raw = _invoke_model(TEXT2SQL_MODEL_ID, prompt)
    return _parse_json(raw)


def create_mart_view(question: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 마트 VIEW를 생성한다.

    Args:
        question: 원본 사용자 질문
        intent_result: classify_intent의 결과 (dimensions, metrics, description 포함)

    Returns:
        {"view_name": "mart_xxx", "sql": "CREATE OR REPLACE VIEW ...", "description": "..."}
    """
    template = _MART_PROMPT_PATH.read_text(encoding="utf-8")

    dimensions = ", ".join(intent_result.get("dimensions", []))
    metrics = ", ".join(intent_result.get("metrics", ["매출", "주문건수"]))
    description = intent_result.get("description", "사용자 요청 기반 데이터 마트")

    # 뷰 이름 생성 (간단한 해시 기반)
    view_name = _generate_view_name(intent_result)

    prompt = (
        template
        .replace("{database}", ATHENA_DATABASE)
        .replace("{view_name}", view_name)
        .replace("{dimensions}", dimensions)
        .replace("{metrics}", metrics)
        .replace("{description}", description)
        .replace("{question}", question)
    )

    raw = _invoke_model(TEXT2SQL_MODEL_ID, prompt)
    return _parse_json(raw)


def execute_mart_creation(mart_result: Dict[str, Any]) -> str:
    """Athena에서 VIEW를 생성한다.

    Returns:
        생성된 뷰 이름
    """
    sql = mart_result["sql"]
    view_name = mart_result["view_name"]

    # DDL 실행 (CREATE OR REPLACE VIEW)
    run_ddl(sql)

    return view_name


def build_mart_analysis_prompt(question: str, view_name: str, mart_sql: str = "") -> str:
    """생성된 마트(VIEW) 위에서 분석 SQL을 생성하기 위한 프롬프트를 조립한다."""
    system_prompt = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    # 마트 SQL에서 컬럼 힌트 추출
    mart_context = f"""

## Additional Context
A data mart view has been created: {ATHENA_DATABASE}.{view_name}

### VIEW Definition (for column reference):
```sql
{mart_sql}
```

You MUST query FROM {ATHENA_DATABASE}.{view_name} (not fact_events).
Only use columns that exist in the VIEW definition above.
The view already has pre-computed/aggregated columns — do NOT re-aggregate unless doing further grouping.
Use standard Athena SQL syntax.

## Current Question
User: {question}
위 마트를 활용해서 가장 인사이트 있는 분석 쿼리를 작성해줘. VIEW에 정의된 컬럼만 사용할 것.
Assistant:
"""
    return system_prompt + mart_context


def run_mart_pipeline(question: str) -> Tuple[str, Dict[str, Any]]:
    """마트 생성 전체 파이프라인을 실행한다.

    Returns:
        (intent_type, pipeline_context)
        - intent_type: "simple_analysis" | "mart_creation"
        - pipeline_context: 파이프라인 실행 결과 컨텍스트
    """
    # Step 1: 의도 분류
    intent_result = classify_intent(question)
    intent_type = intent_result.get("intent", "simple_analysis")

    if intent_type == "simple_analysis":
        return "simple_analysis", {}

    # Step 2: VIEW SQL 생성
    mart_result = create_mart_view(question, intent_result)

    # Step 3: VIEW 실행
    view_name = execute_mart_creation(mart_result)

    # Step 4: 분석 프롬프트 생성
    analysis_prompt = build_mart_analysis_prompt(question, view_name, mart_result.get("sql", ""))

    return "mart_creation", {
        "view_name": view_name,
        "mart_description": mart_result.get("description", ""),
        "mart_sql": mart_result.get("sql", ""),
        "analysis_prompt": analysis_prompt,
    }


def _generate_view_name(intent_result: Dict[str, Any]) -> str:
    """의도 결과에서 뷰 이름을 생성한다."""
    dims = intent_result.get("dimensions", [])
    if dims:
        # 차원명을 조합하여 뷰 이름 생성
        name_parts = []
        for d in dims[:3]:  # 최대 3개 차원만 이름에 포함
            # 한글을 영문으로 간단 매핑
            mapping = {
                "연령대": "age",
                "나이": "age",
                "성별": "gender",
                "제품": "product",
                "제품유형": "product",
                "월": "monthly",
                "월간": "monthly",
                "분기": "quarterly",
                "결제": "payment",
                "배송": "shipping",
                "로열티": "loyalty",
                "고객": "customer",
            }
            mapped = mapping.get(d, d.lower().replace(" ", "_"))
            name_parts.append(mapped)
        return "mart_" + "_".join(name_parts)
    return "mart_custom_analysis"


def _parse_json(raw: str) -> Dict[str, Any]:
    """LLM 응답에서 JSON을 추출한다."""
    # JSON 블록 추출 시도 (중첩 가능)
    # 가장 바깥 {} 찾기
    brace_count = 0
    start_idx = -1
    for i, ch in enumerate(raw):
        if ch == "{":
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif ch == "}":
            brace_count -= 1
            if brace_count == 0 and start_idx >= 0:
                try:
                    return json.loads(raw[start_idx : i + 1])
                except json.JSONDecodeError:
                    start_idx = -1
                    continue

    # fallback: regex
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSON 파싱 실패: {raw[:300]}")
