import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.tenants.models import Base


class WidgetSession(Base):
    __tablename__ = "widget_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(10), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    meta_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class OfflineMessage(Base):
    __tablename__ = "offline_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="text")
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    client_ts: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
