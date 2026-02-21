from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class User:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Repository:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    owner: str = ""
    name: str = ""
    full_name: str = ""     
    description: Optional[str] = None
    default_branch: str = "main"
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    language: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Analysis:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    repository_id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_id: Optional[uuid.UUID] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    error_message: Optional[str] = None

    total_commits: int = 0
    avg_commit_size: float = 0.0
    commits_per_day: float = 0.0
    commits_per_month: float = 0.0
    code_churn_additions: int = 0
    code_churn_deletions: int = 0
    avg_time_between_commits_hours: float = 0.0
    bus_factor: int = 0
    language_distribution: dict[str, float] = field(default_factory=dict)

    ai_summary: Optional[str] = None
    readme_quality_score: Optional[float] = None
    readme_quality_feedback: Optional[str] = None
    detected_tech_stack: list[str] = field(default_factory=list)
    architecture_analysis: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class CommitStats:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    analysis_id: uuid.UUID = field(default_factory=uuid.uuid4)
    sha: str = ""
    author_name: str = ""
    author_email: str = ""
    message: str = ""
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0
    committed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Contributor:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    analysis_id: uuid.UUID = field(default_factory=uuid.uuid4)
    username: str = ""
    avatar_url: Optional[str] = None
    total_commits: int = 0
    additions: int = 0
    deletions: int = 0
    first_commit_at: Optional[datetime] = None
    last_commit_at: Optional[datetime] = None
