import json
import uuid
from collections.abc import Awaitable, Callable
from contextlib import suppress

import redis.asyncio as aioredis  # type: ignore[import-untyped]

from apps.api.core.config import settings
from apps.api.core.interfaces import Event, EventBus


class RedisStreamEventBus(EventBus):
    def __init__(self, redis_url: str, stream_maxlen: int = 10000) -> None:
        self._redis = aioredis.from_url(
            redis_url,
            decode_responses=True,
            max_connections=settings.redis_pool_size,
            socket_keepalive=settings.redis_socket_keepalive,
            socket_connect_timeout=settings.redis_socket_connect_timeout,
        )
        self._stream_maxlen = stream_maxlen
        self._handlers: dict[str, list[Callable[[Event], Awaitable[None]]]] = {}

    async def publish(self, event: Event) -> None:
        event_id = event.correlation_id or str(uuid.uuid4())
        payload = {
            "type": event.type,
            "data": json.dumps(event.data),
            "tenant_id": event.tenant_id or "",
            "correlation_id": event_id,
            "event_id": str(uuid.uuid4()),
        }
        await self._redis.xadd(
            f"events:{event.type}",
            payload,  # type: ignore[arg-type]
            maxlen=self._stream_maxlen,
        )
        await self._redis.xadd(
            "events:all",
            payload,  # type: ignore[arg-type]
            maxlen=self._stream_maxlen,
        )
        await self._dispatch_local(event)

    async def _dispatch_local(self, event: Event) -> None:
        handlers = self._handlers.get(event.type, []) + self._handlers.get("*", [])
        for handler in handlers:
            with suppress(Exception):
                await handler(event)

    async def subscribe(self, event_type: str, handler: Callable[[Event], Awaitable[None]]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def unsubscribe(
        self, event_type: str, handler: Callable[[Event], Awaitable[None]]
    ) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
