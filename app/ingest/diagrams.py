from __future__ import annotations


def is_png(filename: str) -> bool:
    return filename.lower().endswith(".png")


def describe_diagram(filename: str) -> str:
    return f"Architecture diagram provided: {filename}"
