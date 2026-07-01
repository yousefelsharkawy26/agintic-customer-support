import math
from collections import Counter

from apps.api.core.adapters import OpenAIEmbeddingProvider
from apps.api.core.adapters.qdrant_store import QdrantVectorStore
from apps.api.core.config import settings
from apps.api.core.interfaces import Document, SearchFilter


class HybridRetriever:
    def __init__(self) -> None:
        self._store = QdrantVectorStore(url=settings.qdrant_url)
        self._embeddings = OpenAIEmbeddingProvider(api_key=settings.openai_api_key)

    def collection_name(self, tenant_id: str) -> str:
        return self._store._collection_name("docs", tenant_id)

    async def retrieve(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 10,
        filters: list[SearchFilter] | None = None,
    ) -> list[Document]:
        dense_vector = await self._embeddings.embed_query(query)
        sparse_vector = self._bm25_sparse(query)

        collection = self.collection_name(tenant_id)

        try:
            result = await self._store.search_hybrid(
                collection=collection,
                dense_vector=dense_vector,
                sparse_vector=sparse_vector,
                limit=top_k,
                filters=filters,
            )
        except Exception:
            result = await self._store.search(
                collection=collection,
                vector=dense_vector,
                limit=top_k,
                filters=filters,
            )

        return [
            Document(
                id=r.id,
                content=r.payload.get("content", ""),
                metadata={k: v for k, v in r.payload.items() if k != "content"},
            )
            for r in result.records
        ]

    async def retrieve_dense(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 10,
        filters: list[SearchFilter] | None = None,
    ) -> list[Document]:
        dense_vector = await self._embeddings.embed_query(query)
        collection = self.collection_name(tenant_id)
        result = await self._store.search(
            collection=collection, vector=dense_vector, limit=top_k, filters=filters
        )
        return [
            Document(
                id=r.id,
                content=r.payload.get("content", ""),
                metadata={k: v for k, v in r.payload.items() if k != "content"},
            )
            for r in result.records
        ]

    def _bm25_sparse(self, query: str, k1: float = 1.5, b: float = 0.75) -> dict[int, float]:
        terms = query.lower().split()
        term_freq = Counter(terms)
        n_terms = len(terms)
        sparse: dict[int, float] = {}
        for _i, (term, count) in enumerate(term_freq.items()):
            tf = count / n_terms if n_terms else 0
            idf = math.log((1 + 1) / (1 + 1))
            score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * 1)))
            sparse[hash(term) % 1000000] = score
        return sparse
