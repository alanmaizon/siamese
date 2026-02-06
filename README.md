# Inspiration
I wanted a local-first way to turn messy incident artifacts into a crisp, evidence-backed root cause analysis without sending sensitive data to a remote SaaS UI. The goal: keep teams in control of their data while still benefiting from strong LLM reasoning.

# What it does
Siamese (Living System Debugger) lets you upload incident artifacts—logs, metrics CSVs, configs, and diagrams: ask a natural-language question, and get a validated JSON incident report with summary, timeline, evidence, likely root cause, recommended fixes, and missing information. The UI renders the analysis and lets you download the raw JSON.

# How we built it
We built a Streamlit UI on top of a modular Python backend. Artifacts are ingested and compacted into context (logs with head/tail line numbers, metrics anomaly windows, configs capped to 400 lines). The app sends a structured prompt to the selected Gemini models, enforces JSON output, validates it with Pydantic, and saves all run artifacts locally.

# Challenges we ran into
- Model availability and rate limits required robust provider toggling and clear error handling.
- Enforcing valid JSON across different providers needed a repair retry strategy and strict schema validation.
- Balancing context detail with token limits while keeping evidence traceable.

# Accomplishments that we're proud of
- Local-first workflow with transparent run artifacts and deterministic ingest.
- Strict schema validation and automatic JSON repair for reliability.
- Clean UX that stays focused on the incident analysis workflow.

# What we learned
- Provider differences matter; consistent output needs defensive parsing and retries.
- Small ingestion choices (line numbers, anomaly windows) greatly improve evidence quality.
- A simple, focused UI beats a complex dashboard for incident debugging.

# What's next for Siamese
- Add richer metrics analysis (correlations, change-point detection).
- Support additional artifact types (traces, k8s events).
- Team workflows: comparisons across incidents and shared run history.