import hashlib
import secrets
from typing import Any

import jwt as pyjwt

from apps.api.core.config import settings


def create_api_key() -> str:
    return f"cs_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_jwt(token: str) -> dict[str, Any] | None:
    try:
        payload: dict[str, Any] = pyjwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except pyjwt.PyJWTError:
        return None
