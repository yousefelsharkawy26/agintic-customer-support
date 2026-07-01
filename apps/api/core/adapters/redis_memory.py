import json
import time

import redis.asyncio as aioredis  # type: ignore[import-untyped]

from apps.api.core.interfaces import MemoryEntry, MemoryProvider, MessageRole


class RedisMemoryProvider(MemoryProvider):
    def __init__(self, redis_url: str, ttl: int = 86400) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._ttl = ttl

    def _key(self, conversation_id: str) -> str:
        return f"memory:{conversation_id}"

    async def add(self, conversation_id: str, entry: MemoryEntry) -> None:
        data = {
            "role": entry.role.value,
            "content": entry.content,
            "timestamp": entry.timestamp or time.time(),
            "metadata": json.dumps(entry.metadata),
        }
        await self._redis.rpush(self._key(conversation_id), json.dumps(data))
        await self._redis.expire(self._key(conversation_id), self._ttl)

    async def get(self, conversation_id: str, limit: int = 50) -> list[MemoryEntry]:
        raw = await self._redis.lrange(self._key(conversation_id), -limit, -1)
        entries = []
        for item in raw:
            parsed = json.loads(item)
            entries.append(
                MemoryEntry(
                    role=MessageRole(parsed["role"]),
                    content=parsed["content"],
                    timestamp=parsed["timestamp"],
                    metadata=json.loads(parsed.get("metadata", "{}")),
                )
            )
        return entries

    async def clear(self, conversation_id: str) -> None:
        await self._redis.delete(self._key(conversation_id))

    async def search(self, conversation_id: str, query: str, limit: int = 10) -> list[MemoryEntry]:
        entries = await self.get(conversation_id, limit=1000)
        results = [e for e in entries if query.lower() in e.content.lower()]
        return results[:limit]
