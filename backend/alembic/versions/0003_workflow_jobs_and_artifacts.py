"""workflow jobs and proposal artifacts

Revision ID: 0003_workflow_jobs_and_artifacts
Revises: 0002_document_display_name
Create Date: 2026-07-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_workflow_jobs_and_artifacts"
down_revision = "0002_document_display_name"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "proposals",
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'draft'")),
    )

    op.create_table(
        "workflow_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("task_id", sa.String(length=255), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_workflow_jobs_id"), "workflow_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_workflow_jobs_project_id"), "workflow_jobs", ["project_id"], unique=False)
    op.create_index(op.f("ix_workflow_jobs_task_id"), "workflow_jobs", ["task_id"], unique=False)

    op.create_table(
        "proposal_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proposal_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("artifact_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default=sa.text("'queued'")),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["workflow_jobs.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_proposal_artifacts_id"), "proposal_artifacts", ["id"], unique=False)
    op.create_index(op.f("ix_proposal_artifacts_job_id"), "proposal_artifacts", ["job_id"], unique=False)
    op.create_index(op.f("ix_proposal_artifacts_proposal_id"), "proposal_artifacts", ["proposal_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_proposal_artifacts_proposal_id"), table_name="proposal_artifacts")
    op.drop_index(op.f("ix_proposal_artifacts_job_id"), table_name="proposal_artifacts")
    op.drop_index(op.f("ix_proposal_artifacts_id"), table_name="proposal_artifacts")
    op.drop_table("proposal_artifacts")

    op.drop_index(op.f("ix_workflow_jobs_task_id"), table_name="workflow_jobs")
    op.drop_index(op.f("ix_workflow_jobs_project_id"), table_name="workflow_jobs")
    op.drop_index(op.f("ix_workflow_jobs_id"), table_name="workflow_jobs")
    op.drop_table("workflow_jobs")

    op.drop_column("proposals", "status")

