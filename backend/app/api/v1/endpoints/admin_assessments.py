from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_pre_sales_user
from app.models.assessment import Assessment
from app.models.classification_result import ClassificationResult
from app.models.domain import Domain
from app.models.user import User
from app.schemas.assessment import AdminAssessmentListItem, AssessmentResultRead
from app.services.assessment_result_service import build_assessment_result

router = APIRouter()


@router.get("/assessments", response_model=list[AdminAssessmentListItem])
def list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pre_sales_user),
) -> list[AdminAssessmentListItem]:
    assessments = db.execute(select(Assessment).order_by(Assessment.created_at.desc())).scalars().all()

    items: list[AdminAssessmentListItem] = []
    for assessment in assessments:
        client = db.get(User, assessment.client_id)
        domain = db.get(Domain, assessment.domain_id)
        classification = db.execute(
            select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
        ).scalar_one_or_none()
        items.append(
            AdminAssessmentListItem(
                id=assessment.id,
                client_name=(client.full_name or client.email) if client else "Unknown",
                company=client.company if client else None,
                domain=domain.name if domain else "Unknown",
                status=assessment.status,
                created_at=assessment.created_at,
                completed_at=assessment.completed_at,
                category=classification.category if classification else None,
                matched_use_case=classification.matched_use_case if classification else None,
            )
        )
    return items


@router.get("/assessments/{assessment_id}/result", response_model=AssessmentResultRead)
def admin_get_result(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_pre_sales_user),
) -> AssessmentResultRead:
    assessment = db.get(Assessment, assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return build_assessment_result(db, assessment)
