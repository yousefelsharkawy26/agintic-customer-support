from __future__ import annotations

import structlog

from apps.api.agent.interfaces import AgentContext, PipelineStage
from apps.api.agent.stages import (
    Composer,
    IntentClassifier,
    Planner,
    Postprocessor,
    Preprocessor,
    Reasoner,
    Retriever,
    ToolExecutor,
)

logger = structlog.get_logger()


class AgentPipeline:
    def __init__(self) -> None:
        self._stages: list[PipelineStage] = [
            Preprocessor(),
            IntentClassifier(),
            Planner(),
            Retriever(),
            Reasoner(),
            ToolExecutor(),
            Composer(),
            Postprocessor(),
        ]

    async def run(self, ctx: AgentContext) -> AgentContext:
        for stage in self._stages:
            ctx = await stage.run(ctx)
            logger.debug("stage_complete", stage=stage.name, intent=ctx.intent)
        return ctx
