from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.analysis import ProcessAnalysis
from app.models.document import ProcessDocument
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.proposal_artifact import ProposalArtifact
from app.models.user import User
from app.models.workflow_job import WorkflowJob
from app.services.document_processor import ensure_directory, save_file
from app.services.workflow_service import build_analysis_payload, build_proposal_payload


DEMO_CASES = [
    {
        "name": "Invoice Automation Discovery",
        "client_name": "Northwind Finance",
        "industry": "finance",
        "description": "Invoice intake, OCR extraction, ERP validation, approval routing, and payment posting.",
        "document_name": "invoice_process_sop.txt",
        "document_text": "Receive invoice email. Download attachment. Extract invoice data. Validate amount. Approve high value exceptions. Update ERP.",
    },
    {
        "name": "HR Onboarding Value Model",
        "client_name": "Aster HR Services",
        "industry": "hr",
        "description": "Employee onboarding, document verification, account creation, policy acknowledgements, and payroll setup.",
        "document_name": "hr_onboarding_flow.txt",
        "document_text": "When a candidate accepts the offer, HR sends welcome email, verifies documents, creates system accounts, routes approvals, and updates payroll.",
    },
    {
        "name": "Claims Processing Benchmark",
        "client_name": "Helix Insurance",
        "industry": "healthcare",
        "description": "Claims intake, document classification, policy validation, exception handling, and settlement updates.",
        "document_name": "claims_processing_notes.txt",
        "document_text": "Claims are received by email and portal. OCR reads attachments. AI classifies claim type. Human reviews exceptions. System updates the claim ledger.",
    },
]


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        demo_user = db.execute(select(User).where(User.email == settings.demo_user_email)).scalar_one_or_none()
        if demo_user is None:
            demo_user = User(
                email=settings.demo_user_email,
                full_name="AVIP Demo",
                hashed_password=hash_password(settings.demo_user_password),
                role="demo",
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

        if db.execute(select(Project).where(Project.owner_id == demo_user.id)).scalars().first() is not None:
            return

        demo_root = ensure_directory(Path(settings.upload_dir) / "demo_seed")
        report_root = ensure_directory(Path(settings.report_dir) / "demo_seed")
        _ = report_root

        for case in DEMO_CASES:
            project = Project(
                owner_id=demo_user.id,
                name=case["name"],
                client_name=case["client_name"],
                industry=case["industry"],
                description=case["description"],
                status="active",
            )
            db.add(project)
            db.commit()
            db.refresh(project)

            document_path = save_file(demo_root / f"project_{project.id}", case["document_name"], case["document_text"].encode("utf-8"))
            document = ProcessDocument(
                project_id=project.id,
                original_filename=case["document_name"],
                display_name=Path(case["document_name"]).stem.replace("_", " ").title(),
                stored_filename=document_path.name,
                mime_type="text/plain",
                storage_path=str(document_path),
                extracted_text=case["document_text"],
                file_size=len(case["document_text"].encode("utf-8")),
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            analysis_payload = build_analysis_payload(project, [document])
            analysis = ProcessAnalysis(
                project_id=project.id,
                automation_readiness=analysis_payload["automation_readiness"],
                ai_confidence=analysis_payload["ai_confidence"],
                risk_level=analysis_payload["risk_level"],
                summary=analysis_payload["summary"],
                analysis_json=analysis_payload,
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            analysis_job = WorkflowJob(
                project_id=project.id,
                job_type="analysis",
                status="completed",
                task_id=f"seed-analysis-{project.id}",
                payload_json={"seed": True},
                result_json=analysis_payload,
            )
            db.add(analysis_job)
            db.commit()
            db.refresh(analysis_job)

            proposal_payload = build_proposal_payload(project, analysis_payload)
            proposal = Proposal(
                project_id=project.id,
                title=f"{project.name} Proposal",
                status="ready",
                executive_summary=proposal_payload["executive_summary"],
                proposal_json=proposal_payload,
                pdf_path=proposal_payload["files"]["pdf"],
                ppt_path=proposal_payload["files"]["pptx"],
            )
            db.add(proposal)
            db.commit()
            db.refresh(proposal)

            proposal_job = WorkflowJob(
                project_id=project.id,
                job_type="proposal",
                status="completed",
                task_id=f"seed-proposal-{project.id}",
                payload_json={"seed": True},
                result_json=proposal_payload,
            )
            db.add(proposal_job)
            db.commit()
            db.refresh(proposal_job)

            for artifact_type, file_path in (("pdf", proposal.pdf_path), ("pptx", proposal.ppt_path)):
                artifact = ProposalArtifact(
                    proposal_id=proposal.id,
                    job_id=proposal_job.id,
                    artifact_type=artifact_type,
                    status="completed",
                    file_path=file_path,
                    file_name=Path(file_path).name if file_path else None,
                    generated_at=datetime.utcnow(),
                )
                db.add(artifact)

            db.commit()

            for artifact_type, file_path in (("pdf", proposal.pdf_path), ("pptx", proposal.ppt_path)):
                artifact = ProposalArtifact(
                    proposal_id=proposal.id,
                    job_id=proposal_job.id,
                    artifact_type=artifact_type,
                    status="completed",
                    file_path=file_path,
                    file_name=Path(file_path).name if file_path else None,
                    generated_at=proposal.created_at,
                )
                db.add(artifact)
            db.commit()
    finally:
        db.close()
