"""Few-shot 예시 로더 및 프롬프트 조립."""
from pathlib import Path
from typing import Any
import yaml

_EXAMPLES_PATH = Path(__file__).parent.parent / "prompts" / "few_shot_examples.yaml"

def load_few_shot_examples() -> list[dict[str, Any]]:
    raise NotImplementedError

def build_user_message(question: str) -> str:
    raise NotImplementedError
