# Webhooks

Configure outbound webhooks to deliver events to external systems (Slack, Zendesk, Intercom, HubSpot).

## Overview

Webhooks are configured per-tenant. Each webhook specifies:

- **Provider**: `slack`, `zendesk`, `intercom`, or `hubspot`
- **URL**: The destination endpoint
- **Events**: Which events to deliver (e.g., `conversation.created`)
- **Secret**: Used to sign deliveries with HMAC-SHA256

Events are delivered with a `X-Signature-256` header containing the HMAC-SHA256 signature of the request body. This allows you to verify the request came from our API.

## Creating a Webhook

```bash
curl -X POST http://localhost:8080/api/v1/webhooks/configs \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "slack",
    "label": "Production Slack",
    "url": "https://hooks.slack.com/services/T00/B00/xxx",
    "secret": "whsec_your_signing_secret",
    "events": ["conversation.created", "ticket.resolved"],
    "retry_count": 3,
    "timeout_ms": 10000
  }'
```

Response:

```json
{
  "id": "wh-abc-123",
  "tenant_id": "my-tenant",
  "provider": "slack",
  "label": "Production Slack",
  "url": "https://hooks.slack.com/services/T00/B00/xxx",
  "events": ["conversation.created", "ticket.resolved"],
  "is_active": true,
  "retry_count": 3,
  "timeout_ms": 10000,
  "created_at": "2026-07-01T12:00:00Z",
  "updated_at": "2026-07-01T12:00:00Z"
}
```

## Supported Events

| Event                           | Description                                  |
| ------------------------------- | -------------------------------------------- |
| `conversation.created`          | A new conversation has been started          |
| `conversation.assigned`         | A conversation was assigned to an agent      |
| `conversation.resolved`         | A conversation was marked as resolved        |
| `conversation.message_received` | A new message was received in a conversation |
| `ticket.created`                | A new support ticket was created             |
| `ticket.updated`                | An existing ticket was updated               |
| `ticket.resolved`               | A ticket was resolved                        |
| `feedback.received`             | Customer feedback was submitted              |
| `agent.status_changed`          | An agent's status changed (online/offline)   |
| `contact.created`               | A new contact was created                    |

Not all providers support all events. Use `GET /api/v1/webhooks/providers` to see which events each provider supports.

## Verifying Webhook Signatures

Each delivery includes an `X-Signature-256` header with the HMAC-SHA256 signature of the request body.

### Python Example

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# In your webhook handler:
@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Signature-256", "").replace("sha256=", "")
    secret = "whsec_your_signing_secret"

    if not verify_webhook(payload, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process the webhook
    data = await request.json()
    ...
```

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature.replace('sha256=', '')),
    Buffer.from(expected)
  );
}

app.post('/webhook', (req, res) => {
  const payload = JSON.stringify(req.body);
  const signature = req.headers['x-signature-256'].replace('sha256=', '');
  const secret = 'whsec_your_signing_secret';

  if (!verifyWebhook(payload, signature, secret)) {
    return res.status(401).send('Invalid signature');
  }

  // Process the webhook
  ...
});
```

## Retry Logic

Failed deliveries (network errors, 5xx responses) are retried with exponential backoff:

- Attempt 1: immediate
- Attempt 2: 2s delay
- Attempt 3: 4s delay
- Attempt 4: 8s delay (max)

Total max attempts: `retry_count` (default: 3). After all retries fail, the delivery is marked as `failed` in the database.

## Delivery Status

Query delivery history:

```bash
curl http://localhost:8080/api/v1/webhooks/deliveries \
  -H "Authorization: Bearer <jwt_token>"
```

Response:

```json
{
  "deliveries": [
    {
      "id": "d-1",
      "config_id": "wh-abc-123",
      "event_type": "conversation.created",
      "status": "delivered",
      "response_code": 200,
      "attempt": 1,
      "duration_ms": 150,
      "created_at": "2026-07-01T12:00:00Z"
    }
  ]
}
```

## Testing Webhooks

Test a webhook configuration without triggering a real event:

```bash
curl -X POST "http://localhost:8080/api/v1/webhooks/test?config_id=wh-abc-123" \
  -H "Authorization: Bearer <jwt_token>"
```

This fires a test `conversation.created` event using the real delivery engine.

## Provider-Specific Payloads

Each provider receives a formatted payload. Examples:

### Slack

```json
{
  "text": "*Conversation Created*",
  "attachments": [
    {
      "color": "#36a64f",
      "fields": [
        { "title": "Conversation Id", "value": "c-123", "short": true },
        { "title": "Message", "value": "Help me", "short": true }
      ]
    }
  ]
}
```

### Zendesk

```json
{
  "ticket": {
    "subject": "Support: c-123",
    "description": "Help me",
    "priority": "normal",
    "tags": ["api"],
    "external_id": "c-123"
  }
}
```

### Intercom

```json
{
  "event_name": "conversation.created",
  "user_id": "u-123",
  "conversation_id": "c-123",
  "metadata": {
    "source": "customer_support_api",
    "summary": "Help me"
  }
}
```

### HubSpot

```json
{
  "properties": [
    { "property": "email", "value": "user@example.com" },
    { "property": "customer_support_tier", "value": "premium" }
  ]
}
```
