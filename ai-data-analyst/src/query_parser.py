"""Few-shot 예시 로더 및 프롬프트 조립."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
_SYSTEM_PROMPT_PATH = _PROMPTS_DIR / "system_prompt.txt"
_EXAMPLES_PATH = _PROMPTS_DIR / "few_shot_examples.yaml"
_CHART_PROMPT_PATH = _PROMPTS_DIR / "chart_prompt.txt"
_DESCRIPTION_PROMPT_PATH = _PROMPTS_DIR / "description_prompt.txt"


def load_few_shot_examples() -> List[Dict[str, Any]]:
    """YAML 파일에서 few-shot 예시를 로드한다."""
    with open(_EXAMPLES_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("few_shot_examples", [])


def build_prompt(question: str) -> str:
    """Model-1(Text2SQL)용 최종 프롬프트를 조립한다.

    시스템 프롬프트 + few-shot 예시 + 사용자 질문을 결합.
    """
    system_prompt = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    examples = load_few_shot_examples()

    few_shot_text = "\n\n## Examples\n"
    for ex in examples:
        few_shot_text += f'\nUser: {ex["question"]}\n'
        few_shot_text += f'Assistant: {{"sql": "{ex["output"]["sql"]}"}}\n'

    user_section = f"\n\n## Current Question\nUser: {question}\nAssistant:"

    return system_prompt + few_shot_text + user_section


def build_chart_prompt(question: str, data_csv: str) -> str:
    """Model-2(Chart Generation)용 프롬프트를 조립한다."""
    template = _CHART_PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{question}", question).replace("{data_csv}", data_csv)


def build_description_prompt(question: str, data_csv: str) -> str:
    """Model-3(Description)용 프롬프트를 조립한다."""
    template = _DESCRIPTION_PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{question}", question).replace("{data_csv}", data_csv)
