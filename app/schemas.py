from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class IncidentAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    timeline: list[str]
    evidence: list[str]
    likely_root_cause: str
    recommended_fixes: list[str]
    missing_information: list[str]
