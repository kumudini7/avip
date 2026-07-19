from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    original_filename: str
    display_name: str | None = None
    stored_filename: str
    mime_type: str | None = None
    storage_path: str
    extracted_text: str | None = None
    file_size: int | None = None
    created_at: datetime


class DocumentUpdate(BaseModel):
    display_name: str | None = None
