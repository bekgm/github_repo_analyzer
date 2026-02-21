"""
Celery tasks — the actual background work.

Design decisions
────────────────
• Each task is a *thin wrapper* that sets up a sync DB session (Celery
  workers are synchronous) and delegates to the analysis pipeline.
• We use asyncio.run() inside the task because our GitHub client and
  Gemini client are async. This is a pragmatic choice that avoids
  running a separate async Celery worker.
• The task updates Analysis status at every major phase so the frontend
  can show progress.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime

import structlog
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.domain.entities import AnalysisStatus, CommitStats
from app.domain.services import (
    aggregate_contributors,
    calculate_bus_factor,
    compute_avg_commit_size,
    compute_avg_time_between_commits,
    compute_code_churn,
    compute_commits_per_day,
    compute_commits_per_month,
)
from app.infrastructure.database.models import (
    AnalysisModel,
    CommitStatsModel,
    ContributorModel,
)
from app.infrastructure.external.gemini_client import GeminiClient
from app.infrastructure.external.github_client import GitHubClient
from app.infrastructure.cache.redis_cache import RedisCache, CachedGitHubClient
from app.infrastructure.jobs.celery_app import celery_app

logger = structlog.get_logger(__name__)


def _get_sync_session() -> Session:
    settings = get_settings()
    engine = create_engine(settings.sync_database_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine)
    return factory()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def run_analysis_task(self, analysis_id: str, owner: str, name: str) -> dict:
    """
    Main background job: fetch commits, compute metrics, run AI analysis.

    Returns a summary dict for Celery result backend inspection.
    """
    logger.info("Starting analysis task", analysis_id=analysis_id, repo=f"{owner}/{name}")
    session = _get_sync_session()

    try:
        # Mark IN_PROGRESS
        _update_status(session, analysis_id, AnalysisStatus.IN_PROGRESS)

        # ── Run the async pipeline in a one-shot event loop ──
        result = asyncio.run(_analyze(analysis_id, owner, name))

        # ── Persist results ──────────────────────────────────
        _save_results(session, analysis_id, result)
        _update_status(session, analysis_id, AnalysisStatus.COMPLETED)

        logger.info("Analysis completed", analysis_id=analysis_id)
        return {"status": "completed", "analysis_id": analysis_id}

    except Exception as exc:
        logger.error("Analysis failed", analysis_id=analysis_id, error=str(exc))
        _update_status(session, analysis_id, AnalysisStatus.FAILED, str(exc))
        # Let Celery retry on transient errors
        if isinstance(exc, ExternalServiceError) and self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        return {"status": "failed", "analysis_id": analysis_id, "error": str(exc)}

    finally:
        session.close()


async def _analyze(analysis_id: str, owner: str, name: str) -> dict:
    """
    Async pipeline:
    1. Fetch commits + details (with caching)
    2. Compute metrics
    3. AI analysis
    """
    aid = uuid.UUID(analysis_id)

    gh_raw = GitHubClient()
    cache = RedisCache()
    gh = CachedGitHubClient(gh_raw, cache)
    gemini = GeminiClient()

    # ── Step 1: Fetch data ───────────────────────────────────────────────
    commits_list = await gh.get_commits(owner, name, max_pages=5)
    languages_raw = await gh.get_languages(owner, name)
    readme = await gh.get_readme(owner, name)
    file_paths = await gh.get_repo_tree(owner, name)

    # Fetch detail for each commit (concurrent batches to avoid rate limits)
    commit_entities: list[CommitStats] = []
    shas = [c.get("sha", "") for c in commits_list[:100] if c.get("sha")]

    # Fetch in batches of 10 concurrently
    import asyncio
    BATCH_SIZE = 10
    for i in range(0, len(shas), BATCH_SIZE):
        batch = shas[i : i + BATCH_SIZE]
        details = await asyncio.gather(
            *(gh.get_commit_detail(owner, name, sha) for sha in batch)
        )
        for detail in details:
            commit_entities.append(gh_raw.parse_commit(detail, aid))

    # ── Step 2: Compute metrics ──────────────────────────────────────────
    additions, deletions = compute_code_churn(commit_entities)
    contributors = aggregate_contributors(commit_entities, aid)

    total_bytes = sum(languages_raw.values()) or 1
    language_distribution = {
        lang: round(bytes_ / total_bytes * 100, 2) for lang, bytes_ in languages_raw.items()
    }

    metrics = {
        "total_commits": len(commit_entities),
        "avg_commit_size": compute_avg_commit_size(commit_entities),
        "commits_per_day": compute_commits_per_day(commit_entities),
        "commits_per_month": compute_commits_per_month(commit_entities),
        "code_churn_additions": additions,
        "code_churn_deletions": deletions,
        "avg_time_between_commits_hours": compute_avg_time_between_commits(commit_entities),
        "bus_factor": calculate_bus_factor(contributors),
        "language_distribution": language_distribution,
    }

    # ── Step 3: AI analysis — single consolidated call (1 API request) ──
    ai_results = {
        "ai_summary": None,
        "readme_quality_score": None,
        "readme_quality_feedback": None,
        "detected_tech_stack": [],
        "architecture_analysis": None,
    }
    try:
        ai_results = await gemini.analyze_repository(
            f"{owner}/{name}", None, language_distribution, file_paths, readme
        )
    except Exception as ai_err:
        logger.warning("AI analysis skipped (non-fatal)", error=str(ai_err))

    await cache.close()

    return {
        **metrics,
        **ai_results,
        "commit_entities": commit_entities,
        "contributors": contributors,
    }


# ── DB helpers (synchronous, for Celery worker) ─────────────────────────────


def _update_status(
    session: Session, analysis_id: str, status: AnalysisStatus,
    error_message: str | None = None,
) -> None:
    analysis = session.get(AnalysisModel, uuid.UUID(analysis_id))
    if analysis:
        analysis.status = status.value
        if error_message:
            analysis.error_message = error_message
        if status == AnalysisStatus.COMPLETED:
            analysis.completed_at = datetime.utcnow()
        session.commit()


def _save_results(session: Session, analysis_id: str, result: dict) -> None:
    aid = uuid.UUID(analysis_id)
    analysis = session.get(AnalysisModel, aid)
    if not analysis:
        return

    # Metrics
    analysis.total_commits = result["total_commits"]
    analysis.avg_commit_size = result["avg_commit_size"]
    analysis.commits_per_day = result["commits_per_day"]
    analysis.commits_per_month = result["commits_per_month"]
    analysis.code_churn_additions = result["code_churn_additions"]
    analysis.code_churn_deletions = result["code_churn_deletions"]
    analysis.avg_time_between_commits_hours = result["avg_time_between_commits_hours"]
    analysis.bus_factor = result["bus_factor"]
    analysis.language_distribution = result["language_distribution"]

    # AI
    analysis.ai_summary = result["ai_summary"]
    analysis.readme_quality_score = result["readme_quality_score"]
    analysis.readme_quality_feedback = result["readme_quality_feedback"]
    analysis.detected_tech_stack = result["detected_tech_stack"]
    analysis.architecture_analysis = result["architecture_analysis"]

    # Commit stats
    for c in result.get("commit_entities", []):
        model = CommitStatsModel(
            id=c.id, analysis_id=aid, sha=c.sha,
            author_name=c.author_name, author_email=c.author_email,
            message=c.message, additions=c.additions, deletions=c.deletions,
            files_changed=c.files_changed, committed_at=c.committed_at,
        )
        session.add(model)

    # Contributors
    for contrib in result.get("contributors", []):
        model = ContributorModel(
            id=contrib.id, analysis_id=aid, username=contrib.username,
            avatar_url=contrib.avatar_url, total_commits=contrib.total_commits,
            additions=contrib.additions, deletions=contrib.deletions,
            first_commit_at=contrib.first_commit_at,
            last_commit_at=contrib.last_commit_at,
        )
        session.add(model)

    session.commit()
