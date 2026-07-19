from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data.questionnaire import get_questionnaire
from app.db.session import get_db
from app.deps import get_current_client_user
from app.models.domain import Domain
from app.models.user import User
from app.schemas.assessment import QuestionnaireQuestion

router = APIRouter()


@router.get("/for-assessment", response_model=list[QuestionnaireQuestion])
def get_questions_for_assessment(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_client_user),
) -> list[QuestionnaireQuestion]:
    domain = db.get(Domain, domain_id)
    if domain is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return [QuestionnaireQuestion(**question) for question in get_questionnaire(domain.name)]
