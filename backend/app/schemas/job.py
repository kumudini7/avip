from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowJobCreate(BaseModel):
    job_type: str
    payload_json: dict[str, Any] = Field(default_factory=dict)


class WorkflowJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    job_type: str
    status: str
    task_id: str | None = None
    payload_json: dict[str, Any]
    result_json: dict[str, Any]
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WorkflowJobListResponse(BaseModel):
    items: list[WorkflowJobRead]
