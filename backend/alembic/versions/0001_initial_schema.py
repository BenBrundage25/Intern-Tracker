"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _created_at() -> sa.Column:
    return sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "postings",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("source_job_id", sa.Text),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("company", sa.Text),
        sa.Column("location", sa.Text),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("experience_level", sa.Text),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("url", sa.Text),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        _created_at(),
    )

    op.create_table(
        "posting_skills",
        sa.Column(
            "posting_id",
            sa.BigInteger,
            sa.ForeignKey("postings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("skill", sa.Text, primary_key=True),
        sa.Column("kind", sa.Text, primary_key=True),
        sa.CheckConstraint("kind IN ('required', 'preferred')", name="posting_skills_kind"),
    )
    op.create_index("ix_posting_skills_skill", "posting_skills", ["skill"])

    op.create_table(
        "posting_embeddings",
        sa.Column(
            "posting_id",
            sa.BigInteger,
            sa.ForeignKey("postings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("model", sa.Text, primary_key=True),
        sa.Column("embedding", Vector(384), nullable=False),
    )

    op.create_table(
        "resumes",
        sa.Column("id", sa.BigInteger, sa.Identity(), primary_key=True),
        sa.Column("text", sa.Text, nullable=False),
        _created_at(),
    )

    op.create_table(
        "llm_cache",
        sa.Column("prompt_hash", sa.String(64), primary_key=True),
        sa.Column("model", sa.Text, nullable=False),
        sa.Column("response", JSONB, nullable=False),
        _created_at(),
    )

    op.create_table(
        "labels",
        sa.Column(
            "resume_id",
            sa.BigInteger,
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "posting_id",
            sa.BigInteger,
            sa.ForeignKey("postings.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("source", sa.Text, primary_key=True),
        sa.Column("relevant", sa.SmallInteger, nullable=False),
        _created_at(),
        sa.CheckConstraint("relevant BETWEEN 0 AND 2", name="labels_relevant_range"),
        sa.CheckConstraint("source IN ('human', 'llm')", name="labels_source"),
    )


def downgrade() -> None:
    for table in (
        "labels",
        "llm_cache",
        "resumes",
        "posting_embeddings",
        "posting_skills",
        "postings",
    ):
        op.drop_table(table)
