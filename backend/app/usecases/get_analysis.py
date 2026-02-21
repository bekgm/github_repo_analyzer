"""
Use case: Get Analysis Result.

Simple query use case — reads from DB and returns the analysis.
"""

from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundError
from app.domain.entities import Analysis
from app.domain.repositories import AnalysisRepository, CommitStatsRepository, ContributorRepository


class GetAnalysisUseCase:
    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        commit_stats_repo: CommitStatsRepository,
        contributor_repo: ContributorRepository,
    ) -> None:
        self._analyses = analysis_repo
        self._commits = commit_stats_repo
        self._contributors = contributor_repo

    async def execute(self, analysis_id: uuid.UUID) -> dict:
        analysis = await self._analyses.get_by_id(analysis_id)
        if not analysis:
            raise NotFoundError("Analysis", str(analysis_id))

        contributors = await self._contributors.get_by_analysis(analysis_id)
        commits = await self._commits.get_by_analysis(analysis_id)

        return {
            "analysis": analysis,
            "contributors": list(contributors),
            "commits": list(commits),
            "commits_count": len(commits),
        }


class ListAnalysesUseCase:
    def __init__(self, analysis_repo: AnalysisRepository) -> None:
        self._analyses = analysis_repo

    async def execute(
        self, repository_id: uuid.UUID, *, limit: int = 20, offset: int = 0
    ) -> list[Analysis]:
        return list(await self._analyses.list_by_repository(
            repository_id, limit=limit, offset=offset
        ))
