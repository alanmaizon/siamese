from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

LAST_RAW_OUTPUT: Optional[str] = None
_DOTENV_LOADED = False


class OpenAIOutputError(RuntimeError):
    pass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_env() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    load_dotenv(dotenv_path=_repo_root() / ".env", override=False)
    _DOTENV_LOADED = True


def generate_raw(system_prompt: str, user_text: str) -> str:
    global LAST_RAW_OUTPUT

    _load_env()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIOutputError("OPENAI_API_KEY is not set in the environment.")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        temperature=0.2,
    )

    text = getattr(response, "output_text", None)
    if not text:
        try:
            text = response.output_text
        except Exception:
            text = None

    if not text:
        raise OpenAIOutputError("No text content returned by OpenAI.")

    LAST_RAW_OUTPUT = text
    return text
