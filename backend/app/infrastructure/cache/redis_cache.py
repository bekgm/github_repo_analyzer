"""
Redis caching layer.

Design decisions
────────────────
• Uses native redis.asyncio for non-blocking cache access.
• Cache keys are namespaced: `gra:<domain>:<identifier>` to avoid
  collisions and make invalidation patterns easy (SCAN + DEL).
• TTL defaults to 1 hour for GitHub API responses — balances freshness
  with rate-limit conservation.
• All values are JSON-serialised; the module is transparent to callers.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import redis.asyncio as aioredis
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

_PREFIX = "gra"


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self._redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )

    async def get(self, domain: str, key: str) -> Optional[Any]:
        full_key = f"{_PREFIX}:{domain}:{key}"
        raw = await self._redis.get(full_key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set(
        self, domain: str, key: str, value: Any, ttl_seconds: int = 3600
    ) -> None:
        full_key = f"{_PREFIX}:{domain}:{key}"
        await self._redis.set(full_key, json.dumps(value, default=str), ex=ttl_seconds)

    async def delete(self, domain: str, key: str) -> None:
        full_key = f"{_PREFIX}:{domain}:{key}"
        await self._redis.delete(full_key)

    async def invalidate_domain(self, domain: str) -> int:
        """Delete all keys for a given domain. Returns count deleted."""
        pattern = f"{_PREFIX}:{domain}:*"
        deleted = 0
        async for key in self._redis.scan_iter(match=pattern, count=100):
            await self._redis.delete(key)
            deleted += 1
        return deleted

    async def close(self) -> None:
        await self._redis.close()


# ── Cached GitHub Client Wrapper ─────────────────────────────────────────────


class CachedGitHubClient:
    """
    Wraps GitHubClient with Redis caching.

    Transparently returns cached GitHub API responses when available,
    falling back to the live API on cache miss.
    """

    def __init__(self, github_client, cache: RedisCache):
        self._gh = github_client
        self._cache = cache

    async def get_repository(self, owner: str, name: str) -> dict:
        cache_key = f"repo:{owner}/{name}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            logger.debug("Cache hit", key=cache_key)
            return cached
        data = await self._gh.get_repository(owner, name)
        await self._cache.set("github", cache_key, data, ttl_seconds=3600)
        return data

    async def get_commits(self, owner: str, name: str, *, max_pages: int = 5) -> list[dict]:
        cache_key = f"commits:{owner}/{name}:p{max_pages}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            logger.debug("Cache hit", key=cache_key)
            return cached
        data = await self._gh.get_commits(owner, name, max_pages=max_pages)
        await self._cache.set("github", cache_key, data, ttl_seconds=1800)
        return data

    async def get_commit_detail(self, owner: str, name: str, sha: str) -> dict:
        cache_key = f"commit_detail:{owner}/{name}:{sha}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            return cached
        data = await self._gh.get_commit_detail(owner, name, sha)
        # Commit details are immutable — cache for 24 hours
        await self._cache.set("github", cache_key, data, ttl_seconds=86400)
        return data

    async def get_languages(self, owner: str, name: str) -> dict[str, int]:
        cache_key = f"languages:{owner}/{name}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            return cached
        data = await self._gh.get_languages(owner, name)
        await self._cache.set("github", cache_key, data, ttl_seconds=3600)
        return data

    async def get_readme(self, owner: str, name: str) -> str | None:
        cache_key = f"readme:{owner}/{name}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            return cached
        data = await self._gh.get_readme(owner, name)
        if data:
            await self._cache.set("github", cache_key, data, ttl_seconds=3600)
        return data

    async def get_repo_tree(self, owner: str, name: str, branch: str = "HEAD") -> list[str]:
        cache_key = f"tree:{owner}/{name}:{branch}"
        cached = await self._cache.get("github", cache_key)
        if cached:
            return cached
        data = await self._gh.get_repo_tree(owner, name, branch)
        await self._cache.set("github", cache_key, data, ttl_seconds=3600)
        return data
