from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5


class Base(DeclarativeBase):
    pass


class Posting(Base):
    __tablename__ = "postings"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    source_job_id: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    company: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    experience_level: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    url: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostingSkill(Base):
    __tablename__ = "posting_skills"
    __table_args__ = (
        CheckConstraint("kind IN ('required', 'preferred')", name="posting_skills_kind"),
    )

    posting_id: Mapped[int] = mapped_column(
        ForeignKey("postings.id", ondelete="CASCADE"), primary_key=True
    )
    skill: Mapped[str] = mapped_column(Text, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, primary_key=True)


class PostingEmbedding(Base):
    __tablename__ = "posting_embeddings"

    posting_id: Mapped[int] = mapped_column(
        ForeignKey("postings.id", ondelete="CASCADE"), primary_key=True
    )
    model: Mapped[str] = mapped_column(Text, primary_key=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LlmCache(Base):
    __tablename__ = "llm_cache"

    prompt_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    model: Mapped[str] = mapped_column(Text)
    response: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (
        CheckConstraint("relevant BETWEEN 0 AND 2", name="labels_relevant_range"),
        CheckConstraint("source IN ('human', 'llm')", name="labels_source"),
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True
    )
    posting_id: Mapped[int] = mapped_column(
        ForeignKey("postings.id", ondelete="CASCADE"), primary_key=True
    )
    # Part of the key so human and LLM labels for the same pair can coexist
    # (needed for the Week 5 agreement / Cohen's kappa analysis).
    source: Mapped[str] = mapped_column(Text, primary_key=True)
    relevant: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
