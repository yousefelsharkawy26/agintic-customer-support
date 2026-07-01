from __future__ import annotations

from typing import Any

import structlog

from apps.api.core.interfaces import MemoryEntry, MemoryProvider, MessageRole

logger = structlog.get_logger()


class WorkingMemory:
    def __init__(self, ttl: int = 300) -> None:
        self._store: dict[str, list[dict[str, Any]]] = {}
        self._ttl = ttl

    async def set(self, conversation_id: str, key: str, value: Any) -> None:
        if conversation_id not in self._store:
            self._store[conversation_id] = []
        self._store[conversation_id].append({"key": key, "value": value})

    async def get(self, conversation_id: str, key: str) -> Any | None:
        entries = self._store.get(conversation_id, [])
        for e in reversed(entries):
            if e["key"] == key:
                return e["value"]
        return None

    async def clear(self, conversation_id: str) -> None:
        self._store.pop(conversation_id, None)


class ConversationMemory:
    def __init__(self, provider: MemoryProvider) -> None:
        self._provider = provider

    async def add(self, conversation_id: str, role: MessageRole, content: str) -> None:
        entry = MemoryEntry(role=role, content=content, timestamp=0)
        await self._provider.add(conversation_id, entry)

    async def get(self, conversation_id: str, limit: int = 50) -> list[MemoryEntry]:
        return await self._provider.get(conversation_id, limit=limit)


class KnowledgeMemory:
    def __init__(self, retriever: Any) -> None:
        self._retriever = retriever

    async def search(
        self, query: str, tenant_id: str = "default", top_k: int = 5
    ) -> list[dict[str, Any]]:
        docs = await self._retriever.retrieve(query=query, tenant_id=tenant_id, top_k=top_k)
        return [
            {
                "content": d.content,
                "score": getattr(d, "score", None),
                "source": d.metadata.get("source", ""),
            }
            for d in docs
        ]
