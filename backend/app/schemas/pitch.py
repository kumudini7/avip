from __future__ import annotations

from pydantic import BaseModel


class PitchGenerateRequest(BaseModel):
    industry: str
    pain_points: list[str]


class PitchKpiTemplateItem(BaseModel):
    kpi: str
    baseline: str
    target: str


class PitchGeneratedContent(BaseModel):
    as_is: list[str]
    to_be: list[str]
    kpi_template: list[PitchKpiTemplateItem]


class PitchGenerateResponse(BaseModel):
    content: PitchGeneratedContent
    model: str | None = None
