from __future__ import annotations


def read_text_capped(text: str, max_lines: int = 400) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)

    kept = lines[:max_lines]
    truncated = len(lines) - max_lines
    return "\n".join(kept) + f"\n\n[TRUNCATED: {truncated} additional lines omitted]"
