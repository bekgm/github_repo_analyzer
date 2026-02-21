"""
Domain services — pure business logic that doesn't belong to a single entity.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Sequence

from app.domain.entities import CommitStats, Contributor


def calculate_bus_factor(contributors: Sequence[Contributor], threshold: float = 0.8) -> int:
    """
    Bus factor = minimum number of contributors whose combined commits
    account for ≥ *threshold* (default 80 %) of total commits.

    If a single person wrote 80 %+ of the code, bus factor = 1.
    An empty repo returns bus factor = 0.

    Algorithm: sort contributors by commit count descending, accumulate
    until the running total crosses the threshold.
    """
    if not contributors:
        return 0

    total = sum(c.total_commits for c in contributors)
    if total == 0:
        return 0

    sorted_contributors = sorted(contributors, key=lambda c: c.total_commits, reverse=True)
    cumulative = 0
    for i, contrib in enumerate(sorted_contributors, start=1):
        cumulative += contrib.total_commits
        if cumulative / total >= threshold:
            return i

    return len(sorted_contributors)


def compute_code_churn(commits: Sequence[CommitStats]) -> tuple[int, int]:
    """Return (total_additions, total_deletions)."""
    additions = sum(c.additions for c in commits)
    deletions = sum(c.deletions for c in commits)
    return additions, deletions


def compute_avg_commit_size(commits: Sequence[CommitStats]) -> float:
    if not commits:
        return 0.0
    total_changes = sum(c.additions + c.deletions for c in commits)
    return total_changes / len(commits)


def compute_avg_time_between_commits(commits: Sequence[CommitStats]) -> float:
    """Average hours between consecutive commits. Returns 0.0 for < 2 commits."""
    if len(commits) < 2:
        return 0.0

    sorted_dates = sorted(c.committed_at for c in commits)
    deltas = [
        (sorted_dates[i + 1] - sorted_dates[i]).total_seconds() / 3600
        for i in range(len(sorted_dates) - 1)
    ]
    return sum(deltas) / len(deltas) if deltas else 0.0


def compute_commits_per_day(commits: Sequence[CommitStats]) -> float:
    """Average commits per calendar day over the repo's active window."""
    if not commits:
        return 0.0
    dates = [c.committed_at for c in commits]
    span_days = max((max(dates) - min(dates)).days, 1)
    return round(len(commits) / span_days, 2)


def compute_commits_per_month(commits: Sequence[CommitStats]) -> float:
    """Average commits per 30-day period based on unique active months."""
    if not commits:
        return 0.0
    months = {(c.committed_at.year, c.committed_at.month) for c in commits}
    num_months = max(len(months), 1)
    return round(len(commits) / num_months, 2)


def aggregate_contributors(commits: Sequence[CommitStats], analysis_id) -> list[Contributor]:
    """Build contributor summary from raw commit data."""
    from collections import defaultdict
    import uuid

    contrib_map: dict[str, dict] = defaultdict(lambda: {
        "total_commits": 0,
        "additions": 0,
        "deletions": 0,
        "dates": [],
    })

    for c in commits:
        # Normalize key to lowercase so "Bekzat" and "bekzat" merge
        raw_key = c.author_email or c.author_name
        key = raw_key.lower() if raw_key else "unknown"
        contrib_map[key]["total_commits"] += 1
        contrib_map[key]["additions"] += c.additions
        contrib_map[key]["deletions"] += c.deletions
        contrib_map[key]["dates"].append(c.committed_at)
        # Keep the name variant with the most commits (first seen wins, overwritten if same)
        if "name" not in contrib_map[key]:
            contrib_map[key]["name"] = c.author_name

    result: list[Contributor] = []
    for email, data in contrib_map.items():
        dates = sorted(data["dates"])
        result.append(
            Contributor(
                id=uuid.uuid4(),
                analysis_id=analysis_id,
                username=data["name"],
                total_commits=data["total_commits"],
                additions=data["additions"],
                deletions=data["deletions"],
                first_commit_at=dates[0] if dates else None,
                last_commit_at=dates[-1] if dates else None,
            )
        )
    return result
