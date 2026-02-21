
from __future__ import annotations

import asyncio
import re
from datetime import datetime
from typing import Any, Optional

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.domain.entities import CommitStats, Repository

logger = structlog.get_logger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubClient:
    """Thin async wrapper around GitHub REST API v3."""

    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        self._token = token or settings.github_token
        self._headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            self._headers["Authorization"] = f"Bearer {self._token}"

    # ── Low-level request ────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        reraise=True,
    )
    async def _get(self, url: str, params: dict | None = None) -> httpx.Response:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self._headers, params=params)
            if resp.status_code == 404:
                raise ExternalServiceError("GitHub", "Repository not found")
            if resp.status_code == 403:
                raise ExternalServiceError("GitHub", "Rate limit exceeded or forbidden")
            resp.raise_for_status()
            return resp

    # ── Pagination ───────────────────────────────────────────────────────

    async def _get_paginated(
        self, url: str, *, params: dict | None = None, max_pages: int = 10
    ) -> list[dict[str, Any]]:
        """Follow GitHub's Link header pagination up to *max_pages*."""
        params = params or {}
        params.setdefault("per_page", 100)
        all_items: list[dict[str, Any]] = []

        current_url: str | None = url
        page = 0
        while current_url and page < max_pages:
            resp = await self._get(current_url, params if page == 0 else None)
            data = resp.json()
            if isinstance(data, list):
                all_items.extend(data)
            else:
                all_items.append(data)

            # Parse Link header for next page
            current_url = self._parse_next_link(resp.headers.get("Link", ""))
            page += 1

        return all_items

    @staticmethod
    def _parse_next_link(link_header: str) -> str | None:
        if not link_header:
            return None
        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        return match.group(1) if match else None

    # ── Public methods ───────────────────────────────────────────────────

    async def get_repository(self, owner: str, name: str) -> dict[str, Any]:
        """GET /repos/{owner}/{name}"""
        resp = await self._get(f"{GITHUB_API}/repos/{owner}/{name}")
        return resp.json()

    async def get_commits(
        self, owner: str, name: str, *, max_pages: int = 5
    ) -> list[dict[str, Any]]:
        """GET /repos/{owner}/{name}/commits  (paginated)"""
        return await self._get_paginated(
            f"{GITHUB_API}/repos/{owner}/{name}/commits",
            max_pages=max_pages,
        )

    async def get_commit_detail(self, owner: str, name: str, sha: str) -> dict[str, Any]:
        """GET /repos/{owner}/{name}/commits/{sha} — includes file-level stats."""
        resp = await self._get(f"{GITHUB_API}/repos/{owner}/{name}/commits/{sha}")
        return resp.json()

    async def get_languages(self, owner: str, name: str) -> dict[str, int]:
        """GET /repos/{owner}/{name}/languages — bytes per language."""
        resp = await self._get(f"{GITHUB_API}/repos/{owner}/{name}/languages")
        return resp.json()

    async def get_readme(self, owner: str, name: str) -> str | None:
        """Return decoded README content or None if absent."""
        try:
            resp = await self._get(
                f"{GITHUB_API}/repos/{owner}/{name}/readme",
                params={"ref": "HEAD"},
            )
            data = resp.json()
            import base64
            return base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
        except ExternalServiceError:
            return None

    async def get_repo_tree(self, owner: str, name: str, branch: str = "HEAD") -> list[str]:
        """Return list of file paths (flat) from the repo tree."""
        try:
            resp = await self._get(
                f"{GITHUB_API}/repos/{owner}/{name}/git/trees/{branch}",
                params={"recursive": "1"},
            )
            tree = resp.json().get("tree", [])
            return [item["path"] for item in tree if item["type"] == "blob"]
        except ExternalServiceError:
            return []

    # ── Helpers ──────────────────────────────────────────────────────────

    def parse_repo_metadata(self, data: dict[str, Any]) -> Repository:
        """Map GitHub API response → domain Repository entity."""
        return Repository(
            owner=data.get("owner", {}).get("login", ""),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description"),
            default_branch=data.get("default_branch", "main"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            language=data.get("language"),
        )

    def parse_commit(self, data: dict[str, Any], analysis_id) -> CommitStats:
        """Map a single commit detail response → domain CommitStats entity."""
        commit_info = data.get("commit", {})
        author = commit_info.get("author", {})
        stats = data.get("stats", {})
        return CommitStats(
            analysis_id=analysis_id,
            sha=data.get("sha", ""),
            author_name=author.get("name", "unknown"),
            author_email=author.get("email", ""),
            message=commit_info.get("message", ""),
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            files_changed=len(data.get("files", [])),
            committed_at=datetime.fromisoformat(
                author.get("date", "2000-01-01T00:00:00Z").replace("Z", "+00:00")
            ),
        )
