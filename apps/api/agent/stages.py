from __future__ import annotations

import re

import structlog

from apps.api.agent.interfaces import AgentContext, PipelineStage

logger = structlog.get_logger()


class Preprocessor(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        ctx.metadata["original_query"] = ctx.query
        ctx.query = ctx.query.strip()
        ctx.metadata["query_length"] = len(ctx.query)
        ctx.metadata["has_pii"] = self._detect_pii(ctx.query)
        logger.info("preprocessor_done", query_length=len(ctx.query))
        return ctx

    def _detect_pii(self, text: str) -> bool:
        patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            r"\b\d{16}\b",
        ]
        return any(re.search(p, text) for p in patterns)


class IntentClassifier(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        q = ctx.query.lower()
        faq_keywords = ["hours", "shipping", "return", "payment", "policy", "faq"]
        escalation_keywords = ["human", "agent", "manager", "speak to", "talk to", "real person"]
        tool_keywords = ["ticket", "create", "open", "issue", "problem", "bug", "refund"]

        if any(k in q for k in escalation_keywords):
            ctx.intent = "escalation"
        elif any(k in q for k in tool_keywords):
            ctx.intent = "needs_tool"
        elif any(k in q for k in faq_keywords):
            ctx.intent = "faq"
        else:
            ctx.intent = "complex"

        logger.info("intent_classified", intent=ctx.intent, query=q[:50])
        return ctx


class Planner(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        intent_plan: dict[str, list[str]] = {
            "faq": ["respond"],
            "complex": ["retrieve", "reason", "respond"],
            "needs_tool": ["retrieve", "reason", "execute_tool", "respond"],
            "escalation": ["execute_tool", "respond"],
        }
        ctx.plan = intent_plan.get(ctx.intent, ["respond"])
        logger.info("plan_created", intent=ctx.intent, plan=ctx.plan)
        return ctx


class Retriever(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        if "retrieve" not in ctx.plan:
            return ctx
        ctx.metadata["retrieved"] = True
        logger.info("retriever_stage", query=ctx.query[:50])
        return ctx


class Reasoner(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        if "reason" not in ctx.plan:
            return ctx
        ctx.metadata["reasoned"] = True
        logger.info("reasoner_stage", plan=ctx.plan)
        return ctx


class ToolExecutor(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        if "execute_tool" not in ctx.plan:
            return ctx
        ctx.metadata["tool_executed"] = True
        logger.info("tool_executor_stage")
        return ctx


class Composer(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        logger.info("composer_stage")
        return ctx


class Postprocessor(PipelineStage):
    async def run(self, ctx: AgentContext) -> AgentContext:
        safety_issues: list[str] = []
        prohibited = [
            r"\bhttp[s]?://(?!.*(?:support|help|docs)\.)",
            r"(?i)\b(?:hack|exploit|bypass)\b",
        ]
        for pattern in prohibited:
            if re.search(pattern, ctx.query):
                safety_issues.append("potentially_harmful_content")
                break
        ctx.metadata["safety_issues"] = safety_issues
        logger.info("postprocessor_done", safety_issues=safety_issues)
        return ctx
