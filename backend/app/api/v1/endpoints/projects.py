from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import ProcessAnalysis
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOverviewRead, ProjectRead, ProjectUpdate
from app.core.config import settings


router = APIRouter()


def _get_project_or_404(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectRead]:
    projects = db.execute(
        select(Project).where(Project.owner_id == current_user.id).order_by(Project.created_at.desc())
    ).scalars().all()
    return [ProjectRead.model_validate(project) for project in projects]


@router.get("/overview", response_model=list[ProjectOverviewRead])
def project_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectOverviewRead]:
    projects = db.execute(
        select(Project).where(Project.owner_id == current_user.id).order_by(Project.updated_at.desc())
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


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        client_name=payload.client_name,
        industry=payload.industry,
        description=payload.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = _get_project_or_404(db, project_id, current_user.id)
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRead:
    project = _get_project_or_404(db, project_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(project)


@router.delete(
    "/{project_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project = _get_project_or_404(db, project_id, current_user.id)
    db.delete(project)
    db.commit()
    for base_dir in (settings.upload_dir, settings.report_dir):
        project_dir = Path(base_dir) / f"project_{project_id}"
        if project_dir.exists():
            shutil.rmtree(project_dir, ignore_errors=True)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
