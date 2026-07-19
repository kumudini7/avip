from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProposalArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    job_id: int | None = None
    artifact_type: str
    status: str
    file_path: str | None = None
    file_name: str | None = None
    error_message: str | None = None
    generated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

