from __future__ import annotations

from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, index=True
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    matched_use_case: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[list | None] = mapped_column(JSON, nullable=True)
    similar_use_cases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    complexity: Mapped[str] = mapped_column(String(20), nullable=False)
    estimated_timeline: Mapped[str] = mapped_column(String(60), nullable=False)

    ai_readiness_score: Mapped[int | None] = mapped_column(Float, nullable=True)
    automation_maturity_score: Mapped[int | None] = mapped_column(Float, nullable=True)
    migration_readiness_score: Mapped[int | None] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(40), nullable=True)
    business_justification: Mapped[list | None] = mapped_column(JSON, nullable=True)
    roi_estimate: Mapped[str | None] = mapped_column(Text, nullable=True)
