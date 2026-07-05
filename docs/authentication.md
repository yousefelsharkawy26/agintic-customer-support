# Authentication

The API supports two authentication methods: **Bearer JWT** (recommended for servers) and **API Key** (simple, for scripts).

## Bearer JWT (Recommended)

### 1. Create an API Key

First, create an API key for your tenant. This is a one-time setup step.

```bash
curl -X POST http://localhost:8080/api/v1/auth/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-tenant-id",
    "label": "Production server key"
  }'
```

Response:

```json
{
  "api_key": "csk_live_a1b2c3d4e5f6...",
  "tenant_id": "my-tenant-id"
}
```

> **⚠️ IMPORTANT**: The `api_key` is shown **only once**. Store it securely (e.g., in a secrets manager). You cannot retrieve it later.

### 2. Exchange API Key for JWT Token

```bash
curl -X POST "http://localhost:8080/api/v1/auth/token?api_key=csk_live_a1b2c3d4e5f6..."
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the JWT Token

Include the token in the `Authorization` header:

```bash
curl http://localhost:8080/api/v1/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "stream": false}'
```

## API Key (Simple)

For scripts and quick testing, you can use the API key directly without exchanging it for a JWT:

```bash
curl http://localhost:8080/api/v1/webhooks/providers \
  -H "X-API-Key: csk_live_a1b2c3d4e5f6..."
```

This is equivalent to using a JWT token but skips the token exchange step.

## Multi-Tenant Security

Every authenticated request is scoped to a tenant. The `tenant_id` is extracted from the JWT token (or looked up from the API key). All database queries are automatically filtered by this tenant.

If you try to access another tenant's resources, you'll get a `403 Forbidden`:

```bash
curl http://localhost:8080/api/v1/tenants/other-tenant/config \
  -H "Authorization: Bearer <your-token>"
# 403 Forbidden: Tenant mismatch
```

## Widget Endpoints (Public)

The following endpoints are **public** and do not require authentication:

- `POST /api/v1/widget/sessions/start`
- `POST /api/v1/widget/sessions/{session_id}/heartbeat`
- `POST /api/v1/widget/sessions/{session_id}/end`
- `POST /api/v1/widget/messages/offline`
- `GET /api/v1/widget/messages/offline/{tenant_id}/{visitor_id}`
- `GET /api/v1/widget/settings/{tenant_id}`
- `POST /api/v1/widget/analytics/event`

These are designed to be called from the embeddable chat widget running in a visitor's browser.

## Python Example

```python
import httpx

API_KEY = "csk_live_a1b2c3d4e5f6..."
BASE_URL = "http://localhost:8080"

# Option 1: Use API key directly
response = httpx.get(
    f"{BASE_URL}/api/v1/webhooks/providers",
    headers={"X-API-Key": API_KEY},
)
print(response.json())

# Option 2: Exchange for JWT token
token_response = httpx.post(f"{BASE_URL}/api/v1/auth/token", params={"api_key": API_KEY})
token = token_response.json()["access_token"]

# Use JWT token for subsequent requests
response = httpx.get(
    f"{BASE_URL}/api/v1/tenants/my-tenant/config",
    headers={"Authorization": f"Bearer {token}"},
)
print(response.json())
```

## Security Best Practices

1. **Never commit API keys** to version control. Use environment variables or a secrets manager.
2. **Rotate API keys** periodically (delete old keys, create new ones).
3. **Use HTTPS** in production to prevent token interception.
4. **Use short-lived JWT tokens** (default: 24 hours). Exchange for a new token when expired.
5. **Restrict CORS origins** in production (set `CORS_ORIGINS` env var to your domain).
