from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Engagement(Base):
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(120), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), default="discovery")
    health: Mapped[str] = mapped_column(String(32), default="on_track")
    started_at: Mapped[date] = mapped_column(Date, default=date.today)
    closed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    roi_value: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped["User"] = relationship("User")
    kpis: Mapped[list["EngagementKpi"]] = relationship(
        "EngagementKpi",
        back_populates="engagement",
        cascade="all, delete-orphan",
    )
    stage_states: Mapped[list["EngagementStageState"]] = relationship(
        "EngagementStageState",
        back_populates="engagement",
        cascade="all, delete-orphan",
    )
    activities: Mapped[list["ActivityEntry"]] = relationship(
        "ActivityEntry",
        back_populates="engagement",
        cascade="all, delete-orphan",
    )
