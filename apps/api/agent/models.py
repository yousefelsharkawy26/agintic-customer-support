from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.tenants.models import Base


class AgentModel(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: f"agt_{uuid.uuid4().hex[:12]}"
    )
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o")
    status: Mapped[str] = mapped_column(String(50), default="draft")
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)

    # Use JSONB to store arrays of string IDs
    enabled_tool_ids: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")
    knowledge_collection_ids: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default="[]"
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
