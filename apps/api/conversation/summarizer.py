from __future__ import annotations

import structlog

from apps.api.core.interfaces import LLMMessage, MessageRole, ToolProvider

logger = structlog.get_logger()

SUMMARY_THRESHOLD = 10


class ConversationSummarizer:
    def __init__(self, llm: ToolProvider) -> None:
        self._llm = llm

    async def needs_summary(self, messages: list[LLMMessage]) -> bool:
        user_turns = sum(1 for m in messages if m.role == MessageRole.USER)
        return user_turns >= SUMMARY_THRESHOLD

    async def summarize(self, messages: list[LLMMessage]) -> LLMMessage:
        text = "\n".join(f"{m.role.value}: {m.content[:200]}" for m in messages[-20:])
        logger.info("conversation_summarized", turns=len(messages))
        return LLMMessage(
            role=MessageRole.SYSTEM,
            content=f"Previous conversation summary:\n{text[:500]}",
        )
