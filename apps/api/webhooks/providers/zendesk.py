from __future__ import annotations

from typing import Any

import httpx
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class ZendeskConfig(BaseModel):
    subdomain: str
    email: str
    api_token: str


def _auth_header(config: ZendeskConfig) -> str:
    import base64

    credentials = f"{config.email}/token:{config.api_token}"
    return f"Basic {base64.b64encode(credentials.encode()).decode()}"


async def create_ticket(
    config: ZendeskConfig,
    subject: str,
    description: str,
    priority: str = "normal",
    tags: list[str] | None = None,
    custom_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ticket: dict[str, Any] = {
        "subject": subject,
        "description": description,
        "priority": priority,
    }
    if tags:
        ticket["tags"] = tags
    if custom_fields:
        ticket["custom_fields"] = [{"id": k, "value": v} for k, v in custom_fields.items()]

    url = f"https://{config.subdomain}.zendesk.com/api/v2/tickets.json"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            url,
            json={"ticket": ticket},
            headers={
                "Authorization": _auth_header(config),
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def update_ticket(
    config: ZendeskConfig,
    ticket_id: str,
    comment: str,
    status: str | None = None,
) -> dict[str, Any]:
    ticket: dict[str, Any] = {
        "comment": {"body": comment, "public": False},
    }
    if status:
        ticket["status"] = status

    url = f"https://{config.subdomain}.zendesk.com/api/v2/tickets/{ticket_id}.json"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.put(
            url,
            json={"ticket": ticket},
            headers={
                "Authorization": _auth_header(config),
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
