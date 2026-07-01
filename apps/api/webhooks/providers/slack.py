from __future__ import annotations

import hashlib
import hmac
import time
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog
from pydantic import BaseModel

logger = structlog.get_logger()


class SlackConfig(BaseModel):
    webhook_url: str
    signing_secret: str | None = None
    channel: str | None = None


def verify_slack_signature(body: bytes, headers: dict[str, str], secret: str) -> bool:
    timestamp = headers.get("X-Slack-Request-Timestamp", "")
    sig = headers.get("X-Slack-Signature", "")
    if not timestamp or not sig:
        return False
    now = time.time()
    if abs(now - float(timestamp)) > 300:
        return False
    base = f"v0:{timestamp}:{body.decode()}"
    expected = "v0=" + hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


async def send_slack_message(
    config: SlackConfig,
    text: str,
    attachments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"text": text}
    if attachments:
        payload["attachments"] = attachments
    if config.channel:
        payload["channel"] = config.channel

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(config.webhook_url, json=payload)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def send_conversation_notification(
    config: SlackConfig,
    conversation_id: str,
    tenant_name: str,
    user_message: str,
) -> None:
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "New Support Conversation"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Tenant:*\n{tenant_name}"},
                {"type": "mrkdwn", "text": f"*Conversation:*\n<fakeUrl.to|{conversation_id[:8]}>"},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"> {user_message[:300]}"},
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"🕐 {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                }
            ],
        },
    ]

    await send_slack_message(config, text="", attachments=[{"blocks": blocks}])
