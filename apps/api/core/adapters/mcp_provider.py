import json
from typing import Any

import httpx

from apps.api.core.interfaces import ToolCall, ToolProvider, ToolResult


class MCPToolProvider(ToolProvider):
    def __init__(self, server_url: str, api_key: str | None = None) -> None:
        self._server_url = server_url.rstrip("/")
        self._headers: dict[str, str] = {}
        if api_key:
            self._headers["Authorization"] = f"Bearer {api_key}"

    async def list_tools(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._server_url}/tools/list",
                headers=self._headers,
                timeout=10,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            tools: list[dict[str, Any]] = data.get("tools", [])
            return tools

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self._server_url}/tools/execute",
                    headers=self._headers,
                    json={
                        "name": tool_call.name,
                        "arguments": tool_call.arguments,
                        "id": tool_call.id,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data: dict[str, Any] = response.json()
                return ToolResult(
                    tool_call_id=tool_call.id or "",
                    output=json.dumps(data.get("output", {})),
                    is_error=data.get("is_error", False),
                )
            except httpx.HTTPError as e:
                return ToolResult(
                    tool_call_id=tool_call.id or "",
                    output=str(e),
                    is_error=True,
                )
