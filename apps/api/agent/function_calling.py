from __future__ import annotations

from typing import Any

from apps.api.tools.registry import ToolSpec


def tool_spec_to_openai_tool(spec: ToolSpec) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": spec.name,
            "description": spec.description,
            "parameters": spec.input_schema,
        },
    }


def tool_specs_to_openai_tools(specs: list[ToolSpec]) -> list[dict[str, Any]]:
    return [tool_spec_to_openai_tool(s) for s in specs]


def parse_tool_call(response_message: dict[str, Any]) -> list[dict[str, Any]]:
    tool_calls = response_message.get("tool_calls", [])
    return [
        {
            "id": tc.get("id", ""),
            "name": tc.get("function", {}).get("name", ""),
            "arguments": tc.get("function", {}).get("arguments", "{}"),
        }
        for tc in tool_calls
    ]
