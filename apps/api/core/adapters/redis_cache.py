import pickle
from typing import Any

import redis.asyncio as aioredis  # type: ignore[import-untyped]

from apps.api.core.interfaces import CacheProvider


class RedisCacheProvider(CacheProvider):
    def __init__(self, redis_url: str, tenant_prefix: str = "") -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=False)
        self._tenant_prefix = f"{tenant_prefix}:" if tenant_prefix else ""

    def _key(self, key: str) -> str:
        return f"{self._tenant_prefix}{key}"

    async def get(self, key: str) -> Any | None:
        value = await self._redis.get(self._key(key))
        if value is None:
            return None
        return pickle.loads(value)  # type: ignore[arg-type]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        data = pickle.dumps(value)
        if ttl:
            await self._redis.setex(self._key(key), ttl, data)
        else:
            await self._redis.set(self._key(key), data)

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(self._key(key)))
