import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.tenants.models import Base


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    server_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    api_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    transport: Mapped[str] = mapped_column(String(20), default="http")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    timeout_ms: Mapped[int] = mapped_column(Integer, default=30000)
    health_status: Mapped[str] = mapped_column(String(20), default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ToolAuditLog(Base):
    __tablename__ = "tool_audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    arguments: Mapped[str] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(Text, nullable=True)
    is_error: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
