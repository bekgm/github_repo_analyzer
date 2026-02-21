"""
Concrete repository implementations backed by SQLAlchemy async sessions.
"""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    Analysis,
    AnalysisStatus,
    CommitStats,
    Contributor,
    Repository,
    User,
)
from app.domain.repositories import (
    AnalysisRepository,
    CommitStatsRepository,
    ContributorRepository,
    RepositoryRepository,
    UserRepository,
)
from app.infrastructure.database.models import (
    AnalysisModel,
    CommitStatsModel,
    ContributorModel,
    RepositoryModel,
    UserModel,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _user_model_to_entity(m: UserModel) -> User:
    return User(
        id=m.id, username=m.username, email=m.email,
        hashed_password=m.hashed_password, is_active=m.is_active,
        created_at=m.created_at, updated_at=m.updated_at,
    )


def _repo_model_to_entity(m: RepositoryModel) -> Repository:
    return Repository(
        id=m.id, owner=m.owner, name=m.name, full_name=m.full_name,
        description=m.description, default_branch=m.default_branch,
        stars=m.stars, forks=m.forks, open_issues=m.open_issues,
        language=m.language, created_at=m.created_at, updated_at=m.updated_at,
    )


def _analysis_model_to_entity(m: AnalysisModel) -> Analysis:
    return Analysis(
        id=m.id, repository_id=m.repository_id, user_id=m.user_id,
        status=AnalysisStatus(m.status), error_message=m.error_message,
        total_commits=m.total_commits, avg_commit_size=m.avg_commit_size,
        commits_per_day=m.commits_per_day, commits_per_month=m.commits_per_month,
        code_churn_additions=m.code_churn_additions,
        code_churn_deletions=m.code_churn_deletions,
        avg_time_between_commits_hours=m.avg_time_between_commits_hours,
        bus_factor=m.bus_factor, language_distribution=m.language_distribution or {},
        ai_summary=m.ai_summary, readme_quality_score=m.readme_quality_score,
        readme_quality_feedback=m.readme_quality_feedback,
        detected_tech_stack=m.detected_tech_stack or [],
        architecture_analysis=m.architecture_analysis,
        created_at=m.created_at, completed_at=m.completed_at,
    )


def _commit_model_to_entity(m: CommitStatsModel) -> CommitStats:
    return CommitStats(
        id=m.id, analysis_id=m.analysis_id, sha=m.sha,
        author_name=m.author_name, author_email=m.author_email,
        message=m.message, additions=m.additions, deletions=m.deletions,
        files_changed=m.files_changed, committed_at=m.committed_at,
    )


def _contributor_model_to_entity(m: ContributorModel) -> Contributor:
    return Contributor(
        id=m.id, analysis_id=m.analysis_id, username=m.username,
        avatar_url=m.avatar_url, total_commits=m.total_commits,
        additions=m.additions, deletions=m.deletions,
        first_commit_at=m.first_commit_at, last_commit_at=m.last_commit_at,
    )


# ── User Repository ─────────────────────────────────────────────────────────


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self._session.get(UserModel, user_id)
        return _user_model_to_entity(result) if result else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _user_model_to_entity(row) if row else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id, username=user.username, email=user.email,
            hashed_password=user.hashed_password, is_active=user.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return _user_model_to_entity(model)


# ── Repository Repository ───────────────────────────────────────────────────


class SqlAlchemyRepoRepository(RepositoryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, repo_id: uuid.UUID) -> Optional[Repository]:
        result = await self._session.get(RepositoryModel, repo_id)
        return _repo_model_to_entity(result) if result else None

    async def get_by_full_name(self, full_name: str) -> Optional[Repository]:
        stmt = select(RepositoryModel).where(RepositoryModel.full_name == full_name)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _repo_model_to_entity(row) if row else None

    async def upsert(self, repo: Repository) -> Repository:
        stmt = pg_insert(RepositoryModel).values(
            id=repo.id, owner=repo.owner, name=repo.name,
            full_name=repo.full_name, description=repo.description,
            default_branch=repo.default_branch, stars=repo.stars,
            forks=repo.forks, open_issues=repo.open_issues, language=repo.language,
        ).on_conflict_do_update(
            index_elements=["full_name"],
            set_={
                "description": repo.description,
                "default_branch": repo.default_branch,
                "stars": repo.stars,
                "forks": repo.forks,
                "open_issues": repo.open_issues,
                "language": repo.language,
            },
        ).returning(RepositoryModel.__table__.c.id)
        result = await self._session.execute(stmt)
        repo.id = result.scalar_one()
        await self._session.flush()
        return repo


# ── Analysis Repository ─────────────────────────────────────────────────────


class SqlAlchemyAnalysisRepository(AnalysisRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, analysis_id: uuid.UUID) -> Optional[Analysis]:
        result = await self._session.get(AnalysisModel, analysis_id)
        return _analysis_model_to_entity(result) if result else None

    async def list_by_repository(
        self, repo_id: uuid.UUID, *, limit: int = 20, offset: int = 0
    ) -> Sequence[Analysis]:
        stmt = (
            select(AnalysisModel)
            .where(AnalysisModel.repository_id == repo_id)
            .order_by(AnalysisModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [_analysis_model_to_entity(r) for r in result.scalars().all()]

    async def create(self, analysis: Analysis) -> Analysis:
        model = AnalysisModel(
            id=analysis.id, repository_id=analysis.repository_id,
            user_id=analysis.user_id, status=analysis.status.value,
        )
        self._session.add(model)
        await self._session.flush()
        return _analysis_model_to_entity(model)

    async def update_status(
        self, analysis_id: uuid.UUID, status: AnalysisStatus,
        error_message: Optional[str] = None,
    ) -> None:
        values: dict = {"status": status.value}
        if error_message is not None:
            values["error_message"] = error_message
        stmt = update(AnalysisModel).where(AnalysisModel.id == analysis_id).values(**values)
        await self._session.execute(stmt)
        await self._session.flush()

    async def save_results(self, analysis: Analysis) -> None:
        stmt = (
            update(AnalysisModel)
            .where(AnalysisModel.id == analysis.id)
            .values(
                status=analysis.status.value,
                total_commits=analysis.total_commits,
                avg_commit_size=analysis.avg_commit_size,
                commits_per_day=analysis.commits_per_day,
                commits_per_month=analysis.commits_per_month,
                code_churn_additions=analysis.code_churn_additions,
                code_churn_deletions=analysis.code_churn_deletions,
                avg_time_between_commits_hours=analysis.avg_time_between_commits_hours,
                bus_factor=analysis.bus_factor,
                language_distribution=analysis.language_distribution,
                ai_summary=analysis.ai_summary,
                readme_quality_score=analysis.readme_quality_score,
                readme_quality_feedback=analysis.readme_quality_feedback,
                detected_tech_stack=analysis.detected_tech_stack,
                architecture_analysis=analysis.architecture_analysis,
                completed_at=analysis.completed_at,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()


# ── Commit Stats Repository ─────────────────────────────────────────────────


class SqlAlchemyCommitStatsRepository(CommitStatsRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def bulk_create(self, commits: Sequence[CommitStats]) -> None:
        models = [
            CommitStatsModel(
                id=c.id, analysis_id=c.analysis_id, sha=c.sha,
                author_name=c.author_name, author_email=c.author_email,
                message=c.message, additions=c.additions, deletions=c.deletions,
                files_changed=c.files_changed, committed_at=c.committed_at,
            )
            for c in commits
        ]
        self._session.add_all(models)
        await self._session.flush()

    async def get_by_analysis(self, analysis_id: uuid.UUID) -> Sequence[CommitStats]:
        stmt = select(CommitStatsModel).where(CommitStatsModel.analysis_id == analysis_id)
        result = await self._session.execute(stmt)
        return [_commit_model_to_entity(r) for r in result.scalars().all()]


# ── Contributor Repository ───────────────────────────────────────────────────


class SqlAlchemyContributorRepository(ContributorRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def bulk_upsert(self, contributors: Sequence[Contributor]) -> None:
        models = [
            ContributorModel(
                id=c.id, analysis_id=c.analysis_id, username=c.username,
                avatar_url=c.avatar_url, total_commits=c.total_commits,
                additions=c.additions, deletions=c.deletions,
                first_commit_at=c.first_commit_at, last_commit_at=c.last_commit_at,
            )
            for c in contributors
        ]
        self._session.add_all(models)
        await self._session.flush()

    async def get_by_analysis(self, analysis_id: uuid.UUID) -> Sequence[Contributor]:
        stmt = select(ContributorModel).where(ContributorModel.analysis_id == analysis_id)
        result = await self._session.execute(stmt)
        return [_contributor_model_to_entity(r) for r in result.scalars().all()]
