import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.auth.utils import create_api_key, hash_api_key
from apps.api.core.config import settings
from apps.api.core.database import get_db
from apps.api.tenants.models import TenantApiKey

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class ApiKeyRequest(BaseModel):
    tenant_id: str
    label: str


class ApiKeyResponse(BaseModel):
    api_key: str
    tenant_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_tenant_api_key(
    body: ApiKeyRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyResponse:
    raw_key = create_api_key()
    hashed = hash_api_key(raw_key)
    api_key_record = TenantApiKey(
        tenant_id=body.tenant_id,
        key_hash=hashed,
        label=body.label,
    )
    db.add(api_key_record)
    logger.info("api_key_created", tenant_id=body.tenant_id, label=body.label)
    return ApiKeyResponse(api_key=raw_key, tenant_id=body.tenant_id)


@router.post("/token", response_model=TokenResponse)
async def get_token(
    api_key: str,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    hashed = hash_api_key(api_key)
    result = await db.execute(
        select(TenantApiKey).where(
            TenantApiKey.key_hash == hashed,
            TenantApiKey.is_active,
        )
    )
    key_record = result.scalar_one_or_none()
    if not key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    import jwt as pyjwt

    token = pyjwt.encode(
        {
            "tenant_id": key_record.tenant_id,
            "key_id": key_record.id,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return TokenResponse(access_token=token)
