from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.questionnaire import get_questionnaire
from app.db.session import get_db
from app.deps import get_current_client_user
from app.models.assessment import Assessment
from app.models.assessment_response import AssessmentResponse
from app.models.classification_result import ClassificationResult
from app.models.domain import Domain
from app.models.roi_input import RoiInput
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentResultRead,
    ClassificationResultRead,
    ClientAssessmentListItem,
    ResponsesSubmit,
    RoiInputCreate,
    RoiResult,
)
from app.services.assessment_classification_service import ClassificationError, classify_assessment
from app.services.assessment_report_service import generate_assessment_report
from app.services.assessment_result_service import build_assessment_result
from app.services.readiness_scoring_service import compute_scores
from app.services.roi_calculator import compute_roi

router = APIRouter()

# Used only when Groq is unavailable and the KB use-case match has to degrade gracefully -
# maps the new 4-tier recommendation onto the older pure_rpa/rpa_ai/rpa_ui category so the
# ROI calculator (which still keys off category+complexity) always has a valid value.
_FALLBACK_CATEGORY = {
    "Manual Process": "pure_rpa",
    "RPA": "pure_rpa",
    "RPA + Native UiPath AI": "rpa_ai",
    "RPA + External AI": "rpa_ai",
}


def _get_assessment_or_404(db: Session, assessment_id: int, client_id: int) -> Assessment:
    assessment = db.execute(
        select(Assessment).where(Assessment.id == assessment_id, Assessment.client_id == client_id)
    ).scalar_one_or_none()
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


def _get_domain_or_404(db: Session, domain_id: int) -> Domain:
    domain = db.get(Domain, domain_id)
    if domain is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> AssessmentRead:
    _get_domain_or_404(db, payload.domain_id)
    assessment = Assessment(
        client_id=current_user.id,
        domain_id=payload.domain_id,
        business_context=payload.business_context,
        status="in_progress",
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return AssessmentRead.model_validate(assessment)


@router.get("", response_model=list[ClientAssessmentListItem])
def list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> list[ClientAssessmentListItem]:
    rows = db.execute(
        select(Assessment, Domain, ClassificationResult)
        .join(Domain, Domain.id == Assessment.domain_id)
        .outerjoin(ClassificationResult, ClassificationResult.assessment_id == Assessment.id)
        .where(Assessment.client_id == current_user.id)
        .order_by(Assessment.created_at.desc())
    ).all()

    return [
        ClientAssessmentListItem(
            id=assessment.id,
            domain=domain.name,
            status=assessment.status,
            created_at=assessment.created_at,
            completed_at=assessment.completed_at,
            category=classification.category if classification else None,
            matched_use_case=classification.matched_use_case if classification else None,
            confidence_score=classification.confidence_score if classification else None,
        )
        for assessment, domain, classification in rows
    ]


@router.post("/{assessment_id}/responses")
def submit_responses(
    assessment_id: int,
    payload: ResponsesSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> dict[str, int]:
    assessment = _get_assessment_or_404(db, assessment_id, current_user.id)

    existing = db.execute(
        select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment.id)
    ).scalars().all()
    for row in existing:
        db.delete(row)
    db.flush()

    for item in payload.responses:
        db.add(AssessmentResponse(assessment_id=assessment.id, question_key=item.question_key, response=item.response))

    db.commit()
    return {"saved": len(payload.responses)}


@router.post("/{assessment_id}/classify", response_model=ClassificationResultRead)
def classify(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> ClassificationResultRead:
    assessment = _get_assessment_or_404(db, assessment_id, current_user.id)
    domain = _get_domain_or_404(db, assessment.domain_id)

    questions = get_questionnaire(domain.name)
    responses = db.execute(
        select(AssessmentResponse).where(AssessmentResponse.assessment_id == assessment.id)
    ).scalars().all()
    responses_by_question = {response.question_key: response.response for response in responses}

    # Deterministic scoring never depends on Groq/network - compute it first so it always
    # succeeds, then best-effort attempt the Groq-based use-case match on top of it.
    scores = compute_scores(domain=domain.name, answers=responses_by_question)

    try:
        result = classify_assessment(
            domain=domain.name,
            business_context=assessment.business_context or {},
            questions=questions,
            responses_by_question=responses_by_question,
        )
    except ClassificationError as exc:
        result = {
            "category": _FALLBACK_CATEGORY.get(scores["recommendation"], "pure_rpa"),
            "matched_use_case": "Not available - AI use-case matching requires GROQ_API_KEY",
            "confidence_score": 0,
            "reasoning": [f"AI-powered use-case matching is unavailable: {exc}"],
            "similar_use_cases": [],
            "complexity": "medium",
            "estimated_timeline": "TBD",
        }

    existing_result = db.execute(
        select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
    ).scalar_one_or_none()
    if existing_result is not None:
        db.delete(existing_result)
        db.flush()

    classification = ClassificationResult(
        assessment_id=assessment.id,
        category=result["category"],
        matched_use_case=result["matched_use_case"],
        confidence_score=float(result["confidence_score"]),
        reasoning=result["reasoning"],
        similar_use_cases=result["similar_use_cases"],
        complexity=result["complexity"],
        estimated_timeline=result["estimated_timeline"],
        ai_readiness_score=scores["ai_readiness_score"],
        automation_maturity_score=scores["automation_maturity_score"],
        migration_readiness_score=scores["migration_readiness_score"],
        recommendation=scores["recommendation"],
        business_justification=scores["business_justification"],
        roi_estimate=scores["roi_estimate"],
    )
    db.add(classification)
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(classification)
    return ClassificationResultRead.model_validate(classification)


@router.get("/{assessment_id}/result", response_model=AssessmentResultRead)
def get_result(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> AssessmentResultRead:
    assessment = _get_assessment_or_404(db, assessment_id, current_user.id)
    return build_assessment_result(db, assessment)


@router.post("/{assessment_id}/roi", response_model=RoiResult)
def save_roi(
    assessment_id: int,
    payload: RoiInputCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> RoiResult:
    assessment = _get_assessment_or_404(db, assessment_id, current_user.id)
    classification = db.execute(
        select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
    ).scalar_one_or_none()
    if classification is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment has not been classified yet")

    roi_input_row = db.execute(
        select(RoiInput).where(RoiInput.assessment_id == assessment.id)
    ).scalar_one_or_none()
    if roi_input_row is None:
        roi_input_row = RoiInput(assessment_id=assessment.id)
        db.add(roi_input_row)

    roi_input_row.volume_per_month = payload.volume_per_month
    roi_input_row.team_size = payload.team_size
    roi_input_row.avg_fte_cost = payload.avg_fte_cost
    roi_input_row.currency = payload.currency
    db.commit()
    db.refresh(roi_input_row)

    return RoiResult(
        **compute_roi(
            category=classification.category,
            complexity=classification.complexity,
            volume_per_month=roi_input_row.volume_per_month,
            team_size=roi_input_row.team_size,
            avg_fte_cost=roi_input_row.avg_fte_cost,
            currency=roi_input_row.currency,
        )
    )


@router.get("/{assessment_id}/report.pdf")
def download_report(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> FileResponse:
    assessment = _get_assessment_or_404(db, assessment_id, current_user.id)
    result = build_assessment_result(db, assessment)
    if result.classification is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment has not been classified yet")

    report_path = generate_assessment_report(assessment, result)
    return FileResponse(path=str(report_path), filename=Path(report_path).name, media_type="application/pdf")
