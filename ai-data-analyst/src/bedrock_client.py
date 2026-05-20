"""Bedrock Claude 호출 — 3개 모델 (Text2SQL, Chart, Description)."""
from __future__ import annotations

import io
import json
import os
import re
from typing import Any, Dict, Optional

import boto3

REGION: str = os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
TEXT2SQL_MODEL_ID: str = os.getenv(
    "BEDROCK_TEXT2SQL_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"
)
CHART_MODEL_ID: str = os.getenv(
    "BEDROCK_CHART_MODEL_ID", "qwen.qwen3-coder-next"
)
DESCRIPTION_MODEL_ID: str = os.getenv(
    "BEDROCK_DESCRIPTION_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"
)
MAX_TOKENS: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))

_client = boto3.client("bedrock-runtime", region_name=REGION)


def _invoke_model(model_id: str, prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Bedrock 모델을 호출하고 텍스트 응답을 반환한다.
    
    Anthropic과 Qwen 모델의 요청/응답 형식을 자동 분기한다.
    """
    if "anthropic" in model_id:
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": 0.0,
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        response = _client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    else:
        # Qwen / OpenAI-compatible format
        body = json.dumps(
            {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.0,
            }
        )
        response = _client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        result = json.loads(response["body"].read())
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return result.get("output", {}).get("text", str(result))


def ask_text2sql(question: str, prompt: str) -> Dict[str, Any]:
    """Model-1: 자연어 → SQL 변환.

    Returns:
        {"sql": "SELECT ..."}
    """
    raw = _invoke_model(TEXT2SQL_MODEL_ID, prompt)
    return _parse_json_response(raw)


def ask_chart_generation(question: str, data_csv: str, chart_prompt: str) -> Optional[bytes]:
    """Model-2: 데이터 기반 차트 이미지 생성.

    LLM이 matplotlib 코드를 생성하고, 로컬에서 실행하여 이미지를 반환한다.

    Returns:
        PNG 이미지 bytes 또는 None (실패 시)
    """
    try:
        raw_code = _invoke_model(CHART_MODEL_ID, chart_prompt)
        # 코드 블록에서 Python 코드 추출
        code = _extract_python_code(raw_code)
        # 코드 실행하여 이미지 생성
        return _execute_chart_code(code, data_csv)
    except Exception:
        return None


def ask_description(question: str, description_prompt: str) -> str:
    """Model-3: 데이터 + 차트 취합 → 한국어 설명 작성.

    Returns:
        한국어 설명 문자열
    """
    try:
        return _invoke_model(DESCRIPTION_MODEL_ID, description_prompt)
    except Exception:
        return "데이터 분석 결과를 요약하는 중 오류가 발생했습니다."


def _parse_json_response(raw: str) -> Dict[str, Any]:
    """LLM 응답에서 JSON을 추출한다."""
    json_match = re.search(r"\{[^}]+\}", raw, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError(f"JSON 파싱 실패: {raw[:200]}")


def _extract_python_code(raw: str) -> str:
    """LLM 응답에서 Python 코드 블록을 추출한다."""
    match = re.search(r"```python\s*\n(.*?)```", raw, re.DOTALL)
    if match:
        return match.group(1)
    return raw


def _execute_chart_code(code: str, data_csv: str) -> Optional[bytes]:
    """matplotlib 코드를 실행하여 차트 이미지를 생성한다."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd

        buf = io.BytesIO()
        local_ns = {
            "pd": pd,
            "plt": plt,
            "io": io,
            "buf": buf,
            "data_csv": data_csv,
        }
        exec(code, {"__builtins__": __builtins__}, local_ns)  # noqa: S102

        buf = local_ns.get("buf", buf)
        if buf.tell() == 0:
            plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")

        plt.close("all")
        buf.seek(0)
        return buf.read()
    except Exception:
        return None
