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
from apps.api.agent.models import AgentModel
from apps.api.agent.pipeline import AgentPipeline
from apps.api.auth.deps import get_current_tenant, get_tenant_db
from apps.api.conversation.manager import ConversationManager
from apps.api.core.interfaces import LLMConfig, LLMMessage, LLMProvider, MessageRole
from apps.api.guardrails.guardrails import run_input_guardrails, run_output_guardrails
from apps.api.models.router import ModelRouter
from apps.api.rag.pipeline import RAGContext, RAGPipeline
from apps.api.rag.semantic_cache import SemanticCache

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1", tags=["chat"], dependencies=[Depends(get_current_tenant)])

_semantic_cache: SemanticCache | None = None
_agent_pipeline: AgentPipeline | None = None


def _get_pipeline() -> AgentPipeline:
    global _agent_pipeline
    if _agent_pipeline is None:
        _agent_pipeline = AgentPipeline()
    return _agent_pipeline


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    agent_id: str | None = None
    message: str
    stream: bool = True
    user_id: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "How do I reset my password?",
                "agent_id": "agt_abc123",
                "stream": True,
                "user_id": "user-123",
            }
        }
    }


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    model: str
    citations: list[str] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "conversation_id": "conv-abc-123",
                "message": "To reset your password, go to Settings > Security...",
                "model": "gpt-4o",
                "citations": ["doc-password-reset.pdf"],
            }
        }
    }


@router.post(
    "/chat",
    response_model=None,
    summary="Send a message to the AI assistant",
    description=(
        "Send a message and receive a streaming or non-streaming response.\n\n"
        "**Streaming** (`stream: true`): Returns Server-Sent Events with "
        "tokens as they're generated. Event types:\n"
        '- `data: {"type": "token", "content": "..."}`\n'
        '- `data: {"type": "done", "conversation_id": "...", "citations": [...]}`\n\n'
        "**Non-streaming** (`stream: false`): Returns the full response as JSON."
    ),
    responses={
        200: {
            "description": "Streaming response (SSE) or JSON response",
            "content": {
                "text/event-stream": {
                    "example": (
                        'data: {"type": "token", "content": "To "}\n\n'
                        'data: {"type": "token", "content": "reset "}\n\n'
                        'data: {"type": "done", "conversation_id": "conv-abc-123", "citations": []}\n\n'
                    )
                }
            },
        }
    },
)
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> StreamingResponse | ChatResponse:
    tenant_id = tenant["tenant_id"]
    guardrail_result = run_input_guardrails(body.message)
    if not guardrail_result.passed:
        return ChatResponse(
            conversation_id="",
            message="I couldn't process that request due to safety concerns.",
            model="guardrail",
        )
    sanitized = guardrail_result.sanitized_input or body.message

    # ------------------------------------------------------------------
    # Resolve the Agent configuration
    # ------------------------------------------------------------------
    agent_config: AgentModel | None = None
    if body.agent_id:
        from sqlalchemy import select

        agent_result = await db.execute(
            select(AgentModel).where(
                AgentModel.id == body.agent_id,
                AgentModel.tenant_id == tenant_id,
            )
        )
        agent_config = agent_result.scalar_one_or_none()
        if not agent_config:
            raise HTTPException(status_code=404, detail="Agent not found")

    mgr = ConversationManager()
    rag = RAGPipeline()

    if body.conversation_id:
        conv = await mgr.get_conversation(db, body.conversation_id, tenant_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = await mgr.create_conversation(db, tenant_id, body.user_id, agent_id=body.agent_id)

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
        yield f"data: {
            json.dumps(
                {
                    'type': 'done',
                    'conversation_id': conv_id,
                    'citations': citations,
                }
            )
        }\n\n"


@router.get(
    "/conversations",
    summary="List conversations",
)
async def list_conversations(
    limit: int = 50,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> list[dict[str, Any]]:
    tenant_id = tenant["tenant_id"]
    from sqlalchemy import select

    from apps.api.conversation.models import Conversation

    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == tenant_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )
    convs = result.scalars().all()
    return [
        {
            "id": c.id,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "customer_name": "Customer",  # Mock for now
            "customer_email": "customer@example.com",
            "messages_count": 0,
            "agent_id": "system",
        }
        for c in convs
    ]


@router.get(
    "/conversations/{conversation_id}",
    summary="Get conversation history",
    description=(
        "Retrieve the full message history of a conversation, including "
        "user messages, assistant responses, models used, and timestamps."
    ),
)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_tenant_db),
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    mgr = ConversationManager()
    conv = await mgr.get_conversation(db, conversation_id, tenant["tenant_id"])
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await mgr.get_messages(db, conversation_id)
    return {
        "conversation_id": conv.id,
        "status": conv.status,
        "customer_name": "Customer",
        "customer_email": "customer@example.com",
        "messages_count": len(messages),
        "agent_id": "system",
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }
