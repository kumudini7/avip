from __future__ import annotations

from fastapi import APIRouter, Depends

from app.data.use_cases import USE_CASES
from app.deps import get_current_user
from app.models.user import User
from app.schemas.use_case import UseCaseRead

router = APIRouter()


@router.get("", response_model=list[UseCaseRead])
def list_use_cases(current_user: User = Depends(get_current_user)) -> list[UseCaseRead]:
    return [UseCaseRead.model_validate(entry) for entry in USE_CASES]
