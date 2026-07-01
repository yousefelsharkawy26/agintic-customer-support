from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.agent.interfaces import AgentContext
from apps.api.agent.pipeline import AgentPipeline
from apps.api.conversation.manager import ConversationManager
from apps.api.core.database import get_db
from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, MessageRole
from apps.api.guardrails.guardrails import run_input_guardrails, run_output_guardrails
from apps.api.models.router import ModelRouter
from apps.api.rag.pipeline import RAGContext, RAGPipeline
from apps.api.rag.semantic_cache import SemanticCache

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["chat"])

_semantic_cache: SemanticCache | None = None
_agent_pipeline: AgentPipeline | None = None


def _get_pipeline() -> AgentPipeline:
    global _agent_pipeline
    if _agent_pipeline is None:
        _agent_pipeline = AgentPipeline()
    return _agent_pipeline


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    message: str
    stream: bool = True
    tenant_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    model: str
    citations: list[str] = []


@router.post("/chat")
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse | ChatResponse:
    guardrail_result = run_input_guardrails(body.message)
    if not guardrail_result.passed:
        return ChatResponse(
            conversation_id="",
            message="I couldn't process that request due to safety concerns.",
            model="guardrail",
        )
    sanitized = guardrail_result.sanitized_input or body.message

    mgr = ConversationManager()
    rag = RAGPipeline()
    tenant_id = body.tenant_id or "default"

    if body.conversation_id:
        conv = await mgr.get_conversation(db, body.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = await mgr.create_conversation(db, tenant_id, body.user_id)

    await mgr.add_message(db, conv.id, MessageRole.USER, sanitized)

    history = await mgr.get_history(db, conv.id)
    ctx = await rag.retrieve(sanitized, tenant_id=tenant_id)

    agent_ctx = AgentContext(
        query=sanitized,
        conversation_id=conv.id,
        tenant_id=tenant_id,
        user_id=body.user_id,
        messages=history,
    )
    pipeline = _get_pipeline()
    agent_ctx = await pipeline.run(agent_ctx)

    messages = RAGPipeline.build_messages_static(sanitized, history, ctx)

    model_router = ModelRouter()
    llm = model_router.select(conv.id)

    if body.stream:
        return StreamingResponse(
            _stream_response(mgr, rag, db, llm, conv.id, sanitized, history, ctx),
            media_type="text/event-stream",
            headers={
                "X-Conversation-ID": conv.id,
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    config = LLMConfig()
    response = await llm.generate(messages, config)
    citations = rag.extract_citations(response.content) if ctx.chunks else []
    output_check = run_output_guardrails(response.content)
    final_content = (
        response.content if output_check.passed else "I couldn't generate a safe response."
    )

    await mgr.add_message(
        db,
        conv.id,
        MessageRole.ASSISTANT,
        final_content,
        model=response.model,
        token_count=(response.usage or {}).get("total_tokens"),
    )
    return ChatResponse(
        conversation_id=conv.id,
        message=final_content,
        model=response.model,
        citations=citations,
    )


async def _stream_response(
    mgr: ConversationManager,
    rag: RAGPipeline,
    db: AsyncSession,
    llm: LLMProvider,
    conv_id: str,
    query: str,
    history: list[LLMMessage],
    ctx: RAGContext,
) -> AsyncIterator[str]:
    full_content = ""
    messages = RAGPipeline.build_messages_static(query, history, ctx)
    try:
        async for chunk in llm.generate_stream(messages):
            full_content += chunk
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
    except Exception as e:
        logger.error("stream_error", conversation_id=conv_id, error=str(e))
        yield f"data: {json.dumps({'type': 'error', 'content': 'Streaming error occurred.'})}\n\n"
    finally:
        output_check = run_output_guardrails(full_content)
        final_content = (
            full_content if output_check.passed else "I couldn't generate a safe response."
        )
        citations = rag.extract_citations(full_content) if ctx.chunks else []
        token_count = len(final_content.split())
        await mgr.add_message(
            db,
            conv_id,
            MessageRole.ASSISTANT,
            final_content,
            model=llm.__class__.__name__,
            token_count=token_count,
        )
        yield f"data: {json.dumps({
            'type': 'done',
            'conversation_id': conv_id,
            'citations': citations,
        })}\n\n"


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    mgr = ConversationManager()
    conv = await mgr.get_conversation(db, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await mgr.get_messages(db, conversation_id)
    return {
        "conversation_id": conv.id,
        "status": conv.status,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }
