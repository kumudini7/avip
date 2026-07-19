from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.use_cases import find_use_case
from app.models.assessment import Assessment
from app.models.classification_result import ClassificationResult
from app.models.domain import Domain
from app.models.roi_input import RoiInput
from app.schemas.assessment import (
    AssessmentResultRead,
    ClassificationResultRead,
    RoiInputRead,
    RoiResult,
    UseCaseDetail,
)
from app.services.roi_calculator import compute_roi


def build_assessment_result(db: Session, assessment: Assessment) -> AssessmentResultRead:
    domain = db.get(Domain, assessment.domain_id)
    classification = db.execute(
        select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
    ).scalar_one_or_none()
    roi_input_row = db.execute(
        select(RoiInput).where(RoiInput.assessment_id == assessment.id)
    ).scalar_one_or_none()

    classification_read: ClassificationResultRead | None = None
    use_case: UseCaseDetail | None = None
    roi: RoiResult | None = None

    if classification is not None:
        classification_read = ClassificationResultRead.model_validate(classification)
        domain_name = domain.name if domain else ""
        kb_entry = find_use_case(domain_name, classification.category, classification.matched_use_case)
        if kb_entry is not None:
            use_case = UseCaseDetail(
                domain=kb_entry["domain"],
                category=kb_entry["category"],
                title=kb_entry["title"],
                overview=kb_entry["overview"],
                process_flow=kb_entry["process_flow"],
                systems_involved=kb_entry["systems_involved"],
                roi_benchmarks=kb_entry["roi_benchmarks"],
                value_props=kb_entry["value_props"],
                complexity=kb_entry["complexity"],
            )
        if roi_input_row is not None:
            roi = RoiResult(
                **compute_roi(
                    category=classification.category,
                    complexity=classification.complexity,
                    volume_per_month=roi_input_row.volume_per_month,
                    team_size=roi_input_row.team_size,
                    avg_fte_cost=roi_input_row.avg_fte_cost,
                    currency=roi_input_row.currency,
                )
            )

    return AssessmentResultRead(
        assessment_id=assessment.id,
        domain=domain.name if domain else "",
        status=assessment.status,
        business_context=assessment.business_context,
        classification=classification_read,
        use_case=use_case,
        roi_input=RoiInputRead.model_validate(roi_input_row) if roi_input_row is not None else None,
        roi=roi,
    )
