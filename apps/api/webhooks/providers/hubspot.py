from __future__ import annotations

from typing import Any

import httpx
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class HubSpotConfig(BaseModel):
    access_token: str
    portal_id: str | None = None


async def create_or_update_contact(
    config: HubSpotConfig,
    email: str,
    properties: dict[str, str],
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            json={"properties": {**properties, "email": email}},
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code == 409:
            contact_id = response.json().get("id")
            if contact_id:
                return await update_contact(config, contact_id, properties)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def update_contact(
    config: HubSpotConfig,
    contact_id: str,
    properties: dict[str, str],
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.patch(
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
            json={"properties": properties},
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def create_ticket(
    config: HubSpotConfig,
    subject: str,
    description: str,
    category: str = "customer_support",
) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.hubapi.com/crm/v3/objects/tickets",
            json={
                "properties": {
                    "hs_ticket_priority": "MEDIUM",
                    "hs_pipeline": "0",
                    "hs_ticket_category": category,
                    "subject": subject,
                    "content": description,
                }
            },
            headers={
                "Authorization": f"Bearer {config.access_token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
