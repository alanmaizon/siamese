from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from app import gemini_client
from app.openai_client import OpenAIOutputError, generate_raw as openai_generate_raw

LAST_RAW_OUTPUT: Optional[str] = None


class InvalidJSONError(RuntimeError):
    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_system_prompt() -> str:
    prompt_path = _repo_root() / "prompts" / "system.txt"
    return prompt_path.read_text(encoding="utf-8")


def _clean_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _parse_json(raw: str) -> dict:
    cleaned = _clean_json_text(raw)
    return json.loads(cleaned)


def _provider() -> str:
    return os.environ.get("LLM_PROVIDER", "gemini").strip().lower()


def _generate(system_prompt: str, user_text: str, image_bytes: Optional[bytes]) -> str:
    global LAST_RAW_OUTPUT

    provider = _provider()
    if provider == "openai":
        raw = openai_generate_raw(system_prompt, user_text)
    elif provider == "gemini":
        raw = gemini_client.generate_raw(system_prompt, user_text, image_bytes)
    else:
        raise RuntimeError(
            "Unsupported LLM_PROVIDER. Use 'gemini' or 'openai'."
        )

    LAST_RAW_OUTPUT = raw
    return raw


def analyze(context_text: str, question: str, image_bytes_optional: Optional[bytes]) -> dict:
    system_prompt = _load_system_prompt()
    user_text = (
        f"Context:\n{context_text}\n\n"
        f"Question:\n{question}\n\n"
        "Return ONLY valid JSON matching the schema."
    )

    raw = _generate(system_prompt, user_text, image_bytes_optional)

    try:
        return _parse_json(raw)
    except json.JSONDecodeError:
        repair_prompt = (
            "Return ONLY valid JSON matching schema; here is your previous output; fix it.\n\n"
            f"Previous output:\n{raw}"
        )
        raw_repair = _generate(system_prompt, repair_prompt, None)
        try:
            return _parse_json(raw_repair)
        except json.JSONDecodeError:
            raise InvalidJSONError(
                "Model did not return valid JSON after one repair attempt.",
                raw_repair,
            )
