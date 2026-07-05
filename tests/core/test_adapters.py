from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from apps.api.core.adapters import MCPToolProvider, PDFDocumentLoader, RedisCacheProvider
from apps.api.core.adapters.redis_memory import RedisMemoryProvider
from apps.api.core.interfaces import MemoryEntry, MessageRole, ToolCall


class TestPDFDocumentLoader:
    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_load_returns_document(self) -> None:
        loader = PDFDocumentLoader()
        docs = await loader.load("/fake/path.pdf")
        assert len(docs) == 1
        assert docs[0].id == "/fake/path.pdf"

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_load_stream_yields_documents(self) -> None:
        loader = PDFDocumentLoader()
        results = [d async for d in loader.load_stream("/fake/path.pdf")]
        assert len(results) == 1


class TestRedisCacheProvider:
    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_set_and_get_missing(self) -> None:
        fake_redis = AsyncMock()
        fake_redis.get.return_value = None

        with patch(
            "apps.api.core.adapters.redis_cache.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisCacheProvider("redis://localhost:6379/0")
            result = await provider.get("missing_key")
            assert result is None
            fake_redis.get.assert_awaited_once_with("missing_key")

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_set_and_get_json_roundtrip(self) -> None:
        fake_redis = AsyncMock()

        with patch(
            "apps.api.core.adapters.redis_cache.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisCacheProvider("redis://localhost:6379/0")

            # Test set
            test_data = {"key": "value", "num": 42}
            await provider.set("my_key", test_data)

            # Extract what was passed to redis.set
            args, _ = fake_redis.set.call_args
            saved_data = args[1]

            # Mock get to return what was set
            fake_redis.get.return_value = saved_data

            # Test get
            result = await provider.get("my_key")
            assert result == test_data

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_corrupted_cache_entry_handling(self) -> None:
        fake_redis = AsyncMock()
        # Return invalid JSON
        fake_redis.get.return_value = b"{invalid_json"

        with patch(
            "apps.api.core.adapters.redis_cache.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisCacheProvider("redis://localhost:6379/0")

            # Test get
            result = await provider.get("corrupt_key")

            # Should treat as cache miss
            assert result is None

            # Should have deleted the corrupted key
            fake_redis.delete.assert_awaited_once_with("corrupt_key")


class TestMCPToolProvider:
    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_execute_success(self) -> None:
        async def mock_post(_self: object, _url: str, **_kwargs: object) -> MagicMock:
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {"output": {"result": "ok"}, "is_error": False}
            return response

        with patch("httpx.AsyncClient.post", new=mock_post):
            provider = MCPToolProvider("http://localhost:9000")
            result = await provider.execute(
                ToolCall(name="test_tool", arguments={"arg1": "val1"}, id="call_1")
            )
            assert result.is_error is False
            assert "ok" in result.output

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_execute_http_error(self) -> None:
        async def mock_post(_self: object, _url: str, **_kwargs: object) -> None:
            raise httpx.HTTPError("connection failed")

        with patch("httpx.AsyncClient.post", new=mock_post):
            provider = MCPToolProvider("http://localhost:9000")
            result = await provider.execute(ToolCall(name="test_tool", arguments={}, id="call_2"))
            assert result.is_error is True


class TestRedisMemoryProvider:
    """
    Validates that RedisMemoryProvider serializes each MemoryEntry exactly
    once via the outer json.dumps(data). The 'metadata' field must be stored
    as a native dict inside the JSON object, not as a pre-serialized string
    requiring a second json.loads on read.
    """

    @pytest.mark.asyncio
    async def test_metadata_roundtrip_single_serialization(self) -> None:
        import json

        stored: list[str] = []

        fake_redis = AsyncMock()
        fake_redis.lrange.return_value = []  # pre-populate empty

        async def fake_rpush(_key: str, value: str) -> None:
            stored.append(value)
            # Also update lrange to return the stored items
            fake_redis.lrange.return_value = stored[-50:]

        fake_redis.rpush.side_effect = fake_rpush

        with patch(
            "apps.api.core.adapters.redis_memory.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisMemoryProvider("redis://localhost:6379/0")

            entry = MemoryEntry(
                role=MessageRole.USER,
                content="What is your return policy?",
                timestamp=1_700_000_000.0,
                metadata={"source": "widget", "user_id": "u-123"},
            )
            await provider.add("conv-1", entry)

            # Inspect what was stored in Redis
            assert stored, "Nothing was pushed to Redis."
            raw = stored[0]

            # Must be valid JSON — outer json.dumps called exactly once
            parsed = json.loads(raw)

            # metadata must be a native dict, NOT a JSON string
            assert isinstance(parsed["metadata"], dict), (
                "Double serialization detected: metadata stored as string. "
                f"Got: {type(parsed['metadata']).__name__}"
            )
            assert parsed["metadata"] == entry.metadata

    @pytest.mark.asyncio
    async def test_add_then_get_preserves_metadata(self) -> None:
        """
        Full round-trip: add an entry, then get it back and confirm
        metadata is returned as a dict with the correct values.
        """

        stored: list[str] = []

        fake_redis = AsyncMock()

        async def fake_rpush(_key: str, value: str) -> None:
            stored.append(value)

        async def fake_lrange(_key: str, _start: int, _end: int) -> list[str]:
            return stored

        fake_redis.rpush.side_effect = fake_rpush
        fake_redis.lrange.side_effect = fake_lrange

        with patch(
            "apps.api.core.adapters.redis_memory.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisMemoryProvider("redis://localhost:6379/0")

            entry = MemoryEntry(
                role=MessageRole.ASSISTANT,
                content="Our return policy is 30 days.",
                timestamp=1_700_000_001.0,
                metadata={"confidence": 0.95, "sources": ["doc-1", "doc-2"]},
            )
            await provider.add("conv-1", entry)
            results = await provider.get("conv-1")

            assert len(results) == 1
            recovered = results[0]
            assert recovered.role == MessageRole.ASSISTANT
            assert recovered.content == entry.content
            assert recovered.timestamp == entry.timestamp

            # The critical assertion: metadata must be the original dict
            assert isinstance(
                recovered.metadata, dict
            ), f"Expected dict, got {type(recovered.metadata).__name__}"
            assert recovered.metadata == entry.metadata
