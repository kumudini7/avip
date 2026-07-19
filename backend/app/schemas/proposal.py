from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    status: str
    executive_summary: str | None = None
    proposal_json: dict[str, Any]
    pdf_path: str | None = None
    ppt_path: str | None = None
    created_at: datetime
    updated_at: datetime
