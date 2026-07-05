import json
from typing import Any

import redis.asyncio as aioredis  # type: ignore[import-untyped]
import structlog

from apps.api.core.config import settings
from apps.api.core.interfaces import CacheProvider

logger = structlog.get_logger()


class RedisCacheProvider(CacheProvider):
    def __init__(self, redis_url: str, tenant_prefix: str = "") -> None:
        self._redis = aioredis.from_url(
            redis_url,
            decode_responses=False,
            max_connections=settings.redis_pool_size,
            socket_keepalive=settings.redis_socket_keepalive,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
        )
        self._tenant_prefix = f"{tenant_prefix}:" if tenant_prefix else ""

    def _key(self, key: str) -> str:
        return f"{self._tenant_prefix}{key}"

    async def get(self, key: str) -> Any | None:
        full_key = self._key(key)
        value = await self._redis.get(full_key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logger.warning("redis_cache_corrupted", key=full_key)
            await self._redis.delete(full_key)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        data = json.dumps(value).encode("utf-8")
        if ttl:
            await self._redis.setex(self._key(key), ttl, data)
        else:
            await self._redis.set(self._key(key), data)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(self._key(key)))
