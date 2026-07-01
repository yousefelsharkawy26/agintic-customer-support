import pytest

from apps.api.agent.function_calling import tool_spec_to_openai_tool
from apps.api.agent.interfaces import AgentContext
from apps.api.agent.pipeline import AgentPipeline
from apps.api.agent.stages import (
    IntentClassifier,
    Planner,
    Postprocessor,
    Preprocessor,
)
from apps.api.tools.registry import ToolSpec


class TestAgentPipeline:
    @pytest.mark.asyncio
    async def test_pipeline_runs_full_cycle(self):
        pipeline = AgentPipeline()
        ctx = AgentContext(query="What are your hours?", conversation_id="c1")
        result = await pipeline.run(ctx)
        assert result.metadata.get("original_query") == "What are your hours?"
        assert result.intent in ("faq", "complex")

    @pytest.mark.asyncio
    async def test_pipeline_detects_escalation(self):
        pipeline = AgentPipeline()
        ctx = AgentContext(query="I want to speak to a human agent", conversation_id="c1")
        result = await pipeline.run(ctx)
        assert result.intent == "escalation"
        assert "execute_tool" in result.plan

    @pytest.mark.asyncio
    async def test_pipeline_detects_tool_needed(self):
        pipeline = AgentPipeline()
        ctx = AgentContext(query="Create a ticket for my issue", conversation_id="c1")
        result = await pipeline.run(ctx)
        assert result.intent == "needs_tool"

    @pytest.mark.asyncio
    async def test_preprocessor_strips_and_detects_pii(self):
        stage = Preprocessor()
        ctx = AgentContext(query="  Email me at a@b.com  ", conversation_id="c1")
        result = await stage.run(ctx)
        assert result.query == "Email me at a@b.com"
        assert result.metadata["has_pii"] is True

    @pytest.mark.asyncio
    async def test_intent_classifier_faq(self):
        stage = IntentClassifier()
        ctx = AgentContext(query="What are your shipping hours?", conversation_id="c1")
        result = await stage.run(ctx)
        assert result.intent == "faq"

    @pytest.mark.asyncio
    async def test_planner_creates_plan(self):
        stage = Planner()
        ctx = AgentContext(query="test", conversation_id="c1", intent="complex")
        result = await stage.run(ctx)
        assert "retrieve" in result.plan
        assert "reason" in result.plan

    @pytest.mark.asyncio
    async def test_postprocessor_detects_safety_issues(self):
        stage = Postprocessor()
        ctx = AgentContext(query="How to bypass security", conversation_id="c1")
        result = await stage.run(ctx)
        assert len(result.metadata["safety_issues"]) > 0


class TestFunctionCalling:
    def test_tool_spec_to_openai_tool(self):
        spec = ToolSpec(name="test_fn", version="1.0", description="Test", input_schema={})
        tool = tool_spec_to_openai_tool(spec)
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "test_fn"
