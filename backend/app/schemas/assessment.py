from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AssessmentCreate(BaseModel):
    domain_id: int
    business_context: dict[str, str]


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    domain_id: int
    status: str
    business_context: dict[str, Any] | None = None
    created_at: datetime
    completed_at: datetime | None = None


class ResponseItem(BaseModel):
    question_key: str
    response: Any


class ResponsesSubmit(BaseModel):
    responses: list[ResponseItem]


class QuestionnaireQuestion(BaseModel):
    key: str
    question_text: str
    scale_labels: dict[int, str]


class ClassificationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: Literal["pure_rpa", "rpa_ai", "rpa_ui"]
    matched_use_case: str
    confidence_score: float
    reasoning: list[str]
    similar_use_cases: list[str]
    complexity: Literal["low", "medium", "high"]
    estimated_timeline: str

    ai_readiness_score: float | None = None
    automation_maturity_score: float | None = None
    migration_readiness_score: float | None = None
    recommendation: (
        Literal["Manual Process", "RPA", "RPA + Native UiPath AI", "RPA + External AI"] | None
    ) = None
    business_justification: list[str] | None = None
    roi_estimate: str | None = None


class UseCaseDetail(BaseModel):
    domain: str
    category: str
    title: str
    overview: str
    process_flow: list[str]
    systems_involved: list[str]
    roi_benchmarks: dict[str, Any]
    value_props: list[str]
    complexity: str


class RoiInputCreate(BaseModel):
    volume_per_month: int = Field(ge=100, le=10000)
    team_size: int = Field(ge=1, le=50)
    avg_fte_cost: float = Field(gt=0)
    currency: Literal["INR", "USD"] = "INR"


class RoiInputRead(RoiInputCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: int


class RoiResult(BaseModel):
    currency: str
    current_annual_cost: float
    post_automation_cost: float
    implementation_cost: float
    year1_net_saving: float
    year2_saving: float
    payback_months: float | None
    chart_series: list[float]


class AssessmentResultRead(BaseModel):
    assessment_id: int
    domain: str
    status: str
    business_context: dict[str, Any] | None = None
    classification: ClassificationResultRead | None = None
    use_case: UseCaseDetail | None = None
    roi_input: RoiInputRead | None = None
    roi: RoiResult | None = None


class AdminAssessmentListItem(BaseModel):
    id: int
    client_name: str
    company: str | None = None
    domain: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    category: str | None = None
    matched_use_case: str | None = None


class ClientAssessmentListItem(BaseModel):
    id: int
    domain: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    category: str | None = None
    matched_use_case: str | None = None
    confidence_score: float | None = None
