from typing import Any

from apps.api.tools.registry import ToolSpec


def mcp_schema_to_tool_spec(mcp_tool: dict[str, Any], version: str = "1.0.0") -> ToolSpec:
    return ToolSpec(
        name=mcp_tool.get("name", "unknown"),
        version=version,
        description=mcp_tool.get("description", ""),
        input_schema=mcp_tool.get("inputSchema", mcp_tool.get("parameters", {})),
        owner="mcp",
    )


def mcp_tools_to_tool_specs(
    mcp_tools: list[dict[str, Any]], version: str = "1.0.0"
) -> list[ToolSpec]:
    return [mcp_schema_to_tool_spec(t, version) for t in mcp_tools]
