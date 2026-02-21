"""
Rate-limiting middleware using slowapi (backed by Redis).

Approach: per-IP sliding window, configurable via RATE_LIMIT_PER_MINUTE.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri=settings.redis_url,
    strategy="fixed-window",
)
