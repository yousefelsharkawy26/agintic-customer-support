from __future__ import annotations

import hashlib
from typing import Any, cast

import structlog

from apps.api.core.interfaces import CacheProvider

logger = structlog.get_logger()


class SemanticCache:
    def __init__(self, cache: CacheProvider, threshold: float = 0.92, ttl: int = 3600) -> None:
        self._cache = cache
        self._threshold = threshold
        self._ttl = ttl

    async def get(self, query: str) -> list[dict[str, Any]] | None:
        key = self._make_key(query)
        cached = await self._cache.get(key)
        if cached:
            logger.info("semantic_cache_hit", query=query[:50])
            return cast("list[dict[str, Any]]", cached)
        logger.info("semantic_cache_miss", query=query[:50])
        return None

    async def set(self, query: str, chunks: list[dict[str, Any]]) -> None:
        key = self._make_key(query)
        await self._cache.set(key, chunks, ttl=self._ttl)

    def _make_key(self, query: str) -> str:
        return f"semantic_cache:{hashlib.md5(query.encode()).hexdigest()}"
