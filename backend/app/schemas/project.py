from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    client_name: str | None = None
    industry: str | None = None
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    client_name: str | None = None
    industry: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    status: str
    created_at: datetime
    updated_at: datetime


class ProjectOverviewRead(ProjectRead):
    document_count: int = 0
    has_analysis: bool = False
    has_proposal: bool = False
    automation_readiness: int | None = None
    ai_confidence: int | None = None
    risk_level: str | None = None
    benchmark_automation: int | None = None
    benchmark_roi: int | None = None
    payback: str | None = None
    latest_analysis_id: int | None = None
    latest_proposal_id: int | None = None
