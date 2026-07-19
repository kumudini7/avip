from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.domain import Domain
from app.models.user import User
from app.schemas.domain import DomainRead

router = APIRouter()


@router.get("", response_model=list[DomainRead])
def list_domains(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DomainRead]:
    domains = db.execute(select(Domain).order_by(Domain.name)).scalars().all()
    return [DomainRead.model_validate(domain) for domain in domains]
