from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RoiInput(Base):
    __tablename__ = "roi_inputs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE"), unique=True, index=True
    )
    volume_per_month: Mapped[int] = mapped_column(Integer, nullable=False)
    team_size: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_fte_cost: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
