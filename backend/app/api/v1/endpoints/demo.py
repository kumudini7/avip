from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.analysis import ProcessAnalysis
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.user import User
from app.schemas.demo import DemoDashboardRead
from app.schemas.project import ProjectOverviewRead, ProjectRead


router = APIRouter()


def _build_overview(db: Session, user_id: int) -> list[ProjectOverviewRead]:
    projects = db.execute(
        select(Project).where(Project.owner_id == user_id).order_by(Project.updated_at.desc())
    ).scalars().all()

    overview: list[ProjectOverviewRead] = []
    for project in projects:
        document_count = db.execute(
            select(func.count(ProcessDocument.id)).where(ProcessDocument.project_id == project.id)
        ).scalar_one()
        latest_analysis = db.execute(
            select(ProcessAnalysis).where(ProcessAnalysis.project_id == project.id).order_by(ProcessAnalysis.updated_at.desc())
        ).scalars().first()
        latest_proposal = db.execute(
            select(Proposal).where(Proposal.project_id == project.id).order_by(Proposal.updated_at.desc())
        ).scalars().first()
        benchmark = (latest_analysis.analysis_json.get("benchmark") if latest_analysis and latest_analysis.analysis_json else {}) or {}
        overview.append(
            ProjectOverviewRead(
                **ProjectRead.model_validate(project).model_dump(),
                document_count=document_count,
                has_analysis=latest_analysis is not None,
                has_proposal=latest_proposal is not None,
                automation_readiness=latest_analysis.automation_readiness if latest_analysis else None,
                ai_confidence=latest_analysis.ai_confidence if latest_analysis else None,
                risk_level=latest_analysis.risk_level if latest_analysis else None,
                benchmark_automation=benchmark.get("automation"),
                benchmark_roi=benchmark.get("roi"),
                payback=benchmark.get("payback"),
                latest_analysis_id=latest_analysis.id if latest_analysis else None,
                latest_proposal_id=latest_proposal.id if latest_proposal else None,
            )
        )
    return overview


@router.get("/dashboard", response_model=DemoDashboardRead)
def demo_dashboard(db: Session = Depends(get_db)) -> DemoDashboardRead:
    demo_user = db.execute(select(User).where(User.email == settings.demo_user_email)).scalar_one_or_none()
    if demo_user is None:
        return DemoDashboardRead(featured_process="Demo data will appear after startup seeding.")

    projects = _build_overview(db, demo_user.id)
    analyzed_projects = [item for item in projects if item.has_analysis]
    average_readiness = round(
        sum(item.automation_readiness or 0 for item in analyzed_projects) / len(analyzed_projects)
    ) if analyzed_projects else 0
    average_confidence = round(
        sum(item.ai_confidence or 0 for item in analyzed_projects) / len(analyzed_projects)
    ) if analyzed_projects else 0
    average_benchmark = round(
        sum(item.benchmark_automation or 0 for item in analyzed_projects) / len(analyzed_projects)
    ) if analyzed_projects else 0

    featured_process = projects[0].name if projects else None
    return DemoDashboardRead(
        projects=projects,
        total_projects=len(projects),
        analyzed_projects=len(analyzed_projects),
        average_readiness=average_readiness,
        average_confidence=average_confidence,
        average_benchmark_readiness=average_benchmark,
        featured_process=featured_process,
    )

