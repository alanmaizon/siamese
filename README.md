# siamese

Local-first incident analysis. Upload logs and metrics, ask a question, and get a structured incident analysis validated by Pydantic and rendered in a clean Streamlit UI.

**Why Gemini 3 is essential**
Gemini 3 provides strong multi-document reasoning and structured output control, which lets the app produce consistent JSON incident reports from heterogeneous artifacts (logs, CSV metrics, configs, and optional diagrams). This project relies on Gemini 3 to synthesize evidence-backed root cause analysis across multiple data sources.

**Setup**
1. Create and activate a virtual environment (Python 3.11+).
2. Install dependencies.
3. Export your Gemini API key.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your_key_here"
# Optional: export GEMINI_MODEL="gemini-2.5-flash"
```

You can also create a `.env` file (based on `.env.example`) and the app will load it automatically.

**Run**
```bash
./scripts/run_streamlit.sh
```
Or:
```bash
streamlit run app/ui_streamlit.py
```

**How to use demo artifacts**
1. Place example files in `demo_artifacts/`.
2. Open the UI and upload those files.
3. Ask a question like one of the examples below.

**Example questions**
- Why did API latency spike after the most recent deployment?
- What caused the 5xx error rate to jump around 14:32 UTC?
- Is the database saturation related to the increase in cache misses?

**Troubleshooting**
- Missing key: If you see a missing key error, confirm `GEMINI_API_KEY` is set in your shell environment or in `.env`.
- Invalid JSON: The app attempts one automatic repair. If output is still invalid, the raw response is saved under `runs/<timestamp>/raw_output.txt` for inspection.

**Outputs**
Each analysis run saves:
- `runs/<timestamp>/inputs.json`
- `runs/<timestamp>/question.txt`
- `runs/<timestamp>/context.txt`
- `runs/<timestamp>/output.json` (if valid)
- `runs/<timestamp>/raw_output.txt`
