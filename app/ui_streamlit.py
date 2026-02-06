from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.context_builder import build_context
from app.gemini_client import InvalidJSONError
from app import gemini_client
from app.schemas import IncidentAnalysis


st.set_page_config(page_title="Living System Debugger", layout="wide")

st.title("Living System Debugger")
st.write(
    "Local-first incident analysis. Upload logs and metrics, ask a question, "
    "and get a structured, validated analysis."
)

uploaded_files = st.file_uploader(
    "Upload incident artifacts (logs, metrics.csv, docker-compose.yml, nginx.conf, architecture.png)",
    type=["log", "txt", "csv", "yml", "yaml", "conf", "png"],
    accept_multiple_files=True,
)

question = st.text_area(
    "Question",
    placeholder="Why did API latency spike after the most recent deployment?",
    height=120,
)

analyze_clicked = st.button("Analyze")


def _render_list(title: str, items: list[str]) -> None:
    st.markdown(f"**{title}**")
    if not items:
        st.write("(none)")
        return
    for item in items:
        st.markdown(f"- {item}")


def _write_run_artifacts(
    run_dir: Path,
    filenames: list[str],
    question_text: str,
    context_text: str,
    output_json: dict | None,
    raw_output: str | None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "inputs.json").write_text(
        json.dumps({"files": filenames}, indent=2), encoding="utf-8"
    )
    (run_dir / "question.txt").write_text(question_text, encoding="utf-8")
    (run_dir / "context.txt").write_text(context_text, encoding="utf-8")
    if output_json is not None:
        (run_dir / "output.json").write_text(
            json.dumps(output_json, indent=2), encoding="utf-8"
        )
    if raw_output:
        (run_dir / "raw_output.txt").write_text(raw_output, encoding="utf-8")


if analyze_clicked:
    if not uploaded_files:
        st.error("Please upload at least one artifact file.")
        st.stop()
    if not question.strip():
        st.error("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing incident..."):
        context_text, filenames, image_bytes = build_context(uploaded_files)
        run_dir = Path("runs") / datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        try:
            result = gemini_client.analyze(context_text, question, image_bytes)
            analysis = IncidentAnalysis.model_validate(result)
        except InvalidJSONError as exc:
            _write_run_artifacts(
                run_dir=run_dir,
                filenames=filenames,
                question_text=question,
                context_text=context_text,
                output_json=None,
                raw_output=exc.raw_output,
            )
            st.error(
                "Model returned invalid JSON after one repair attempt. "
                f"Raw output saved to {run_dir}/raw_output.txt"
            )
            st.stop()
        except ValidationError as exc:
            _write_run_artifacts(
                run_dir=run_dir,
                filenames=filenames,
                question_text=question,
                context_text=context_text,
                output_json=None,
                raw_output=gemini_client.LAST_RAW_OUTPUT or "",
            )
            st.error(
                "Model returned JSON that does not match the schema. "
                f"Raw output saved to {run_dir}/raw_output.txt"
            )
            st.text(str(exc))
            st.stop()
        except Exception as exc:
            _write_run_artifacts(
                run_dir=run_dir,
                filenames=filenames,
                question_text=question,
                context_text=context_text,
                output_json=None,
                raw_output=gemini_client.LAST_RAW_OUTPUT or "",
            )
            st.error(f"Analysis failed: {exc}")
            st.stop()

        analysis_dict = analysis.model_dump()
        _write_run_artifacts(
            run_dir=run_dir,
            filenames=filenames,
            question_text=question,
            context_text=context_text,
            output_json=analysis_dict,
            raw_output=gemini_client.LAST_RAW_OUTPUT or "",
        )

    st.success(f"Analysis complete. Saved run to {run_dir}/")

    st.markdown("**Summary**")
    st.write(analysis.summary)

    st.metric(label="Confidence", value=f"{analysis.confidence:.2f}")

    _render_list("Timeline", analysis.timeline)

    st.markdown("**Likely Root Cause**")
    st.write(analysis.likely_root_cause)

    _render_list("Evidence", analysis.evidence)
    _render_list("Recommended Fixes", analysis.recommended_fixes)
    _render_list("Missing Information", analysis.missing_information)

    raw_json = json.dumps(analysis_dict, indent=2)

    with st.expander("Raw JSON"):
        st.code(raw_json, language="json")

    st.download_button(
        label="Download JSON",
        data=raw_json,
        file_name="incident_analysis.json",
        mime="application/json",
    )
