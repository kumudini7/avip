from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import ProcessAnalysis
from app.models.proposal_artifact import ProposalArtifact
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.user import User
from app.models.workflow_job import WorkflowJob
from app.schemas.artifact import ProposalArtifactRead
from app.schemas.job import WorkflowJobRead
from app.schemas.proposal import ProposalRead
from app.schemas.proposal_preview import ProposalPreviewRead
from app.tasks.workflows import process_proposal_job
from app.services.workflow_service import build_proposal_payload


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


def _latest_proposal(db: Session, project_id: int) -> Proposal | None:
    return db.execute(
        select(Proposal).where(Proposal.project_id == project_id).order_by(Proposal.updated_at.desc())
    ).scalars().first()


def _latest_proposal_job(db: Session, project_id: int) -> WorkflowJob | None:
    return db.execute(
        select(WorkflowJob)
        .where(WorkflowJob.project_id == project_id, WorkflowJob.job_type == "proposal")
        .order_by(WorkflowJob.created_at.desc())
    ).scalars().first()


def _proposal_artifacts(db: Session, proposal_id: int) -> list[ProposalArtifact]:
    return db.execute(
        select(ProposalArtifact).where(ProposalArtifact.proposal_id == proposal_id).order_by(ProposalArtifact.created_at.desc())
    ).scalars().all()


def _latest_analysis_payload(db: Session, project_id: int) -> dict | None:
    analysis = _latest_analysis(db, project_id)
    return analysis.analysis_json if analysis else None


def _persist_artifacts(db: Session, proposal: Proposal, proposal_payload: dict, job_id: int | None = None) -> None:
    proposal.status = "ready"
    proposal.executive_summary = proposal_payload["executive_summary"]
    proposal.proposal_json = proposal_payload
    proposal.pdf_path = proposal_payload["files"]["pdf"]
    proposal.ppt_path = proposal_payload["files"]["pptx"]

    artifact_specs = [
        ("pdf", proposal.pdf_path),
        ("pptx", proposal.ppt_path),
    ]
    for artifact_type, file_path in artifact_specs:
        artifact = ProposalArtifact(
            proposal_id=proposal.id,
            job_id=job_id,
            artifact_type=artifact_type,
            status="completed",
            file_path=file_path,
            file_name=Path(file_path).name if file_path else None,
            generated_at=datetime.utcnow(),
        )
        db.add(artifact)


@router.get("/{project_id}/proposal", response_model=ProposalRead)
def get_proposal(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProposalRead:
    _get_project_or_404(db, project_id, current_user.id)
    proposal = _latest_proposal(db, project_id)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return ProposalRead.model_validate(proposal)


@router.post("/{project_id}/proposal", response_model=ProposalRead, status_code=status.HTTP_201_CREATED)
def generate_proposal(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProposalRead:
    project = _get_project_or_404(db, project_id, current_user.id)
    analysis = _latest_analysis(db, project_id)
    if analysis is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Run analysis before generating a proposal")

    proposal_payload = build_proposal_payload(project, analysis.analysis_json)
    proposal = _latest_proposal(db, project_id)
    if proposal is None:
        proposal = Proposal(
            project_id=project_id,
            title=f"{project.name} Proposal",
            status="processing",
            executive_summary=None,
            proposal_json={},
        )
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
    else:
        proposal.title = f"{project.name} Proposal"
        proposal.status = "processing"
    db.commit()
    _persist_artifacts(db, proposal, proposal_payload, job_id=None)
    db.commit()
    db.refresh(proposal)
    return ProposalRead.model_validate(proposal)


@router.get("/{project_id}/proposal/preview", response_model=ProposalPreviewRead)
def proposal_preview(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProposalPreviewRead:
    _get_project_or_404(db, project_id, current_user.id)
    proposal = _latest_proposal(db, project_id)
    artifacts = _proposal_artifacts(db, proposal.id) if proposal else []
    jobs = db.execute(
        select(WorkflowJob)
        .where(WorkflowJob.project_id == project_id, WorkflowJob.status != "queued")
        .order_by(WorkflowJob.created_at.desc())
    ).scalars().all()

    export_status = "pending"
    if proposal is not None:
        export_status = proposal.status
    elif jobs:
        export_status = jobs[0].status

    export_history = [
        {
            "artifact_type": artifact.artifact_type,
            "status": artifact.status,
            "file_name": artifact.file_name,
            "generated_at": artifact.generated_at.isoformat() if artifact.generated_at else None,
            "file_path": artifact.file_path,
        }
        for artifact in artifacts
    ]

    return ProposalPreviewRead(
        proposal=ProposalRead.model_validate(proposal) if proposal else None,
        artifacts=[ProposalArtifactRead.model_validate(item) for item in artifacts],
        jobs=[WorkflowJobRead.model_validate(job) for job in jobs],
        export_status=export_status,
        export_history=export_history,
    )


@router.get("/{project_id}/proposal/history", response_model=list[ProposalArtifactRead])
def proposal_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProposalArtifactRead]:
    _get_project_or_404(db, project_id, current_user.id)
    proposal = _latest_proposal(db, project_id)
    if proposal is None:
        return []
    artifacts = _proposal_artifacts(db, proposal.id)
    return [ProposalArtifactRead.model_validate(item) for item in artifacts]


@router.post("/{project_id}/proposal/jobs", response_model=WorkflowJobRead, status_code=status.HTTP_201_CREATED)
def enqueue_proposal(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkflowJobRead:
    _get_project_or_404(db, project_id, current_user.id)
    job = WorkflowJob(
        project_id=project_id,
        job_type="proposal",
        status="queued",
        payload_json={"mode": "background"},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job.task_id = f"local-{job.id}"
    db.commit()
    db.refresh(job)
    process_proposal_job(project_id=project_id, job_id=job.id)
    db.refresh(job)
    return WorkflowJobRead.model_validate(job)


@router.get("/{project_id}/proposal/jobs", response_model=list[WorkflowJobRead])
def list_proposal_jobs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WorkflowJobRead]:
    _get_project_or_404(db, project_id, current_user.id)
    jobs = db.execute(
        select(WorkflowJob)
        .where(
            WorkflowJob.project_id == project_id,
            WorkflowJob.job_type == "proposal",
            WorkflowJob.status != "queued",
        )
        .order_by(WorkflowJob.created_at.desc())
    ).scalars().all()
    return [WorkflowJobRead.model_validate(job) for job in jobs]


@router.get("/{project_id}/proposal/jobs/{job_id}", response_model=WorkflowJobRead)
def get_proposal_job(
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
            WorkflowJob.job_type == "proposal",
        )
    ).scalars().first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal job not found")
    return WorkflowJobRead.model_validate(job)


@router.get("/{project_id}/proposal/download/pdf")
def download_pdf(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    proposal = _latest_proposal(db, project_id)
    if proposal is None or not proposal.pdf_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")
    return FileResponse(
        path=proposal.pdf_path,
        filename=Path(proposal.pdf_path).name,
        media_type="application/pdf",
    )


@router.get("/{project_id}/proposal/download/pptx")
def download_pptx(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    proposal = _latest_proposal(db, project_id)
    if proposal is None or not proposal.ppt_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PPTX not found")
    return FileResponse(
        path=proposal.ppt_path,
        filename=Path(proposal.ppt_path).name,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
