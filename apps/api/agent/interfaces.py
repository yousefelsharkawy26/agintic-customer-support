from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from apps.api.core.interfaces import LLMMessage


@dataclass
class AgentContext:
    query: str
    conversation_id: str
    tenant_id: str = "default"
    user_id: str | None = None
    messages: list[LLMMessage] = field(default_factory=list)
    retrieved_chunks: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    intent: str = "faq"
    plan: list[str] = field(default_factory=list)
    response: str = ""
    citations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class PipelineStage(ABC):
    @abstractmethod
    async def run(self, ctx: AgentContext) -> AgentContext: ...

    @property
    def name(self) -> str:
        return self.__class__.__name__
