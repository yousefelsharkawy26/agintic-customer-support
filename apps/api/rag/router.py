from typing import Any

import structlog
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.deps import get_current_tenant, get_tenant_db
from apps.api.rag.models import IndexedDocument
from apps.api.rag.pipeline import RAGPipeline

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/documents", tags=["rag"], dependencies=[Depends(get_current_tenant)]
)


class DocumentIngestRequest(BaseModel):
    content: str
    source_type: str = "markdown"
    source_url: str | None = None
    title: str | None = None


class DocumentResponse(BaseModel):
    id: str
    title: str | None
    source_type: str
    chunk_count: int
    version: int


@router.post("/ingest")
async def ingest_document(
    body: DocumentIngestRequest,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    tenant_id = tenant["tenant_id"]
    pipeline = RAGPipeline()
    chunk_count = await pipeline.index_document(
        db=db,
        text=body.content,
        source_type=body.source_type,
        tenant_id=tenant_id,
        source_url=body.source_url,
        title=body.title,
    )
    return {"chunks_indexed": chunk_count, "tenant_id": tenant_id}


@router.get("/")
async def list_documents(
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    tenant_id = tenant["tenant_id"]
    result = await db.execute(
        select(IndexedDocument)
        .where(
            IndexedDocument.tenant_id == tenant_id,
            IndexedDocument.is_active == True,  # noqa: E712
        )
        .order_by(IndexedDocument.created_at.desc())
    )
    docs = result.scalars().all()
    return {
        "documents": [
            {
                "id": d.document_id,
                "title": d.title,
                "source_type": d.source_type,
                "chunk_count": d.chunk_count,
                "version": d.version,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ]
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, str]:
    tenant_id = tenant["tenant_id"]
    pipeline = RAGPipeline()
    await pipeline._indexer.delete_document(document_id, tenant_id)
    return {"status": "deleted", "document_id": document_id}
