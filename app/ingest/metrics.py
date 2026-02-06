from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd


def summarize_metrics_csv(data: bytes) -> str:
    df = pd.read_csv(BytesIO(data))
    lines: list[str] = []

    lines.append(f"Row count: {len(df)}")
    lines.append("Columns: " + ", ".join(df.columns.astype(str).tolist()))

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        lines.append("Summary stats (numeric): no numeric columns detected.")
    else:
        summary = numeric_df.describe().to_string()
        lines.append("Summary stats (numeric):\n" + summary)

    if "api_latency_p95_ms" in df.columns:
        series = pd.to_numeric(df["api_latency_p95_ms"], errors="coerce")
        top_idx = series.nlargest(3).dropna().index.tolist()
        if not top_idx:
            lines.append("Anomaly detection: api_latency_p95_ms had no numeric values.")
        else:
            window_idx: set[int] = set()
            for idx in top_idx:
                for i in range(idx - 2, idx + 3):
                    if 0 <= i < len(df):
                        window_idx.add(i)
            window_df = df.loc[sorted(window_idx)]
            lines.append(
                "Anomaly windows around top 3 api_latency_p95_ms rows (+/- 2 rows):\n"
                + window_df.to_string(index=True)
            )
    else:
        lines.append("Anomaly detection skipped: column 'api_latency_p95_ms' not found.")

    return "\n".join(lines)
