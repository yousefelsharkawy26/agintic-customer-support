from apps.api.core.interfaces import ToolCall
from apps.api.tools.registry import ToolSpec, get_tool, list_tools, register_tool, rollback_tool
from apps.api.tools.tools import HARDCODED_TOOLS, create_ticket, get_faq


class TestToolRegistry:
    def test_register_and_get(self):
        spec = ToolSpec(name="test_tool", version="1.0", description="A test", input_schema={})
        register_tool(spec)
        assert get_tool("test_tool") is not None

    def test_list_public_tools(self):
        tools = list_tools("public")
        assert all(t.visibility == "public" for t in tools)

    def test_rollback(self):
        spec1 = ToolSpec(name="rb_tool", version="1.0", description="v1", input_schema={})
        spec2 = ToolSpec(name="rb_tool", version="2.0", description="v2", input_schema={})
        register_tool(spec1)
        register_tool(spec2)
        rolled = rollback_tool("rb_tool", "1.0")
        assert rolled is not None
        assert rolled.version == "1.0"


class TestHardcodedTools:
    async def test_create_ticket(self):
        tc = ToolCall(name="create_ticket", arguments={"subject": "Bug report"}, id="1")
        result = await create_ticket(tc)
        assert "ticket_id" in result.output

    async def test_get_faq_finds_match(self):
        tc = ToolCall(name="get_faq", arguments={"query": "return"}, id="1")
        result = await get_faq(tc)
        assert "return" in result.output.lower()

    async def test_get_faq_no_match(self):
        tc = ToolCall(name="get_faq", arguments={"query": "nonexistent_xyz"}, id="1")
        result = await get_faq(tc)
        assert "No matching" in result.output

    def test_hardcoded_tools_registered(self):
        assert "create_ticket" in HARDCODED_TOOLS
        assert "escalate_human" in HARDCODED_TOOLS
        assert "get_faq" in HARDCODED_TOOLS
        assert "search_docs" in HARDCODED_TOOLS
