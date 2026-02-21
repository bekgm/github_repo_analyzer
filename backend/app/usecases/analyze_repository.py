"""
Use case: Trigger Repository Analysis.

Orchestrates the full workflow:
1. Validate input.
2. Fetch / upsert repository metadata.
3. Create an Analysis record in PENDING state.
4. Dispatch a Celery background task to perform the heavy work.

This is a thin *application service* — it contains NO business rules,
only coordination between domain objects and infrastructure.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import structlog

from app.core.exceptions import AlreadyExistsError, ValidationError
from app.domain.entities import Analysis, AnalysisStatus, Repository
from app.domain.repositories import AnalysisRepository, RepositoryRepository
from app.infrastructure.cache.redis_cache import CachedGitHubClient

logger = structlog.get_logger(__name__)


@dataclass
class AnalyzeRepoRequest:
    owner: str
    name: str
    user_id: uuid.UUID | None = None


@dataclass
class AnalyzeRepoResponse:
    analysis_id: uuid.UUID
    repository_id: uuid.UUID
    status: str


class AnalyzeRepositoryUseCase:
    """
    Entry point for the POST /analyze endpoint.

    Dependencies are injected via constructor (Dependency Inversion).
    """

    def __init__(
        self,
        repo_repository: RepositoryRepository,
        analysis_repository: AnalysisRepository,
        github_client: CachedGitHubClient,
    ) -> None:
        self._repos = repo_repository
        self._analyses = analysis_repository
        self._gh = github_client

    async def execute(self, request: AnalyzeRepoRequest) -> AnalyzeRepoResponse:
        # ── Validate ─────────────────────────────────────────────────────
        if not request.owner or not request.name:
            raise ValidationError("owner and name are required")

        full_name = f"{request.owner}/{request.name}"
        logger.info("Triggering analysis", repo=full_name)

        # ── Fetch repo metadata from GitHub (cached) ────────────────────
        gh_data = await self._gh.get_repository(request.owner, request.name)
        from app.infrastructure.external.github_client import GitHubClient
        gh = GitHubClient()
        repo_entity = gh.parse_repo_metadata(gh_data)

        # ── Upsert repository ────────────────────────────────────────────
        repo_entity = await self._repos.upsert(repo_entity)

        # ── Create analysis (PENDING) ────────────────────────────────────
        analysis = Analysis(
            repository_id=repo_entity.id,
            user_id=request.user_id,
            status=AnalysisStatus.PENDING,
        )
        analysis = await self._analyses.create(analysis)

        # ── Dispatch background job ──────────────────────────────────────
        from app.infrastructure.jobs.tasks import run_analysis_task

        run_analysis_task.delay(
            str(analysis.id),
            request.owner,
            request.name,
        )
        logger.info("Analysis dispatched", analysis_id=str(analysis.id))

        return AnalyzeRepoResponse(
            analysis_id=analysis.id,
            repository_id=repo_entity.id,
            status=analysis.status.value,
        )
