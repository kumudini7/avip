from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ActivityEntry(Base):
    __tablename__ = "activity_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    engagement_id: Mapped[int] = mapped_column(ForeignKey("engagements.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    engagement: Mapped["Engagement"] = relationship("Engagement", back_populates="activities")
