from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from apps.api.rag.semantic_cache import SemanticCache


class TestSemanticCacheSerializationPath:
    """
    Verifies that chunks written via SemanticCache.set() are serialized
    exactly once (by RedisCacheProvider.set → json.dumps) and deserialized
    exactly once (by RedisCacheProvider.get → json.loads).

    SemanticCache itself must NOT call json.dumps/loads; the serialization
    boundary belongs exclusively to RedisCacheProvider.
    """

    @pytest.mark.asyncio
    async def test_set_passes_native_list_to_provider(self) -> None:
        """
        SemanticCache.set() must pass the raw list to the CacheProvider
        without pre-serializing it to a JSON string.
        """
        mock_provider = AsyncMock()
        cache = SemanticCache(cache=mock_provider)

        chunks: list[dict[str, Any]] = [{"id": "1", "content": "hello"}]
        await cache.set("test query", chunks)

        # The value passed to the provider must be the original list, not a string.
        _key, actual_value = mock_provider.set.call_args[0][:2]
        assert isinstance(actual_value, list), (
            "SemanticCache.set() must not pre-serialize chunks; "
            f"expected list, got {type(actual_value).__name__}"
        )
        assert actual_value == chunks

    @pytest.mark.asyncio
    async def test_get_returns_native_list_from_provider(self) -> None:
        """
        SemanticCache.get() must return the object given back by the
        CacheProvider as-is. Since RedisCacheProvider.get() already
        deserializes via json.loads, SemanticCache must NOT call
        json.loads again.
        """
        # Simulate what RedisCacheProvider.get() returns after its own
        # json.loads: a native Python list.
        deserialized_chunks: list[dict[str, Any]] = [{"id": "1", "content": "hello"}]
        mock_provider = AsyncMock()
        mock_provider.get.return_value = deserialized_chunks

        cache = SemanticCache(cache=mock_provider)
        result = await cache.get("test query")

        assert result == deserialized_chunks
        assert isinstance(result, list), (
            "SemanticCache.get() must not re-deserialize; "
            f"expected list, got {type(result).__name__}"
        )

    @pytest.mark.asyncio
    async def test_full_roundtrip_single_serialization(self) -> None:
        """
        End-to-end simulation of the full write/read path through
        RedisCacheProvider (with a real fake-Redis backend) to confirm
        exactly one json.dumps on write and one json.loads on read.

        Path:
          SemanticCache.set()
            → RedisCacheProvider.set() → json.dumps(chunks).encode() → Redis (setex)
            → RedisCacheProvider.get() → json.loads(raw) → native list
          SemanticCache.get()
            → receives native list directly, no further transformation

        Note: SemanticCache always provides a ttl so RedisCacheProvider
        calls setex(), not set().
        """
        import json

        stored: dict[str, bytes] = {}

        fake_redis = AsyncMock()

        # setex(key, ttl, value) — used when ttl is provided
        async def fake_setex(key: str, _ttl: int, value: bytes) -> None:
            stored[key] = value

        # set(key, value) — used when no ttl
        async def fake_set(key: str, value: bytes) -> None:
            stored[key] = value

        async def fake_get(key: str) -> bytes | None:
            return stored.get(key)

        fake_redis.setex.side_effect = fake_setex
        fake_redis.set.side_effect = fake_set
        fake_redis.get.side_effect = fake_get

        from apps.api.core.adapters.redis_cache import RedisCacheProvider

        with patch(
            "apps.api.core.adapters.redis_cache.aioredis.from_url",
            return_value=fake_redis,
        ):
            provider = RedisCacheProvider("redis://localhost:6379/0")
            cache = SemanticCache(cache=provider)

            original_chunks: list[dict[str, Any]] = [
                {"id": "doc-1", "content": "The refund policy is 30 days."},
                {"id": "doc-2", "content": "Contact us at support@example.com."},
            ]

            # Write path: SemanticCache.set → provider.set → json.dumps → Redis (setex)
            await cache.set("refund policy", original_chunks)

            # Verify Redis received valid JSON bytes, not a pickle blob.
            assert stored, "Nothing was written to Redis."
            stored_key = next(iter(stored))
            raw_bytes = stored[stored_key]
            # Must be valid JSON — json.loads must not raise.
            decoded = json.loads(raw_bytes)
            assert decoded == original_chunks, "Redis value does not match original chunks."

            # Read path: provider.get → json.loads → native list → SemanticCache.get
            result = await cache.get("refund policy")

            assert result == original_chunks, "Round-trip value mismatch."
            assert isinstance(result, list), "Returned type must be list, not string."
            # Guard: double-serialization would produce a string here instead of a list
            assert not isinstance(result, str), (
                "Double serialization detected: SemanticCache.get() returned a "
                "JSON string instead of a deserialized list."
            )
