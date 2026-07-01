from __future__ import annotations

import asyncio
import json
from typing import Any, cast

import httpx
import structlog

from apps.api.core.interfaces import ToolCall, ToolResult

logger = structlog.get_logger()


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._last_failure_time = 0.0
        self._open = False

    async def call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        if self._open:
            if asyncio.get_event_loop().time() - self._last_failure_time > self._recovery_timeout:
                self._open = False
                self._failure_count = 0
            else:
                raise RuntimeError("Circuit breaker is open")
        try:
            result = await fn(*args, **kwargs)
            self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = asyncio.get_event_loop().time()
            if self._failure_count >= self._failure_threshold:
                self._open = True
                logger.warning("circuit_breaker_opened", failures=self._failure_count)
            raise e


class MCPTransport:
    def __init__(self, server_url: str, api_key: str | None = None) -> None:
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=server_url.rstrip("/"), headers=headers, timeout=30.0
        )

    async def list_tools(self) -> list[dict[str, Any]]:
        response = await self._client.post("/tools/list")
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return cast("list[dict[str, Any]]", data.get("tools", []))

    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        response = await self._client.post(
            "/tools/execute",
            json={
                "name": tool_call.name,
                "arguments": tool_call.arguments,
                "id": tool_call.id,
            },
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return ToolResult(
            tool_call_id=tool_call.id or "",
            output=json.dumps(data.get("output", {})),
            is_error=data.get("is_error", False),
        )

    async def health(self) -> bool:
        try:
            response = await self._client.get("/health", timeout=5.0)
            return bool(response.is_success)
        except Exception:
            return False

    def set_timeout(self, timeout: float) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._client.base_url,
            headers=dict(self._client.headers),
            timeout=timeout,
        )


class MCPClient:
    def __init__(self, server_url: str, api_key: str | None = None) -> None:
        self._transport = MCPTransport(server_url, api_key)
        self._breaker = CircuitBreaker()

    async def list_tools(self) -> list[dict[str, Any]]:
        result = await self._breaker.call(self._transport.list_tools)
        return cast("list[dict[str, Any]]", result)

    async def execute(self, tool_call: ToolCall, timeout: float = 30.0) -> ToolResult:
        self._transport.set_timeout(timeout)
        result = await self._breaker.call(self._transport.execute_tool, tool_call)
        return cast(ToolResult, result)

    async def health(self) -> bool:
        try:
            return await self._transport.health()
        except Exception:
            return False
