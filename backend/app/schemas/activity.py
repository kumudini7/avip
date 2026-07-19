from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    engagement_id: int
    type: str
    text: str
    created_at: datetime
    client_name: str | None = None
    author: str | None = None
