from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from apps.api.core.interfaces import SearchFilter, SearchResult, VectorRecord, VectorStore


class QdrantVectorStore(VectorStore):
    def __init__(self, url: str, api_key: str | None = None) -> None:
        self._client = AsyncQdrantClient(url=url, api_key=api_key)

    async def create_collection(self, name: str, vector_size: int) -> None:
        await self._client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        points = [PointStruct(id=r.id, vector=r.vector, payload=r.payload) for r in records]
        await self._client.upsert(
            collection_name=collection,
            points=points,
        )

    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 10,
        filters: list[SearchFilter] | None = None,
    ) -> SearchResult:
        qdrant_filter: Filter | None = None
        if filters:
            conditions: list[Any] = [
                FieldCondition(
                    key=f.key,
                    match=MatchValue(value=f.value),
                )
                for f in filters
            ]
            qdrant_filter = Filter(must=conditions)

        results = await self._client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
            query_filter=qdrant_filter,
        )
        return SearchResult(
            records=[
                VectorRecord(
                    id=str(r.id),
                    vector=r.vector or [],  # type: ignore[arg-type]
                    payload=r.payload or {},
                    score=r.score,
                )
                for r in results.points
            ]
        )

    async def delete(self, collection: str, ids: list[str]) -> None:
        await self._client.delete(
            collection_name=collection,
            points_selector=ids,  # type: ignore[arg-type]
        )

    async def delete_collection(self, name: str) -> None:
        await self._client.delete_collection(collection_name=name)
