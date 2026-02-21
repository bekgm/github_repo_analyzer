"""
Repository (port) interfaces — abstract contracts the infrastructure must fulfil.

This is the *Dependency Inversion* boundary: use-cases depend only on these
ABCs; concrete implementations live in the infrastructure layer.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from app.domain.entities import (
    Analysis,
    AnalysisStatus,
    CommitStats,
    Contributor,
    Repository,
    User,
)


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...


class RepositoryRepository(ABC):
    """Persists GitHub repository metadata."""

    @abstractmethod
    async def get_by_id(self, repo_id: uuid.UUID) -> Optional[Repository]: ...

    @abstractmethod
    async def get_by_full_name(self, full_name: str) -> Optional[Repository]: ...

    @abstractmethod
    async def upsert(self, repo: Repository) -> Repository: ...


class AnalysisRepository(ABC):
    @abstractmethod
    async def get_by_id(self, analysis_id: uuid.UUID) -> Optional[Analysis]: ...

    @abstractmethod
    async def list_by_repository(
        self, repo_id: uuid.UUID, *, limit: int = 20, offset: int = 0
    ) -> Sequence[Analysis]: ...

    @abstractmethod
    async def create(self, analysis: Analysis) -> Analysis: ...

    @abstractmethod
    async def update_status(
        self, analysis_id: uuid.UUID, status: AnalysisStatus, error_message: Optional[str] = None
    ) -> None: ...

    @abstractmethod
    async def save_results(self, analysis: Analysis) -> None: ...


class CommitStatsRepository(ABC):
    @abstractmethod
    async def bulk_create(self, commits: Sequence[CommitStats]) -> None: ...

    @abstractmethod
    async def get_by_analysis(self, analysis_id: uuid.UUID) -> Sequence[CommitStats]: ...


class ContributorRepository(ABC):
    @abstractmethod
    async def bulk_upsert(self, contributors: Sequence[Contributor]) -> None: ...

    @abstractmethod
    async def get_by_analysis(self, analysis_id: uuid.UUID) -> Sequence[Contributor]: ...
