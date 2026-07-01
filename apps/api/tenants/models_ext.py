import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.tenants.models import Base


class TenantConfig(Base):
    __tablename__ = "tenant_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    llm_api_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    llm_model: Mapped[str] = mapped_column(String(100), default="gpt-4o")
    embeddings_model: Mapped[str] = mapped_column(String(100), default="text-embedding-3-large")
    daily_request_limit: Mapped[int] = mapped_column(Integer, default=1000)
    monthly_token_limit: Mapped[int] = mapped_column(Integer, default=1_000_000)
    branding: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
