from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.project import ProjectOverviewRead


class DemoDashboardRead(BaseModel):
    projects: list[ProjectOverviewRead] = Field(default_factory=list)
    total_projects: int = 0
    analyzed_projects: int = 0
    average_readiness: int = 0
    average_confidence: int = 0
    average_benchmark_readiness: int = 0
    featured_process: str | None = None

