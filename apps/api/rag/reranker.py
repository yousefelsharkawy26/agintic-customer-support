from abc import ABC, abstractmethod

import httpx

from apps.api.core.config import settings
from apps.api.core.interfaces import Document


class Reranker(ABC):
    @abstractmethod
    async def rerank(
        self, query: str, documents: list[Document], top_k: int = 5
    ) -> list[Document]: ...


class CohereReranker(Reranker):
    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.cohere_api_key

    async def rerank(self, query: str, documents: list[Document], top_k: int = 5) -> list[Document]:
        docs = [d.content for d in documents if d.content]
        if not docs:
            return documents[:top_k]

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.cohere.com/v2/rerank",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "rerank-english-v3.0",
                    "query": query,
                    "documents": docs,
                    "top_n": top_k,
                },
            )
            if response.status_code != 200:
                return documents[:top_k]

            data = response.json()
            ranked: list[Document] = []
            for item in data.get("results", []):
                idx = item["index"]
                ranked.append(documents[idx])
            return ranked


class NoopReranker(Reranker):
    async def rerank(
        self, _query: str, documents: list[Document], top_k: int = 5
    ) -> list[Document]:
        return documents[:top_k]
