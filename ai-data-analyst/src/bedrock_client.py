"""Bedrock Claude 호출 — NL → {sql, chart_type, summary} JSON 반환."""
import os
from pathlib import Path
from typing import Any

MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"
MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
REGION: str = os.getenv("AWS_REGION", "ap-northeast-2")
_SYSTEM_PROMPT: str = (Path(__file__).parent.parent / "prompts" / "system_prompt.txt").read_text(encoding="utf-8")

def ask_bedrock(question: str) -> dict[str, Any]:
    """자연어 질문을 Bedrock에 전달하고 {sql, chart_type, summary} 반환."""
    if MOCK_MODE:
        return _mock_response(question)
    raise NotImplementedError

def _load_few_shot_text() -> str:
    raise NotImplementedError

def _parse_json_response(raw: str) -> dict[str, Any]:
    raise NotImplementedError

def _mock_response(question: str) -> dict[str, Any]:
    return {
        "sql": "SELECT product_category, SUM(amount) AS revenue FROM fact_events WHERE event_type='purchase' GROUP BY product_category ORDER BY revenue DESC",
        "chart_type": "bar",
        "summary": f"[MOCK] '{question}'에 대한 카테고리별 매출 현황입니다.",
    }
