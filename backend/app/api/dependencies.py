"""
FastAPI dependency injection.

Wires together infrastructure → use-cases for each request.
Clean Architecture's composition root lives here.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.redis_cache import CachedGitHubClient, RedisCache
from app.infrastructure.database.repositories import (
    SqlAlchemyAnalysisRepository,
    SqlAlchemyCommitStatsRepository,
    SqlAlchemyContributorRepository,
    SqlAlchemyRepoRepository,
)
from app.infrastructure.database.session import get_db
from app.infrastructure.external.github_client import GitHubClient
from app.usecases.analyze_repository import AnalyzeRepositoryUseCase
from app.usecases.get_analysis import GetAnalysisUseCase, ListAnalysesUseCase


def _github_client() -> CachedGitHubClient:
    return CachedGitHubClient(GitHubClient(), RedisCache())


def get_analyze_use_case(
    session: AsyncSession = Depends(get_db),
    gh: CachedGitHubClient = Depends(_github_client),
) -> AnalyzeRepositoryUseCase:
    return AnalyzeRepositoryUseCase(
        repo_repository=SqlAlchemyRepoRepository(session),
        analysis_repository=SqlAlchemyAnalysisRepository(session),
        github_client=gh,
    )


def get_analysis_detail_use_case(
    session: AsyncSession = Depends(get_db),
) -> GetAnalysisUseCase:
    return GetAnalysisUseCase(
        analysis_repo=SqlAlchemyAnalysisRepository(session),
        commit_stats_repo=SqlAlchemyCommitStatsRepository(session),
        contributor_repo=SqlAlchemyContributorRepository(session),
    )


def get_list_analyses_use_case(
    session: AsyncSession = Depends(get_db),
) -> ListAnalysesUseCase:
    return ListAnalysesUseCase(
        analysis_repo=SqlAlchemyAnalysisRepository(session),
    )
