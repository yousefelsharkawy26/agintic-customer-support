from __future__ import annotations

from typing import Any

import structlog
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.utils import hash_api_key, verify_jwt
from apps.api.core.database import get_db
from apps.api.tenants.models import Tenant, TenantApiKey

logger = structlog.get_logger()

security = HTTPBearer(auto_error=False)


async def _resolve_api_key(
    api_key: str,
    db: AsyncSession,
) -> dict[str, Any] | None:
    hashed = hash_api_key(api_key)
    result = await db.execute(
        select(TenantApiKey).where(
            TenantApiKey.key_hash == hashed,
            TenantApiKey.is_active.is_(True),
        )
    )
    key_record = result.scalar_one_or_none()
    if key_record is None:
        return None

    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == key_record.tenant_id, Tenant.is_active.is_(True))
    )
    tenant_row: Any = tenant_result.scalar_one_or_none()
    if tenant_row is None:
        return None

    return {
        "tenant_id": tenant_row.id,
        "tenant_name": tenant_row.name,
        "tenant_slug": tenant_row.slug,
        "plan": tenant_row.plan,
        "auth_method": "api_key",
        "key_id": key_record.id,
    }


async def _resolve_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> dict[str, Any] | None:
    if credentials is None:
        return None
    payload = verify_jwt(credentials.credentials)
    if payload is None:
        return None
    payload["auth_method"] = "bearer"
    return payload


async def get_current_tenant(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    x_api_key: str | None = Header(None, alias="x-api-key"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    if not credentials and not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication. Provide Bearer token or x-api-key header.",
        )

    if credentials:
        payload = await _resolve_bearer_token(credentials)
        if payload:
            request.state.tenant = payload
            return payload

    if x_api_key:
        payload = await _resolve_api_key(x_api_key, db)
        if payload:
            request.state.tenant = payload
            return payload

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
    )


def verify_tenant_access(request_tenant_id: str, auth_tenant: dict[str, Any]) -> None:
    if request_tenant_id and request_tenant_id != auth_tenant["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )


from collections.abc import AsyncIterator

from apps.api.core.database import async_session_factory
from apps.api.core.rls import bind_session_to_tenant


async def get_tenant_db(
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> AsyncIterator[AsyncSession]:
    """Guarantees the session is strictly bound to the authenticated tenant."""
    async with async_session_factory() as session:
        tenant_id = tenant["tenant_id"]
        bind_session_to_tenant(session, tenant_id)

        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise
