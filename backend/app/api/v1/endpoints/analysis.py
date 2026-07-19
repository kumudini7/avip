from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import ProcessAnalysis
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.user import User
from app.models.workflow_job import WorkflowJob
from app.schemas.analysis import AnalysisRead
from app.schemas.job import WorkflowJobRead
from app.tasks.workflows import process_analysis_job
from app.services.workflow_service import build_analysis_payload


router = APIRouter()


def _get_project_or_404(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.execute(
        select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _latest_analysis(db: Session, project_id: int) -> ProcessAnalysis | None:
    return db.execute(
        select(ProcessAnalysis)
        .where(ProcessAnalysis.project_id == project_id)
        .order_by(ProcessAnalysis.updated_at.desc())
    ).scalars().first()


def _latest_job(db: Session, project_id: int) -> WorkflowJob | None:
    return db.execute(
        select(WorkflowJob)
        .where(WorkflowJob.project_id == project_id, WorkflowJob.job_type == "analysis")
        .order_by(WorkflowJob.created_at.desc())
    ).scalars().first()


@router.get("/{project_id}/analysis", response_model=AnalysisRead)
def get_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisRead:
    _get_project_or_404(db, project_id, current_user.id)
    analysis = _latest_analysis(db, project_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    return AnalysisRead.model_validate(analysis)


@router.post("/{project_id}/analysis", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
def run_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisRead:
    project = _get_project_or_404(db, project_id, current_user.id)
    documents = db.execute(
        select(ProcessDocument).where(ProcessDocument.project_id == project_id).order_by(ProcessDocument.created_at.desc())
    ).scalars().all()

    analysis_payload = build_analysis_payload(project, documents)
    existing = _latest_analysis(db, project_id)
    if existing is None:
        analysis = ProcessAnalysis(
            project_id=project_id,
            automation_readiness=analysis_payload["automation_readiness"],
            ai_confidence=analysis_payload["ai_confidence"],
            risk_level=analysis_payload["risk_level"],
            summary=analysis_payload["summary"],
            analysis_json=analysis_payload,
        )
        db.add(analysis)
    else:
        existing.automation_readiness = analysis_payload["automation_readiness"]
        existing.ai_confidence = analysis_payload["ai_confidence"]
        existing.risk_level = analysis_payload["risk_level"]
        existing.summary = analysis_payload["summary"]
        existing.analysis_json = analysis_payload
        analysis = existing
    db.commit()
    db.refresh(analysis)
    return AnalysisRead.model_validate(analysis)


@router.get("/{project_id}/analysis/jobs", response_model=list[WorkflowJobRead])
def list_analysis_jobs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkflowJobRead]:
    _get_project_or_404(db, project_id, current_user.id)
    jobs = db.execute(
        select(WorkflowJob)
        .where(
            WorkflowJob.project_id == project_id,
            WorkflowJob.job_type == "analysis",
            WorkflowJob.status != "queued",
        )
        .order_by(WorkflowJob.created_at.desc())
    ).scalars().all()
    return [WorkflowJobRead.model_validate(job) for job in jobs]


@router.post("/{project_id}/analysis/jobs", response_model=WorkflowJobRead, status_code=status.HTTP_201_CREATED)
def enqueue_analysis(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowJobRead:
    _get_project_or_404(db, project_id, current_user.id)
    job = WorkflowJob(
        project_id=project_id,
        job_type="analysis",
        status="queued",
        payload_json={"mode": "background"},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job.task_id = f"local-{job.id}"
    db.commit()
    db.refresh(job)
    process_analysis_job(project_id=project_id, job_id=job.id)
    db.refresh(job)
    return WorkflowJobRead.model_validate(job)


@router.get("/{project_id}/analysis/jobs/{job_id}", response_model=WorkflowJobRead)
def get_analysis_job(
    project_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowJobRead:
    _get_project_or_404(db, project_id, current_user.id)
    job = db.execute(
        select(WorkflowJob).where(
            WorkflowJob.id == job_id,
            WorkflowJob.project_id == project_id,
            WorkflowJob.job_type == "analysis",
        )
    ).scalars().first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis job not found")
    return WorkflowJobRead.model_validate(job)
