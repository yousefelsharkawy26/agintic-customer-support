from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from apps.api.core.adapters import MCPToolProvider, PDFDocumentLoader, RedisCacheProvider
from apps.api.core.interfaces import ToolCall


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
    async def test_set_and_get(self) -> None:
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
