from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class EngagementCreate(BaseModel):
    client_name: str
    industry: str
    stage: str = "discovery"
    health: str = "on_track"
    started_at: date | None = None
    roi_value: float | None = None


class EngagementUpdate(BaseModel):
    client_name: str | None = None
    industry: str | None = None
    stage: str | None = None
    health: str | None = None
    closed_at: date | None = None
    roi_value: float | None = None


class EngagementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    client_name: str
    industry: str
    stage: str
    health: str
    started_at: date
    closed_at: date | None = None
    roi_value: float | None = None
    created_at: datetime
    updated_at: datetime
    owner_name: str | None = None


class EngagementKpiCreate(BaseModel):
    label: str
    baseline_value: str
    target_value: str
    current_value: str | None = None
    progress: int = Field(default=0, ge=0, le=100)


class EngagementKpiUpdate(BaseModel):
    label: str | None = None
    baseline_value: str | None = None
    target_value: str | None = None
    current_value: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)


class EngagementKpiRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    engagement_id: int
    label: str
    baseline_value: str
    target_value: str
    current_value: str | None = None
    progress: int
    created_at: datetime
    updated_at: datetime


class ApproachStep(BaseModel):
    step: str
    detail: str


class StageTool(BaseModel):
    name: str
    description: str


class StageGeneratedContent(BaseModel):
    objective: str
    client_value: str
    approach: list[ApproachStep]
    tools: list[StageTool]
    pitch_line: str
    checklist: list[str]


class StageStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    engagement_id: int
    stage: str
    checklist_json: list[bool]
    notes: str | None = None
    generated_content: StageGeneratedContent | None = None
    content_generated_at: datetime | None = None
    content_model: str | None = None
    updated_at: datetime


class StageStateUpdate(BaseModel):
    checklist_json: list[bool]
    notes: str | None = None


class StageGenerationResult(BaseModel):
    stage: str
    status: str
    error: str | None = None


class PlaybookGenerationResponse(BaseModel):
    results: list[StageGenerationResult]
