from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.artifact import ProposalArtifactRead
from app.schemas.proposal import ProposalRead
from app.schemas.job import WorkflowJobRead


class ProposalPreviewRead(BaseModel):
    proposal: ProposalRead | None = None
    artifacts: list[ProposalArtifactRead] = Field(default_factory=list)
    jobs: list[WorkflowJobRead] = Field(default_factory=list)
    export_status: str = "pending"
    export_history: list[dict[str, Any]] = Field(default_factory=list)
