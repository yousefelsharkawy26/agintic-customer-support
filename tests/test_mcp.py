import pytest

from apps.api.tools.mcp_client import CircuitBreaker
from apps.api.tools.mcp_schema import mcp_schema_to_tool_spec


class TestCircuitBreaker:
    @pytest.mark.asyncio
    async def test_calls_through_when_closed(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)

        async def ok_fn():
            return "ok"

        result = await cb.call(ok_fn)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)

        async def fail():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await cb.call(fail)
        with pytest.raises(ValueError):
            await cb.call(fail)
        with pytest.raises(RuntimeError, match="Circuit breaker is open"):
            await cb.call(fail)


class TestMCPSchemaAdapter:
    def test_converts_mcp_tool_to_spec(self):
        mcp_tool = {
            "name": "get_weather",
            "description": "Get weather for a location",
            "inputSchema": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        }
        spec = mcp_schema_to_tool_spec(mcp_tool)
        assert spec.name == "get_weather"
        assert spec.description == "Get weather for a location"
        assert "location" in spec.input_schema["properties"]

    def test_converts_multiple_tools(self):
        from apps.api.tools.mcp_schema import mcp_tools_to_tool_specs

        tools = [
            {"name": "tool_a", "inputSchema": {}},
            {"name": "tool_b", "inputSchema": {}},
        ]
        specs = mcp_tools_to_tool_specs(tools)
        assert len(specs) == 2
        assert specs[0].name == "tool_a"
        assert specs[1].name == "tool_b"
