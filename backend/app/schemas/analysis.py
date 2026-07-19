from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class StepRecommendation(BaseModel):
    step: str
    recommendation: str
    rationale: str
    confidence: int


class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    automation_readiness: int
    ai_confidence: int
    risk_level: str
    summary: str | None = None
    analysis_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
