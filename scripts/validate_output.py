from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic import ValidationError

from app.schemas import IncidentAnalysis


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate incident analysis JSON.")
    parser.add_argument("json_path", help="Path to JSON file")
    args = parser.parse_args()

    path = Path(args.json_path)
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        IncidentAnalysis.model_validate(data)
    except ValidationError as exc:
        print("Invalid JSON schema:")
        print(str(exc))
        return 1

    print("Valid incident analysis JSON.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
