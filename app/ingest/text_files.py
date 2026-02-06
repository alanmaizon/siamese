from __future__ import annotations

from typing import Iterable


def decode_text(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _render_lines(lines: Iterable[str], start_line: int) -> str:
    rendered = []
    for idx, line in enumerate(lines):
        rendered.append(f"{start_line + idx:6d}: {line}")
    return "\n".join(rendered)


def head_tail_with_line_numbers(text: str, n: int = 120) -> str:
    lines = text.splitlines()
    total = len(lines)
    if total == 0:
        return "(empty file)"

    if total <= n * 2:
        return _render_lines(lines, 1)

    head = _render_lines(lines[:n], 1)
    tail_start = total - n + 1
    tail = _render_lines(lines[-n:], tail_start)

    return (
        f"First {n} lines:\n{head}\n\n"
        f"Last {n} lines:\n{tail}\n\n"
        f"(Showing {n} + {n} of {total} total lines)"
    )
