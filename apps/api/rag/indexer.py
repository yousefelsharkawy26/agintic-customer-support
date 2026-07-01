import uuid
from typing import Any

import structlog

from apps.api.core.adapters import OpenAIEmbeddingProvider
from apps.api.core.adapters.qdrant_store import QdrantVectorStore
from apps.api.core.config import settings
from apps.api.core.interfaces import VectorRecord
from apps.api.events.redis_bus import RedisStreamEventBus
from apps.api.rag.chunkers import Chunker, RecursiveChunker
from apps.api.rag.loaders import HTMLLoader, MarkdownLoader

logger = structlog.get_logger()


class DocumentIndexer:
    def __init__(self) -> None:
        self._store = QdrantVectorStore(url=settings.qdrant_url)
        self._embeddings = OpenAIEmbeddingProvider(api_key=settings.openai_api_key)
        self._chunker: Chunker = RecursiveChunker()
        self._event_bus: RedisStreamEventBus | None = None

    def set_event_bus(self, bus: RedisStreamEventBus) -> None:
        self._event_bus = bus

    def _collection_name(self, tenant_id: str) -> str:
        return f"{tenant_id}__docs"

    async def ingest_text(
        self,
        text: str,
        source_type: str,
        tenant_id: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        collection = self._collection_name(tenant_id)

        loader = MarkdownLoader() if source_type == "markdown" else HTMLLoader()
        docs = await loader.load(text)
        if not docs:
            return 0

        doc = docs[0]
        if metadata:
            doc.metadata.update(metadata)
        doc.metadata["tenant_id"] = tenant_id
        doc.metadata["source_type"] = source_type

        chunks = self._chunker.chunk(doc)
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        vectors = await self._embeddings.embed(texts)

        records: list[VectorRecord] = []
        for chunk, vector in zip(chunks, vectors, strict=False):
            records.append(
                VectorRecord(
                    id=chunk.id,
                    vector=vector,
                    payload={
                        "content": chunk.content,
                        **chunk.metadata,
                    },
                )
            )

        if records:
            await self._store.ensure_collection(collection, len(vectors[0]), hybrid=False)
            await self._store.upsert(collection, records)

        if self._event_bus:
            from apps.api.core.interfaces import Event

            await self._event_bus.publish(
                Event(
                    type="doc.indexed",
                    data={
                        "tenant_id": tenant_id,
                        "source_type": source_type,
                        "chunk_count": len(records),
                        "document_id": doc.id,
                    },
                    tenant_id=tenant_id,
                    correlation_id=str(uuid.uuid4()),
                )
            )

        logger.info(
            "documents_indexed",
            tenant_id=tenant_id,
            source_type=source_type,
            chunk_count=len(records),
        )
        return len(records)

    async def delete_document(self, document_id: str, tenant_id: str = "default") -> None:
        collection = self._collection_name(tenant_id)
        await self._store.delete_by_filter(collection, "source_id", document_id)
        logger.info("document_deleted", document_id=document_id, tenant_id=tenant_id)
