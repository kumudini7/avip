from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.core.roles import ROLE_CLIENT
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse
from app.schemas.user import UserCreate, UserLogin, UserRead


router = APIRouter()


def _auth_response(user: User) -> AuthResponse:
    token = create_access_token(subject=user.email)
    return AuthResponse(access_token=token, token_type="bearer", user=UserRead.model_validate(user))


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    existing_user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        company=payload.company,
        hashed_password=hash_password(payload.password),
        role=ROLE_CLIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return _auth_response(user)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
