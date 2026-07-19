from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"), index=True)
    question_key: Mapped[str] = mapped_column(String(60), index=True)
    response: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
