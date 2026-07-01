from unittest.mock import AsyncMock, patch

import pytest

from apps.api.core.interfaces import Event
from apps.api.events.redis_bus import RedisStreamEventBus


class TestRedisStreamEventBus:
    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_subscribe_and_dispatch(self) -> None:
        handler = AsyncMock()
        fake_redis = AsyncMock()

        with patch("apps.api.events.redis_bus.aioredis.from_url", return_value=fake_redis):
            bus = RedisStreamEventBus("redis://localhost:6379/0")
            await bus.subscribe("test.event", handler)
            event = Event(type="test.event", data={"msg": "hello"}, tenant_id="t1")
            await bus.publish(event)

            fake_redis.xadd.assert_called()
            handler.assert_awaited_once_with(event)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_wildcard_handler(self) -> None:
        handler = AsyncMock()
        fake_redis = AsyncMock()

        with patch("apps.api.events.redis_bus.aioredis.from_url", return_value=fake_redis):
            bus = RedisStreamEventBus("redis://localhost:6379/0")
            await bus.subscribe("*", handler)
            event = Event(type="any.event", data={})
            await bus.publish(event)

            handler.assert_awaited_once_with(event)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_unsubscribe(self) -> None:
        handler = AsyncMock()
        fake_redis = AsyncMock()

        with patch("apps.api.events.redis_bus.aioredis.from_url", return_value=fake_redis):
            bus = RedisStreamEventBus("redis://localhost:6379/0")
            await bus.subscribe("test.event", handler)
            await bus.unsubscribe("test.event", handler)
            event = Event(type="test.event", data={})
            await bus.publish(event)

            handler.assert_not_awaited()
