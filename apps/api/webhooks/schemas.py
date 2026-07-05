from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WebhookConfigCreate(BaseModel):
    provider: str = Field(..., description="slack, zendesk, intercom, or hubspot")
    label: str
    url: str
    secret: str | None = None
    events: list[str] = Field(default_factory=list)
    retry_count: int = 3
    timeout_ms: int = 10000

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "slack",
                "label": "Production Slack",
                "url": "https://hooks.slack.com/services/T00/B00/xxx",
                "secret": "whsec_your_signing_secret",
                "events": ["conversation.created", "ticket.resolved"],
                "retry_count": 3,
                "timeout_ms": 10000,
            }
        }
    }


class WebhookConfigUpdate(BaseModel):
    label: str | None = None
    url: str | None = None
    secret: str | None = None
    events: list[str] | None = None
    is_active: bool | None = None
    retry_count: int | None = None
    timeout_ms: int | None = None


class WebhookConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    provider: str
    label: str
    url: str
    events: list[str]
    is_active: bool
    retry_count: int
    timeout_ms: int
    created_at: datetime
    updated_at: datetime


class WebhookDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    config_id: str
    event_type: str
    status: str
    response_code: int | None
    error: str | None
    attempt: int
    duration_ms: int
    created_at: datetime


class ProviderConfigResponse(BaseModel):
    provider: str
    label: str
    available_events: list[str]
    docs_url: str


class SlackMessage(BaseModel):
    channel: str | None = None
    text: str
    attachments: list[dict[str, Any]] | None = None


class ZendeskTicket(BaseModel):
    subject: str
    description: str
    priority: str = "normal"
    tags: list[str] | None = None


class IntercomEvent(BaseModel):
    event_name: str
    user_id: str | None = None
    metadata: dict[str, Any] | None = None


class HubSpotContact(BaseModel):
    email: str
    properties: dict[str, str]
