from __future__ import annotations

from typing import Any

import httpx
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class IntercomConfig(BaseModel):
    access_token: str


async def send_conversation_event(
    config: IntercomConfig,
    event_name: str,
    user_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event_name": event_name,
        "user_id": user_id,
        "created_at": int(__import__("time").time()),
    }
    if metadata:
        payload["metadata"] = metadata

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.intercom.io/events",
            json=payload,
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def create_conversation_note(
    config: IntercomConfig,
    conversation_id: str,
    body: str,
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"https://api.intercom.io/conversations/{conversation_id}/respond",
            json={
                "body": body,
                "type": "note",
            },
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
