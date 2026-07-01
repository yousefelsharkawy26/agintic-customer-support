import hashlib
import re
from dataclasses import dataclass

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.interfaces import Document, LLMMessage, MessageRole, SearchFilter
from apps.api.rag.indexer import DocumentIndexer
from apps.api.rag.models import IndexedDocument
from apps.api.rag.reranker import CohereReranker, NoopReranker, Reranker
from apps.api.rag.retriever import HybridRetriever

logger = structlog.get_logger()


@dataclass
class RAGContext:
    chunks: list[Document]
    query: str


class RAGPipeline:
    def __init__(self, use_reranker: bool = True) -> None:
        self._retriever = HybridRetriever()
        self._reranker: Reranker = CohereReranker() if use_reranker else NoopReranker()
        self._indexer = DocumentIndexer()

    async def retrieve(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 10,
        rerank_top_k: int = 5,
        filters: list[SearchFilter] | None = None,
    ) -> RAGContext:
        docs = await self._retriever.retrieve(
            query=query, tenant_id=tenant_id, top_k=top_k, filters=filters
        )
        reranked = await self._reranker.rerank(query, docs, top_k=rerank_top_k)
        return RAGContext(chunks=reranked, query=query)

    @staticmethod
    def format_context_static(ctx: RAGContext, max_chars: int = 8000) -> str:
        parts: list[str] = []
        total = 0
        for i, chunk in enumerate(ctx.chunks):
            header = f"[Source {i + 1}]"
            content = f"{header}\n{chunk.content}"
            total += len(content)
            if total > max_chars:
                break
            parts.append(content)
        return "\n\n".join(parts)

    @staticmethod
    def build_messages_static(
        _query: str, history: list[LLMMessage], ctx: RAGContext | None = None
    ) -> list[LLMMessage]:
        system_parts = ["You are a helpful customer support assistant."]
        if ctx and ctx.chunks:
            context = RAGPipeline.format_context_static(ctx)
            system_parts.append("\nUse the following context to answer:\n" + context)
            system_parts.append(
                "\nCite sources inline like [Source 1], [Source 2]. "
                "If the context doesn't answer the question, say so."
            )
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content="\n".join(system_parts)),
            *history,
        ]
        return messages

    @staticmethod
    def extract_citations(response: str) -> list[str]:
        sources = re.findall(r"\[Source (\d+)\]", response)
        return list(sorted(set(sources), key=int))

    async def index_document(
        self,
        db: AsyncSession,
        text: str,
        source_type: str,
        tenant_id: str = "default",
        source_url: str | None = None,
        title: str | None = None,
    ) -> int:
        checksum = hashlib.sha256(text.encode()).hexdigest()
        result = await db.execute(
            select(IndexedDocument).where(
                IndexedDocument.checksum == checksum,
                IndexedDocument.tenant_id == tenant_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            logger.info("document_already_indexed", checksum=checksum, tenant_id=tenant_id)
            return existing.chunk_count

        chunk_count = await self._indexer.ingest_text(text, source_type, tenant_id)
        if chunk_count:
            doc_record = IndexedDocument(
                document_id=hashlib.md5(text.encode()).hexdigest()[:16],
                tenant_id=tenant_id,
                source_type=source_type,
                source_url=source_url,
                title=title,
                chunk_count=chunk_count,
                checksum=checksum,
            )
            db.add(doc_record)
            logger.info("document_indexed", tenant_id=tenant_id, chunks=chunk_count)
        return chunk_count
