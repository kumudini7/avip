from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EngagementStageState(Base):
    __tablename__ = "engagement_stage_states"
    __table_args__ = (UniqueConstraint("engagement_id", "stage", name="uq_engagement_stage"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    checklist_json: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_content_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content_model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    engagement: Mapped["Engagement"] = relationship("Engagement", back_populates="stage_states")
