from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Prefetch,
    SparseVectorParams,
    VectorParams,
)
from qdrant_client.models import (
    SparseVector as QdrantSparseVector,
)

from apps.api.core.interfaces import SearchFilter, SearchResult, VectorRecord, VectorStore


class QdrantVectorStore(VectorStore):
    def __init__(self, url: str, api_key: str | None = None) -> None:
        self._client = AsyncQdrantClient(url=url, api_key=api_key)

    async def create_collection(self, name: str, vector_size: int, hybrid: bool = False) -> None:
        if hybrid:
            await self._client.create_collection(
                collection_name=name,
                vectors_config={
                    "dense": VectorParams(size=vector_size, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(),
                },
            )
        else:
            await self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def ensure_collection(self, name: str, vector_size: int, hybrid: bool = False) -> None:
        collections = await self._client.get_collections()
        existing = {c.name for c in collections.collections}
        if name not in existing:
            await self.create_collection(name, vector_size, hybrid)

    def _collection_name(self, base: str, tenant_id: str) -> str:
        return f"{tenant_id}__{base}"

    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        points = [PointStruct(id=r.id, vector=r.vector, payload=r.payload) for r in records]
        await self._client.upsert(
            collection_name=collection,
            points=points,
        )

    async def upsert_hybrid(
        self,
        collection: str,
        dense_records: list[VectorRecord],
        sparse_indices: dict[str, list[int]],
        sparse_values: dict[str, list[float]],
    ) -> None:
        points = []
        for r in dense_records:
            indices = sparse_indices.get(r.id)
            values = sparse_values.get(r.id)
            vector: dict[str, Any] = {"dense": r.vector}
            if indices is not None and values is not None:
                vector["sparse"] = QdrantSparseVector(indices=indices, values=values)
            point = PointStruct(
                id=r.id,
                vector=vector,
                payload=r.payload,
            )
            points.append(point)
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
        qdrant_filter = self._build_filter(filters)
        results = await self._client.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
            query_filter=qdrant_filter,
        )
        return self._to_search_result(results.points)

    async def search_hybrid(
        self,
        collection: str,
        dense_vector: list[float],
        sparse_vector: dict[int, float],
        limit: int = 10,
        filters: list[SearchFilter] | None = None,
        _dense_weight: float = 0.7,
        _sparse_weight: float = 0.3,
    ) -> SearchResult:
        qdrant_filter = self._build_filter(filters)
        results = await self._client.query_points(
            collection_name=collection,
            prefetch=[
                Prefetch(query=dense_vector, using="dense", limit=limit * 2),
                Prefetch(
                    query=QdrantSparseVector(
                        indices=list(sparse_vector.keys()),
                        values=list(sparse_vector.values()),
                    ),
                    using="sparse",
                    limit=limit * 2,
                ),
            ],
            query=dense_vector,
            using="dense",
            limit=limit,
            query_filter=qdrant_filter,
        )
        return self._to_search_result(results.points)

    async def delete(self, collection: str, ids: list[str]) -> None:
        await self._client.delete(
            collection_name=collection,
            points_selector=ids,  # type: ignore[arg-type]
        )

    async def delete_collection(self, name: str) -> None:
        await self._client.delete_collection(collection_name=name)

    async def delete_by_filter(self, collection: str, key: str, value: Any) -> None:
        await self._client.delete(
            collection_name=collection,
            points_selector=Filter(must=[FieldCondition(key=key, match=MatchValue(value=value))]),
        )

    def _build_filter(self, filters: list[SearchFilter] | None) -> Filter | None:
        if not filters:
            return None
        conditions: list[Any] = [
            FieldCondition(key=f.key, match=MatchValue(value=f.value)) for f in filters
        ]
        return Filter(must=conditions)

    def _to_search_result(self, points: list[Any]) -> SearchResult:
        return SearchResult(
            records=[
                VectorRecord(
                    id=str(r.id),
                    vector=r.vector or [],  # type: ignore[arg-type]
                    payload=r.payload or {},
                    score=r.score,
                )
                for r in points
            ]
        )
