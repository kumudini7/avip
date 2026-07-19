"""add document display name

Revision ID: 0002_document_display_name
Revises: 0001_initial_tables
Create Date: 2026-07-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_document_display_name"
down_revision = "0001_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "process_documents",
        sa.Column("display_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("process_documents", "display_name")

