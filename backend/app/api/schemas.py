"""
Pydantic schemas for API request / response serialisation.

These are intentionally decoupled from domain entities so we can
evolve the public API independently.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Request Schemas ──────────────────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    """POST /analyze body."""
    owner: str = Field(..., min_length=1, max_length=255, examples=["facebook"])
    name: str = Field(..., min_length=1, max_length=255, examples=["react"])

    @field_validator("owner", "name")
    @classmethod
    def no_slashes(cls, v: str) -> str:
        if "/" in v:
            raise ValueError("Use separate owner and name fields, not owner/name")
        return v.strip()


class PaginationParams(BaseModel):
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


# ── Response Schemas ─────────────────────────────────────────────────────────


class AnalyzeResponse(BaseModel):
    analysis_id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    message: str = "Analysis queued. Poll GET /analyses/{analysis_id} for results."


class RepositoryOut(BaseModel):
    id: uuid.UUID
    owner: str
    name: str
    full_name: str
    description: Optional[str]
    default_branch: str
    stars: int
    forks: int
    open_issues: int
    language: Optional[str]


class ContributorOut(BaseModel):
    username: str
    total_commits: int
    additions: int
    deletions: int
    first_commit_at: Optional[datetime]
    last_commit_at: Optional[datetime]


class DailyCommit(BaseModel):
    date: str
    commits: int


class MetricsOut(BaseModel):
    total_commits: int
    avg_commit_size: float
    commits_per_day: float
    code_churn_additions: int
    code_churn_deletions: int
    avg_time_between_commits_hours: float
    bus_factor: int
    language_distribution: dict[str, float]
    commits_per_date: list[DailyCommit]


class AIInsightsOut(BaseModel):
    ai_summary: Optional[str]
    readme_quality_score: Optional[float]
    readme_quality_feedback: Optional[str]
    detected_tech_stack: list[str]
    architecture_analysis: Optional[str]


class AnalysisDetailOut(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    error_message: Optional[str]
    metrics: MetricsOut
    ai_insights: AIInsightsOut
    contributors: list[ContributorOut]
    commits_count: int
    created_at: datetime
    completed_at: Optional[datetime]


class AnalysisListItem(BaseModel):
    id: uuid.UUID
    status: str
    total_commits: int
    bus_factor: int
    created_at: datetime
    completed_at: Optional[datetime]


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    error: str
    code: str
    detail: Optional[str] = None
