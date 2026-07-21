from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.use_cases import find_use_case
from app.models.assessment import Assessment
from app.models.assessment_response import AssessmentResponse
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
from app.services.final_scorecard_service import compute_final_scorecard
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

        # Recomputed live (not persisted) so it always reflects the latest
        # questionnaire answers and ROI inputs, the same way `roi` above is
        # computed fresh on every fetch rather than cached at classify time.
        if classification.recommendation is not None:
            responses = db.execute(
                select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment.id)
            ).scalars().all()
            answers = {response.question_key: response.response for response in responses}
            dashboard_metrics = compute_final_scorecard(
                answers=answers,
                category=classification.category,
                recommendation=classification.recommendation,
                matched_use_case=classification.matched_use_case,
                automation_maturity_score=classification.automation_maturity_score or 50,
                roi=roi.model_dump() if roi is not None else None,
            )
            classification_read = classification_read.model_copy(update={"dashboard_metrics": dashboard_metrics})

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
