from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    documents: Mapped[list["ProcessDocument"]] = relationship(
        "ProcessDocument",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    analyses: Mapped[list["ProcessAnalysis"]] = relationship(
        "ProcessAnalysis",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[list["WorkflowJob"]] = relationship(
        "WorkflowJob",
        cascade="all, delete-orphan",
    )
    proposals: Mapped[list["Proposal"]] = relationship(
        "Proposal",
        back_populates="project",
        cascade="all, delete-orphan",
    )
