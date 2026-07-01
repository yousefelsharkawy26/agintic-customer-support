from __future__ import annotations

import time
from typing import Any

import structlog

from apps.api.core.interfaces import CacheProvider

logger = structlog.get_logger()


class LocalCacheProvider(CacheProvider):
    def __init__(self, default_ttl: int = 300) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}
        self._default_ttl = default_ttl

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if expires_at is not None and time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.monotonic() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store


class ResilientCacheProvider(CacheProvider):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._primary: CacheProvider | None = None
        self._fallback = LocalCacheProvider(default_ttl=60)
        self._redis_available = True
        self._init_primary()

    def _init_primary(self) -> None:
        try:
            from apps.api.core.adapters.redis_cache import RedisCacheProvider

            self._primary = RedisCacheProvider(self._redis_url)
        except Exception:
            logger.warning("redis_unavailable_using_local_cache")
            self._primary = None
            self._redis_available = False

    async def get(self, key: str) -> Any | None:
        if self._primary and self._redis_available:
            try:
                return await self._primary.get(key)
            except Exception:
                self._redis_available = False
                logger.warning("redis_fallback_to_local", key=key)
        return await self._fallback.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if self._primary and self._redis_available:
            try:
                await self._primary.set(key, value, ttl)
                return
            except Exception:
                self._redis_available = False
        await self._fallback.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        if self._primary and self._redis_available:
            try:
                await self._primary.delete(key)
            except Exception:
                self._redis_available = False
        await self._fallback.delete(key)

    async def exists(self, key: str) -> bool:
        if self._primary and self._redis_available:
            try:
                return await self._primary.exists(key)
            except Exception:
                self._redis_available = False
        return await self._fallback.exists(key)
