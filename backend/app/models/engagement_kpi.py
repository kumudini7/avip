from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EngagementKpi(Base):
    __tablename__ = "engagement_kpis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    baseline_value: Mapped[str] = mapped_column(String(120), nullable=False)
    target_value: Mapped[str] = mapped_column(String(120), nullable=False)
    current_value: Mapped[str | None] = mapped_column(String(120), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    engagement: Mapped["Engagement"] = relationship("Engagement", back_populates="kpis")
