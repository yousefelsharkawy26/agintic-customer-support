from __future__ import annotations

import json
import time
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.tools.models import ToolAuditLog

logger = structlog.get_logger()


async def log_tool_call(
    db: AsyncSession,
    tenant_id: str,
    conversation_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    result: Any,
    is_error: bool = False,
) -> None:
    duration = int((time.time() - time.time()) * 1000)
    log_entry = ToolAuditLog(
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        tool_name=tool_name,
        arguments=json.dumps(arguments),
        result=json.dumps(result) if not isinstance(result, str) else result,
        is_error=is_error,
        duration_ms=duration,
    )
    db.add(log_entry)
    logger.info("tool_call_logged", tool=tool_name, conversation_id=conversation_id)


async def get_tool_audit_logs(
    db: AsyncSession, tenant_id: str, limit: int = 50
) -> list[ToolAuditLog]:
    result = await db.execute(
        select(ToolAuditLog)
        .where(ToolAuditLog.tenant_id == tenant_id)
        .order_by(ToolAuditLog.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
