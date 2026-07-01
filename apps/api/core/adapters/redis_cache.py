import pickle
from typing import Any

import redis.asyncio as aioredis  # type: ignore[import-untyped]

from apps.api.core.interfaces import CacheProvider


class RedisCacheProvider(CacheProvider):
    def __init__(self, redis_url: str) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=False)

    async def get(self, key: str) -> Any | None:
        value = await self._redis.get(key)
        if value is None:
            return None
        return pickle.loads(value)  # type: ignore[arg-type]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        data = pickle.dumps(value)
        if ttl:
            await self._redis.setex(key, ttl, data)
        else:
            await self._redis.set(key, data)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(key))
