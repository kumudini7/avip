"""assessment wizard: domains, questions, assessments, responses, classification, roi

Revision ID: 0006_assessment_wizard
Revises: 0005_stage_generated_content
Create Date: 2026-07-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_assessment_wizard"
down_revision = "0005_stage_generated_content"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("company", sa.String(length=255), nullable=True))
    op.execute("UPDATE users SET role = 'pre_sales' WHERE role <> 'client'")

    op.create_table(
        "domains",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name", name="uq_domains_name"),
    )
    op.create_index(op.f("ix_domains_id"), "domains", ["id"], unique=False)

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain_id", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("weightage", sa.JSON(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["domain_id"], ["domains.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_questions_id"), "questions", ["id"], unique=False)
    op.create_index(op.f("ix_questions_domain_id"), "questions", ["domain_id"], unique=False)

    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("domain_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'in_progress'")),
        sa.Column("business_context", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["domain_id"], ["domains.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_assessments_id"), "assessments", ["id"], unique=False)
    op.create_index(op.f("ix_assessments_client_id"), "assessments", ["client_id"], unique=False)
    op.create_index(op.f("ix_assessments_domain_id"), "assessments", ["domain_id"], unique=False)

    op.create_table(
        "assessment_responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("response", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_assessment_responses_id"), "assessment_responses", ["id"], unique=False)
    op.create_index(
        op.f("ix_assessment_responses_assessment_id"), "assessment_responses", ["assessment_id"], unique=False
    )
    op.create_index(
        op.f("ix_assessment_responses_question_id"), "assessment_responses", ["question_id"], unique=False
    )

    op.create_table(
        "classification_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("matched_use_case", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("reasoning", sa.JSON(), nullable=True),
        sa.Column("similar_use_cases", sa.JSON(), nullable=True),
        sa.Column("complexity", sa.String(length=20), nullable=False),
        sa.Column("estimated_timeline", sa.String(length=60), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assessment_id", name="uq_classification_results_assessment_id"),
    )
    op.create_index(op.f("ix_classification_results_id"), "classification_results", ["id"], unique=False)
    op.create_index(
        op.f("ix_classification_results_assessment_id"), "classification_results", ["assessment_id"], unique=False
    )

    op.create_table(
        "roi_inputs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("volume_per_month", sa.Integer(), nullable=False),
        sa.Column("team_size", sa.Integer(), nullable=False),
        sa.Column("avg_fte_cost", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default=sa.text("'INR'")),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assessment_id", name="uq_roi_inputs_assessment_id"),
    )
    op.create_index(op.f("ix_roi_inputs_id"), "roi_inputs", ["id"], unique=False)
    op.create_index(op.f("ix_roi_inputs_assessment_id"), "roi_inputs", ["assessment_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_roi_inputs_assessment_id"), table_name="roi_inputs")
    op.drop_index(op.f("ix_roi_inputs_id"), table_name="roi_inputs")
    op.drop_table("roi_inputs")

    op.drop_index(op.f("ix_classification_results_assessment_id"), table_name="classification_results")
    op.drop_index(op.f("ix_classification_results_id"), table_name="classification_results")
    op.drop_table("classification_results")

    op.drop_index(op.f("ix_assessment_responses_question_id"), table_name="assessment_responses")
    op.drop_index(op.f("ix_assessment_responses_assessment_id"), table_name="assessment_responses")
    op.drop_index(op.f("ix_assessment_responses_id"), table_name="assessment_responses")
    op.drop_table("assessment_responses")

    op.drop_index(op.f("ix_assessments_domain_id"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_client_id"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_id"), table_name="assessments")
    op.drop_table("assessments")

    op.drop_index(op.f("ix_questions_domain_id"), table_name="questions")
    op.drop_index(op.f("ix_questions_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_domains_id"), table_name="domains")
    op.drop_table("domains")

    op.drop_column("users", "company")
