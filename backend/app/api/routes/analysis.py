"""
API router: Analysis endpoints.

All routes are prefixed with /api/v1 in the main app.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, Request

from app.api.dependencies import (
    get_analysis_detail_use_case,
    get_analyze_use_case,
    get_list_analyses_use_case,
)
from app.api.rate_limit import limiter
from collections import Counter

from app.api.schemas import (
    AIInsightsOut,
    AnalysisDetailOut,
    AnalysisListItem,
    AnalyzeRequest,
    AnalyzeResponse,
    ContributorOut,
    DailyCommit,
    ErrorResponse,
    MetricsOut,
)
from app.usecases.analyze_repository import AnalyzeRepoRequest, AnalyzeRepositoryUseCase
from app.usecases.get_analysis import GetAnalysisUseCase, ListAnalysesUseCase

router = APIRouter(prefix="/analyses", tags=["Analyses"])


# ── POST /analyze ────────────────────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=202,
    responses={422: {"model": ErrorResponse}, 429: {"description": "Rate limit exceeded"}},
    summary="Trigger repository analysis",
    description=(
        "Accepts a GitHub owner/name pair, creates a background analysis job, "
        "and returns immediately with an analysis ID to poll."
    ),
)
@limiter.limit("10/minute")
async def analyze_repository(
    request: Request,
    body: AnalyzeRequest,
    use_case: AnalyzeRepositoryUseCase = Depends(get_analyze_use_case),
) -> AnalyzeResponse:
    result = await use_case.execute(
        AnalyzeRepoRequest(owner=body.owner, name=body.name)
    )
    return AnalyzeResponse(
        analysis_id=result.analysis_id,
        repository_id=result.repository_id,
        status=result.status,
    )


# ── GET /analyses/{analysis_id} ─────────────────────────────────────────────


@router.get(
    "/{analysis_id}",
    response_model=AnalysisDetailOut,
    responses={404: {"model": ErrorResponse}},
    summary="Get analysis details",
)
async def get_analysis(
    analysis_id: uuid.UUID,
    use_case: GetAnalysisUseCase = Depends(get_analysis_detail_use_case),
) -> AnalysisDetailOut:
    data = await use_case.execute(analysis_id)
    analysis = data["analysis"]
    contributors = data["contributors"]
    commits = data["commits"]

    # Compute daily commit counts from stored commit timestamps
    date_counts = Counter(
        c.committed_at.strftime("%m.%d") for c in commits if c.committed_at
    )
    commits_per_date = sorted(
        [DailyCommit(date=d, commits=n) for d, n in date_counts.items()],
        key=lambda x: x.date,
    )

    return AnalysisDetailOut(
        id=analysis.id,
        repository_id=analysis.repository_id,
        status=analysis.status.value if hasattr(analysis.status, "value") else analysis.status,
        error_message=analysis.error_message,
        metrics=MetricsOut(
            total_commits=analysis.total_commits,
            avg_commit_size=analysis.avg_commit_size,
            commits_per_day=analysis.commits_per_day,
            code_churn_additions=analysis.code_churn_additions,
            code_churn_deletions=analysis.code_churn_deletions,
            avg_time_between_commits_hours=analysis.avg_time_between_commits_hours,
            bus_factor=analysis.bus_factor,
            language_distribution=analysis.language_distribution,
            commits_per_date=commits_per_date,
        ),
        ai_insights=AIInsightsOut(
            ai_summary=analysis.ai_summary,
            readme_quality_score=analysis.readme_quality_score,
            readme_quality_feedback=analysis.readme_quality_feedback,
            detected_tech_stack=analysis.detected_tech_stack,
            architecture_analysis=analysis.architecture_analysis,
        ),
        contributors=[
            ContributorOut(
                username=c.username,
                total_commits=c.total_commits,
                additions=c.additions,
                deletions=c.deletions,
                first_commit_at=c.first_commit_at,
                last_commit_at=c.last_commit_at,
            )
            for c in contributors
        ],
        commits_count=data["commits_count"],
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )


# ── GET /analyses?repository_id=... ─────────────────────────────────────────


@router.get(
    "/",
    response_model=list[AnalysisListItem],
    summary="List analyses for a repository",
)
async def list_analyses(
    repository_id: uuid.UUID = Query(..., description="Filter by repository UUID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    use_case: ListAnalysesUseCase = Depends(get_list_analyses_use_case),
) -> list[AnalysisListItem]:
    analyses = await use_case.execute(repository_id, limit=limit, offset=offset)
    return [
        AnalysisListItem(
            id=a.id,
            status=a.status.value if hasattr(a.status, "value") else a.status,
            total_commits=a.total_commits,
            bus_factor=a.bus_factor,
            created_at=a.created_at,
            completed_at=a.completed_at,
        )
        for a in analyses
    ]
