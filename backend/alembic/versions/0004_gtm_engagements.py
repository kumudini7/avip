"""gtm engagements, kpis, stage states, activity entries

Revision ID: 0004_gtm_engagements
Revises: 0003_workflow_jobs_and_artifacts
Create Date: 2026-07-18 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_gtm_engagements"
down_revision = "0003_workflow_jobs_and_artifacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "engagements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("client_name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=120), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False, server_default=sa.text("'discovery'")),
        sa.Column("health", sa.String(length=32), nullable=False, server_default=sa.text("'on_track'")),
        sa.Column("started_at", sa.Date(), nullable=False),
        sa.Column("closed_at", sa.Date(), nullable=True),
        sa.Column("roi_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_engagements_id"), "engagements", ["id"], unique=False)
    op.create_index(op.f("ix_engagements_owner_id"), "engagements", ["owner_id"], unique=False)

    op.create_table(
        "engagement_kpis",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("engagement_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("baseline_value", sa.String(length=120), nullable=False),
        sa.Column("target_value", sa.String(length=120), nullable=False),
        sa.Column("current_value", sa.String(length=120), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["engagement_id"], ["engagements.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_engagement_kpis_id"), "engagement_kpis", ["id"], unique=False)
    op.create_index(op.f("ix_engagement_kpis_engagement_id"), "engagement_kpis", ["engagement_id"], unique=False)

    op.create_table(
        "engagement_stage_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("engagement_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.String(length=32), nullable=False),
        sa.Column("checklist_json", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["engagement_id"], ["engagements.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("engagement_id", "stage", name="uq_engagement_stage"),
    )
    op.create_index(op.f("ix_engagement_stage_states_id"), "engagement_stage_states", ["id"], unique=False)
    op.create_index(
        op.f("ix_engagement_stage_states_engagement_id"), "engagement_stage_states", ["engagement_id"], unique=False
    )

    op.create_table(
        "activity_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("engagement_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["engagement_id"], ["engagements.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_activity_entries_id"), "activity_entries", ["id"], unique=False)
    op.create_index(op.f("ix_activity_entries_engagement_id"), "activity_entries", ["engagement_id"], unique=False)
    op.create_index(op.f("ix_activity_entries_created_at"), "activity_entries", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_activity_entries_created_at"), table_name="activity_entries")
    op.drop_index(op.f("ix_activity_entries_engagement_id"), table_name="activity_entries")
    op.drop_index(op.f("ix_activity_entries_id"), table_name="activity_entries")
    op.drop_table("activity_entries")

    op.drop_index(op.f("ix_engagement_stage_states_engagement_id"), table_name="engagement_stage_states")
    op.drop_index(op.f("ix_engagement_stage_states_id"), table_name="engagement_stage_states")
    op.drop_table("engagement_stage_states")

    op.drop_index(op.f("ix_engagement_kpis_engagement_id"), table_name="engagement_kpis")
    op.drop_index(op.f("ix_engagement_kpis_id"), table_name="engagement_kpis")
    op.drop_table("engagement_kpis")

    op.drop_index(op.f("ix_engagements_owner_id"), table_name="engagements")
    op.drop_index(op.f("ix_engagements_id"), table_name="engagements")
    op.drop_table("engagements")
