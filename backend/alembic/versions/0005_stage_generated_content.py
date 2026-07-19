"""add generated content columns to engagement_stage_states

Revision ID: 0005_stage_generated_content
Revises: 0004_gtm_engagements
Create Date: 2026-07-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_stage_generated_content"
down_revision = "0004_gtm_engagements"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("engagement_stage_states", sa.Column("generated_content_json", sa.JSON(), nullable=True))
    op.add_column("engagement_stage_states", sa.Column("content_generated_at", sa.DateTime(), nullable=True))
    op.add_column("engagement_stage_states", sa.Column("content_model", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("engagement_stage_states", "content_model")
    op.drop_column("engagement_stage_states", "content_generated_at")
    op.drop_column("engagement_stage_states", "generated_content_json")
