"""LLM 기반 차트 이미지 생성 + Description 작성 래퍼."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from bedrock_client import ask_chart_generation, ask_description
from query_parser import build_chart_prompt, build_description_prompt


def generate_chart(question: str, df: pd.DataFrame) -> Optional[bytes]:
    """Model-2를 통해 차트 이미지를 생성한다.

    Args:
        question: 원본 사용자 질문
        df: Athena 쿼리 결과 DataFrame

    Returns:
        PNG 이미지 bytes 또는 None (실패 시)
    """
    data_csv = df.to_csv(index=False)
    chart_prompt = build_chart_prompt(question, data_csv)
    return ask_chart_generation(question, data_csv, chart_prompt)


def generate_description(
    question: str, df: pd.DataFrame, chart_image: Optional[bytes]
) -> str:
    """Model-3를 통해 한국어 설명을 생성한다.

    Args:
        question: 원본 사용자 질문
        df: Athena 쿼리 결과 DataFrame
        chart_image: 차트 이미지 (사용하지 않지만 향후 멀티모달 확장용)

    Returns:
        한국어 설명 문자열
    """
    data_csv = df.to_csv(index=False)
    description_prompt = build_description_prompt(question, data_csv)
    return ask_description(question, description_prompt)
