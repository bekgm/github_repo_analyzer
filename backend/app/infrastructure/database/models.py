"""
SQLAlchemy ORM models.

Design decisions
────────────────
• UUIDs as primary keys — avoids enumeration attacks, safe for distributed ID
  generation (important when Celery workers create records).
• created_at / updated_at on every table — audit trail without extra tooling.
• Indexes on foreign keys + common query columns (full_name, status).
• CASCADE deletes from repository → analysis → commits/contributors so a
  repo removal cleans up everything.
• The `analyses` table stores both computed numeric metrics AND AI text fields
  to keep reads simple (single SELECT); a future refactor could split AI
  results into their own table if they grow significantly.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Users ────────────────────────────────────────────────────────────────────


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    analyses: Mapped[list["AnalysisModel"]] = relationship(back_populates="user")


# ── Repositories ─────────────────────────────────────────────────────────────


class RepositoryModel(Base):
    __tablename__ = "repositories"
    __table_args__ = (
        Index("ix_repositories_full_name", "full_name", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    open_issues: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    analyses: Mapped[list["AnalysisModel"]] = relationship(
        back_populates="repository", cascade="all, delete-orphan"
    )


# ── Analyses ─────────────────────────────────────────────────────────────────


class AnalysisModel(Base):
    __tablename__ = "analyses"
    __table_args__ = (
        Index("ix_analyses_repo_status", "repository_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metrics
    total_commits: Mapped[int] = mapped_column(Integer, default=0)
    avg_commit_size: Mapped[float] = mapped_column(Float, default=0.0)
    commits_per_day: Mapped[float] = mapped_column(Float, default=0.0)
    commits_per_month: Mapped[float] = mapped_column(Float, default=0.0)
    code_churn_additions: Mapped[int] = mapped_column(Integer, default=0)
    code_churn_deletions: Mapped[int] = mapped_column(Integer, default=0)
    avg_time_between_commits_hours: Mapped[float] = mapped_column(Float, default=0.0)
    bus_factor: Mapped[int] = mapped_column(Integer, default=0)
    language_distribution: Mapped[dict] = mapped_column(JSON, default=dict)

    # AI Insights
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    readme_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    readme_quality_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    architecture_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository: Mapped["RepositoryModel"] = relationship(back_populates="analyses")
    user: Mapped["UserModel | None"] = relationship(back_populates="analyses")
    commit_stats: Mapped[list["CommitStatsModel"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )
    contributors: Mapped[list["ContributorModel"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )


# ── Commit Stats ─────────────────────────────────────────────────────────────


class CommitStatsModel(Base):
    __tablename__ = "commits_stats"
    __table_args__ = (
        Index("ix_commits_stats_analysis", "analysis_id"),
        Index("ix_commits_stats_sha", "sha"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    sha: Mapped[str] = mapped_column(String(40), nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    analysis: Mapped["AnalysisModel"] = relationship(back_populates="commit_stats")


# ── Contributors ─────────────────────────────────────────────────────────────


class ContributorModel(Base):
    __tablename__ = "contributors"
    __table_args__ = (
        Index("ix_contributors_analysis", "analysis_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    total_commits: Mapped[int] = mapped_column(Integer, default=0)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    first_commit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_commit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    analysis: Mapped["AnalysisModel"] = relationship(back_populates="contributors")
