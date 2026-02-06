from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Optional

from app.ingest.config import read_text_capped
from app.ingest.diagrams import describe_diagram, is_png
from app.ingest.metrics import summarize_metrics_csv
from app.ingest.text_files import decode_text, head_tail_with_line_numbers


def _get_bytes(uploaded_file: Any) -> bytes:
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()
    return uploaded_file.read()


def build_context(uploaded_files: Iterable[Any]) -> tuple[str, list[str], Optional[bytes]]:
    sections: list[str] = []
    filenames: list[str] = []
    image_bytes: Optional[bytes] = None

    for uploaded in uploaded_files:
        filename = getattr(uploaded, "name", "unknown")
        filenames.append(filename)
        name_lower = filename.lower()
        suffix = Path(filename).suffix.lower()
        data = _get_bytes(uploaded)

        if is_png(filename):
            sections.append(describe_diagram(filename))
            if image_bytes is None:
                image_bytes = data
            continue

        if name_lower in {"docker-compose.yml", "docker-compose.yaml", "nginx.conf"}:
            text = decode_text(data)
            capped = read_text_capped(text, max_lines=400)
            sections.append(f"=== FILE: {filename} (config) ===\n{capped}")
            continue

        if suffix in {".yml", ".yaml"}:
            text = decode_text(data)
            capped = read_text_capped(text, max_lines=400)
            sections.append(f"=== FILE: {filename} (config) ===\n{capped}")
            continue

        if suffix == ".csv":
            try:
                metrics_summary = summarize_metrics_csv(data)
            except Exception as exc:
                metrics_summary = f"Failed to parse CSV metrics: {exc}"
            sections.append(f"=== FILE: {filename} (metrics) ===\n{metrics_summary}")
            continue

        text = decode_text(data)
        snippet = head_tail_with_line_numbers(text, n=120)
        sections.append(f"=== FILE: {filename} (log/text) ===\n{snippet}")

    if not sections:
        sections.append("No artifacts provided.")

    context = "INCIDENT ARTIFACTS CONTEXT\n\n" + "\n\n".join(sections)
    return context, filenames, image_bytes
