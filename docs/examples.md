# Usage Examples

Copy-paste examples for common API operations.

## Setup

```bash
export API_URL="http://localhost:8080"
export TENANT_ID="my-tenant"
export API_KEY="csk_live_..."  # Get from POST /api/v1/auth/api-keys
```

## Authentication

### Create an API Key

```bash
curl -X POST $API_URL/api/v1/auth/api-keys \
  -H "Content-Type: application/json" \
  -d "{
    \"tenant_id\": \"$TENANT_ID\",
    \"label\": \"My API Key\"
  }"
```

### Get a JWT Token

```bash
TOKEN=$(curl -s -X POST "$API_URL/api/v1/auth/token?api_key=$API_KEY" | jq -r '.access_token')
echo $TOKEN
```

## Chat

### Send a Message (Non-Streaming)

```bash
curl -X POST $API_URL/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I reset my password?",
    "stream": false
  }'
```

### Send a Message (Streaming)

```bash
curl -X POST $API_URL/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "message": "How do I reset my password?",
    "stream": true
  }'
```

### Continue a Conversation

```bash
CONV_ID="conv-abc-123"  # From previous response

curl -X POST $API_URL/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"message\": \"What about 2FA?\",
    \"stream\": false
  }"
```

### Get Conversation History

```bash
curl $API_URL/api/v1/conversations/$CONV_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Documents (RAG)

### Upload a Document

```bash
curl -X POST $API_URL/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "tenant_id=$TENANT_ID"
```

### List Documents

```bash
curl $API_URL/api/v1/documents?tenant_id=$TENANT_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Search Documents

```bash
curl -X POST $API_URL/api/v1/documents/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "password reset",
    "tenant_id": "'$TENANT_ID'",
    "limit": 5
  }'
```

## Webhooks

### List Supported Providers

```bash
curl $API_URL/api/v1/webhooks/providers \
  -H "Authorization: Bearer $TOKEN"
```

### List Supported Events

```bash
curl $API_URL/api/v1/webhooks/events \
  -H "Authorization: Bearer $TOKEN"
```

### Create a Slack Webhook

```bash
curl -X POST $API_URL/api/v1/webhooks/configs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "slack",
    "label": "Production Slack",
    "url": "https://hooks.slack.com/services/T00/B00/xxx",
    "secret": "whsec_my_secret",
    "events": ["conversation.created", "ticket.resolved"]
  }'
```

### List Webhooks

```bash
curl $API_URL/api/v1/webhooks/configs \
  -H "Authorization: Bearer $TOKEN"
```

### Test a Webhook

```bash
WEBHOOK_ID="wh-abc-123"

curl -X POST "$API_URL/api/v1/webhooks/test?config_id=$WEBHOOK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete a Webhook

```bash
curl -X DELETE $API_URL/api/v1/webhooks/configs/$WEBHOOK_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Widget

### Get Widget Settings (Public)

```bash
curl $API_URL/api/v1/widget/settings/$TENANT_ID
```

### Update Widget Settings (Admin)

```bash
curl -X PUT $API_URL/api/v1/widget/settings/$TENANT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_color": "#10b981",
    "position": "bottom-left",
    "title": "Acme Support",
    "greeting": "Welcome! How can we help?"
  }'
```

### Start a Widget Session (Public)

```bash
curl -X POST $API_URL/api/v1/widget/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "'$TENANT_ID'",
    "visitor_id": "visitor-123",
    "locale": "en"
  }'
```

## Python Examples

### Send a Message

```python
import httpx

API_URL = "http://localhost:8080"
API_KEY = "csk_live_..."

# Get JWT token
token_response = httpx.post(f"{API_URL}/api/v1/auth/token", params={"api_key": API_KEY})
token = token_response.json()["access_token"]

# Send message
response = httpx.post(
    f"{API_URL}/api/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Hello!", "stream": False},
)
print(response.json())
```

### Stream a Response

```python
import httpx
import json

response = httpx.post(
    f"{API_URL}/api/v1/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Tell me a story", "stream": True},
)

with response.iter_lines() as lines:
    for line in lines:
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if data["type"] == "token":
                print(data["content"], end="", flush=True)
            elif data["type"] == "done":
                print()
                print(f"Conversation ID: {data['conversation_id']}")
```

### Webhook Handler (Flask)

```python
from flask import Flask, request, abort
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_my_secret"

@app.post("/webhook")
def handle_webhook():
    payload = request.get_data()
    signature = request.headers.get("X-Signature-256", "").replace("sha256=", "")

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        abort(401)

    event = request.json
    print(f"Received event: {event['type']}")
    print(f"Data: {event['data']}")
    return "", 200
```

### Embeddable Widget (HTML)

```html
<!doctype html>
<html>
  <head>
    <title>My Site</title>
  </head>
  <body>
    <h1>Welcome to My Site</h1>
    <script
      data-tenant-id="my-tenant"
      data-api-base="http://localhost:8080/api/v1/widget"
      src="http://localhost:8080/chat-widget.js"
    ></script>
  </body>
</html>
```

## Monitoring

### List Alert Rules

```bash
curl $API_URL/api/v1/monitoring/alerts/rules?tenant_id=$TENANT_ID \
  -H "Authorization: Bearer $TOKEN"
```

### List Firing Alerts

```bash
curl $API_URL/api/v1/monitoring/alerts/firing?tenant_id=$TENANT_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Get Cost Summary

```bash
curl $API_URL/api/v1/monitoring/cost/$TENANT_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Tenant Management

### Migrate a Tenant

```bash
curl -X POST $API_URL/api/v1/tenants/$TENANT_ID/migrate \
  -H "Authorization: Bearer $TOKEN"
```

### Get Quota Status

```bash
curl $API_URL/api/v1/tenants/$TENANT_ID/quota \
  -H "Authorization: Bearer $TOKEN"
```

### Update Tenant Config

```bash
curl -X PUT $API_URL/api/v1/tenants/$TENANT_ID/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "llm_model": "gpt-4o",
    "embeddings_model": "text-embedding-3-large",
    "daily_request_limit": 10000,
    "monthly_token_limit": 1000000
  }'
```
