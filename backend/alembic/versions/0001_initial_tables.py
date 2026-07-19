"""initial tables

Revision ID: 0001_initial_tables
Revises:
Create Date: 2026-07-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default=sa.text("'consultant'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("client_name", sa.String(length=255), nullable=True),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_projects_owner_id"), "projects", ["owner_id"], unique=False)

    op.create_table(
        "process_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_process_documents_project_id"), "process_documents", ["project_id"], unique=False)

    op.create_table(
        "process_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("automation_readiness", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("ai_confidence", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default=sa.text("'Medium'")),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("analysis_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_process_analyses_project_id"), "process_analyses", ["project_id"], unique=False)

    op.create_table(
        "proposals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=True),
        sa.Column("proposal_json", sa.JSON(), nullable=False),
        sa.Column("pdf_path", sa.String(length=512), nullable=True),
        sa.Column("ppt_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_proposals_project_id"), "proposals", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_proposals_project_id"), table_name="proposals")
    op.drop_table("proposals")

    op.drop_index(op.f("ix_process_analyses_project_id"), table_name="process_analyses")
    op.drop_table("process_analyses")

    op.drop_index(op.f("ix_process_documents_project_id"), table_name="process_documents")
    op.drop_table("process_documents")

    op.drop_index(op.f("ix_projects_owner_id"), table_name="projects")
    op.drop_table("projects")

    op.drop_table("users")
