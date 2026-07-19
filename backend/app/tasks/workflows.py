from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.analysis import ProcessAnalysis
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.proposal_artifact import ProposalArtifact
from app.models.workflow_job import WorkflowJob
from app.services.workflow_service import build_analysis_payload, build_proposal_payload


def _set_job_status(db, job: WorkflowJob, status: str, result_json: dict | None = None, error_message: str | None = None) -> None:
    job.status = status
    if status == "running" and job.started_at is None:
        job.started_at = datetime.utcnow()
    if status in {"completed", "failed"}:
        job.completed_at = datetime.utcnow()
    if result_json is not None:
        job.result_json = result_json
    if error_message is not None:
        job.error_message = error_message
    db.commit()


def _get_project(db, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise ValueError("Project not found")
    return project


def process_analysis_job(project_id: int, job_id: int) -> dict:
    db = SessionLocal()
    try:
        job = db.query(WorkflowJob).filter(WorkflowJob.id == job_id, WorkflowJob.project_id == project_id).one()
        _set_job_status(db, job, "running")

        project = _get_project(db, project_id)
        documents = db.query(ProcessDocument).filter(ProcessDocument.project_id == project_id).order_by(ProcessDocument.created_at.desc()).all()
        analysis_payload = build_analysis_payload(project, documents)

        analysis = db.query(ProcessAnalysis).filter(ProcessAnalysis.project_id == project_id).one_or_none()
        if analysis is None:
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
            analysis.automation_readiness = analysis_payload["automation_readiness"]
            analysis.ai_confidence = analysis_payload["ai_confidence"]
            analysis.risk_level = analysis_payload["risk_level"]
            analysis.summary = analysis_payload["summary"]
            analysis.analysis_json = analysis_payload

        _set_job_status(db, job, "completed", result_json=analysis_payload)
        db.commit()
        db.refresh(analysis)
        return analysis_payload
    except Exception as exc:
        db.rollback()
        try:
            job = db.query(WorkflowJob).filter(WorkflowJob.id == job_id, WorkflowJob.project_id == project_id).one()
            _set_job_status(db, job, "failed", error_message=str(exc))
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()


def process_proposal_job(project_id: int, job_id: int) -> dict:
    db = SessionLocal()
    try:
        job = db.query(WorkflowJob).filter(WorkflowJob.id == job_id, WorkflowJob.project_id == project_id).one()
        _set_job_status(db, job, "running")

        project = _get_project(db, project_id)
        analysis = db.query(ProcessAnalysis).filter(ProcessAnalysis.project_id == project_id).order_by(ProcessAnalysis.updated_at.desc()).first()
        if analysis is None:
            documents = db.query(ProcessDocument).filter(ProcessDocument.project_id == project_id).order_by(ProcessDocument.created_at.desc()).all()
            analysis_payload = build_analysis_payload(project, documents)
            analysis = ProcessAnalysis(
                project_id=project_id,
                automation_readiness=analysis_payload["automation_readiness"],
                ai_confidence=analysis_payload["ai_confidence"],
                risk_level=analysis_payload["risk_level"],
                summary=analysis_payload["summary"],
                analysis_json=analysis_payload,
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

        proposal = db.query(Proposal).filter(Proposal.project_id == project_id).order_by(Proposal.updated_at.desc()).first()
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
            proposal.status = "processing"
            db.commit()
            db.refresh(proposal)

        proposal_payload = build_proposal_payload(project, analysis.analysis_json)
        proposal.title = f"{project.name} Proposal"
        proposal.status = "ready"
        proposal.executive_summary = proposal_payload["executive_summary"]
        proposal.proposal_json = proposal_payload
        proposal.pdf_path = proposal_payload["files"]["pdf"]
        proposal.ppt_path = proposal_payload["files"]["pptx"]

        artifacts = []
        for artifact_type, file_path in (("pdf", proposal.pdf_path), ("pptx", proposal.ppt_path)):
            artifact = ProposalArtifact(
                proposal_id=proposal.id,
                job_id=job.id,
                artifact_type=artifact_type,
                status="completed",
                file_path=file_path,
                file_name=Path(file_path).name if file_path else None,
                generated_at=datetime.utcnow(),
            )
            db.add(artifact)
            artifacts.append(artifact)

        _set_job_status(db, job, "completed", result_json={**proposal_payload, "artifacts": [artifact.file_path for artifact in artifacts]})
        db.commit()
        db.refresh(proposal)
        return proposal_payload
    except Exception as exc:
        db.rollback()
        try:
            job = db.query(WorkflowJob).filter(WorkflowJob.id == job_id, WorkflowJob.project_id == project_id).one()
            _set_job_status(db, job, "failed", error_message=str(exc))
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="avip.analyze_project")
def analyze_project_job(project_id: int, job_id: int) -> dict:
    return process_analysis_job(project_id, job_id)


@celery_app.task(name="avip.generate_proposal")
def generate_proposal_job(project_id: int, job_id: int) -> dict:
    return process_proposal_job(project_id, job_id)
