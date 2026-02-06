from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

import requests

LAST_RAW_OUTPUT: Optional[str] = None
_DOTENV_LOADED = False


class ModelOutputError(RuntimeError):
    pass


class InvalidJSONError(ModelOutputError):
    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_env() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return
    load_dotenv(dotenv_path=_repo_root() / ".env", override=False)
    _DOTENV_LOADED = True


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


def _extract_text_from_response(resp: Any) -> str:
    if hasattr(resp, "text") and resp.text:
        return resp.text

    if isinstance(resp, dict):
        return _extract_text_from_rest(resp)

    candidates = getattr(resp, "candidates", None)
    if candidates:
        for cand in candidates:
            content = getattr(cand, "content", None)
            if content is None and isinstance(cand, dict):
                content = cand.get("content")
            parts = getattr(content, "parts", None) if content is not None else None
            if parts is None and isinstance(content, dict):
                parts = content.get("parts")
            if parts:
                for part in parts:
                    text = getattr(part, "text", None)
                    if text is None and isinstance(part, dict):
                        text = part.get("text")
                    if text:
                        return text

    raise ModelOutputError("No text content returned by Gemini.")


def _extract_text_from_rest(data: dict) -> str:
    for cand in data.get("candidates", []):
        content = cand.get("content", {})
        for part in content.get("parts", []):
            if "text" in part:
                return part["text"]
    raise ModelOutputError("No text content returned by Gemini (REST).")


def _sdk_generate(system_prompt: str, user_text: str, image_bytes: Optional[bytes]) -> str:
    _load_env()
    from google import genai

    try:
        from google.genai import types
    except Exception:
        types = None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ModelOutputError("GEMINI_API_KEY is not set in the environment.")

    model = os.environ.get("GEMINI_MODEL", "gemini-3-pro-preview")
    client = genai.Client(api_key=api_key)

    contents: Any = None
    config: Any = None

    if types is not None and hasattr(types, "Part"):
        parts = [types.Part.from_text(user_text)]
        if image_bytes:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        if hasattr(types, "Content"):
            contents = [types.Content(role="user", parts=parts)]
        else:
            contents = parts

        if hasattr(types, "GenerateContentConfig"):
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.2,
            )
        elif hasattr(types, "GenerationConfig"):
            config = types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2,
            )

    if contents is None:
        if image_bytes:
            user_text += "\n\n(Note: architecture diagram bytes available.)"
        contents = user_text

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    except TypeError:
        combined = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_text}"
        response = client.models.generate_content(
            model=model,
            contents=combined,
        )

    return _extract_text_from_response(response)


def _rest_generate(system_prompt: str, user_text: str, image_bytes: Optional[bytes]) -> str:
    _load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ModelOutputError("GEMINI_API_KEY is not set in the environment.")

    model = os.environ.get("GEMINI_MODEL", "gemini-3")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )

    parts: list[dict[str, Any]] = [{"text": user_text}]
    if image_bytes:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        parts.append(
            {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": encoded,
                }
            }
        )

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return _extract_text_from_rest(data)


def _generate(system_prompt: str, user_text: str, image_bytes: Optional[bytes]) -> str:
    try:
        return _sdk_generate(system_prompt, user_text, image_bytes)
    except Exception:
        return _rest_generate(system_prompt, user_text, image_bytes)


def analyze(context_text: str, question: str, image_bytes_optional: Optional[bytes]) -> dict:
    global LAST_RAW_OUTPUT

    system_prompt = _load_system_prompt()
    user_text = (
        f"Context:\n{context_text}\n\n"
        f"Question:\n{question}\n\n"
        "Return ONLY valid JSON matching the schema."
    )

    raw = _generate(system_prompt, user_text, image_bytes_optional)
    LAST_RAW_OUTPUT = raw

    try:
        return _parse_json(raw)
    except json.JSONDecodeError:
        repair_prompt = (
            "Return ONLY valid JSON matching schema; here is your previous output; fix it.\n\n"
            f"Previous output:\n{raw}"
        )
        raw_repair = _generate(system_prompt, repair_prompt, None)
        LAST_RAW_OUTPUT = raw_repair
        try:
            return _parse_json(raw_repair)
        except json.JSONDecodeError:
            raise InvalidJSONError(
                "Model did not return valid JSON after one repair attempt.",
                raw_repair,
            )
