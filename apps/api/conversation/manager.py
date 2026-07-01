import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.conversation.models import Conversation, Message
from apps.api.core.adapters import ResilientCacheProvider
from apps.api.core.config import settings
from apps.api.core.interfaces import LLMMessage, MessageRole

logger = structlog.get_logger()


class ConversationManager:
    def __init__(self) -> None:
        self._cache = ResilientCacheProvider(settings.redis_url)

    async def create_conversation(
        self, db: AsyncSession, tenant_id: str, user_id: str | None = None
    ) -> Conversation:
        conv = Conversation(id=str(uuid.uuid4()), tenant_id=tenant_id, user_id=user_id)
        db.add(conv)
        await db.flush()
        cache_key = self._conv_cache_key(conv.id)
        await self._cache.set(
            cache_key,
            {"id": conv.id, "tenant_id": tenant_id, "status": "active"},
            ttl=3600,
        )
        logger.info("conversation_created", conversation_id=conv.id, tenant_id=tenant_id)
        return conv

    async def get_conversation(self, db: AsyncSession, conversation_id: str) -> Conversation | None:
        cache_key = self._conv_cache_key(conversation_id)
        cached = await self._cache.get(cache_key)
        if cached:
            return Conversation(**cached)
        result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalar_one_or_none()
        if conv:
            await self._cache.set(
                cache_key,
                {"id": conv.id, "tenant_id": conv.tenant_id, "status": conv.status},
                ttl=3600,
            )
        return conv

    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: MessageRole,
        content: str,
        model: str | None = None,
        token_count: int | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role.value,
            content=content,
            model=model,
            token_count=token_count,
        )
        db.add(msg)
        await db.flush()
        return msg

    async def get_messages(
        self, db: AsyncSession, conversation_id: str, limit: int = 50
    ) -> list[Message]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_history(self, db: AsyncSession, conversation_id: str) -> list[LLMMessage]:
        messages = await self.get_messages(db, conversation_id)
        return [LLMMessage(role=MessageRole(m.role), content=m.content) for m in messages]

    def _conv_cache_key(self, conversation_id: str) -> str:
        return f"conv:{conversation_id}"
