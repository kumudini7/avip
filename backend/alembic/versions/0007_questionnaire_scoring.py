"""hardcoded questionnaire: drop questions table, assessment_responses.question_key, scoring columns

Revision ID: 0007_questionnaire_scoring
Revises: 0006_assessment_wizard
Create Date: 2026-07-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0007_questionnaire_scoring"
down_revision = "0006_assessment_wizard"
branch_labels = None
depends_on = None


def _drop_fk_on_column(table_name: str, column_name: str) -> None:
    bind = op.get_bind()
    row = bind.execute(
        sa.text(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()
    if row is not None:
        op.drop_constraint(row[0], table_name, type_="foreignkey")


def upgrade() -> None:
    _drop_fk_on_column("assessment_responses", "question_id")
    op.add_column("assessment_responses", sa.Column("question_key", sa.String(length=60), nullable=True))
    op.execute("UPDATE assessment_responses SET question_key = ''")
    op.alter_column(
        "assessment_responses", "question_key", existing_type=sa.String(length=60), nullable=False
    )
    op.create_index(
        op.f("ix_assessment_responses_question_key"), "assessment_responses", ["question_key"], unique=False
    )
    op.drop_index(op.f("ix_assessment_responses_question_id"), table_name="assessment_responses")
    op.drop_column("assessment_responses", "question_id")

    _drop_fk_on_column("questions", "domain_id")
    _drop_fk_on_column("questions", "created_by")
    op.drop_index(op.f("ix_questions_domain_id"), table_name="questions")
    op.drop_index(op.f("ix_questions_id"), table_name="questions")
    op.drop_table("questions")

    op.add_column("classification_results", sa.Column("ai_readiness_score", sa.Float(), nullable=True))
    op.add_column("classification_results", sa.Column("automation_maturity_score", sa.Float(), nullable=True))
    op.add_column("classification_results", sa.Column("migration_readiness_score", sa.Float(), nullable=True))
    op.add_column("classification_results", sa.Column("recommendation", sa.String(length=40), nullable=True))
    op.add_column("classification_results", sa.Column("business_justification", sa.JSON(), nullable=True))
    op.add_column("classification_results", sa.Column("roi_estimate", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("classification_results", "roi_estimate")
    op.drop_column("classification_results", "business_justification")
    op.drop_column("classification_results", "recommendation")
    op.drop_column("classification_results", "migration_readiness_score")
    op.drop_column("classification_results", "automation_maturity_score")
    op.drop_column("classification_results", "ai_readiness_score")

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

    op.drop_index(op.f("ix_assessment_responses_question_key"), table_name="assessment_responses")
    op.drop_column("assessment_responses", "question_key")
    op.add_column("assessment_responses", sa.Column("question_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_assessment_responses_question_id"), "assessment_responses", ["question_id"], unique=False)
    op.create_foreign_key(
        None, "assessment_responses", "questions", ["question_id"], ["id"], ondelete="CASCADE"
    )
