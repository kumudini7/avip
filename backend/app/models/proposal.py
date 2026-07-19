from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposal_json: Mapped[dict] = mapped_column(JSON, default=dict)
    pdf_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ppt_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="proposals")
    artifacts: Mapped[list["ProposalArtifact"]] = relationship(
        "ProposalArtifact",
        cascade="all, delete-orphan",
    )
