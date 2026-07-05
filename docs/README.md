# Customer Support AI — API Documentation

A multi-tenant AI customer support platform with RAG, webhooks,
and embeddable widgets.

## Quick Links

- **Interactive docs (Swagger UI)**: `GET /docs`
- **Alternative docs (ReDoc)**: `GET /redoc`
- **OpenAPI spec (JSON)**: `GET /openapi.json`
- **Health check**: `GET /health`
- **Readiness probe**: `GET /ready`

## Guides

- [Authentication](./authentication.md) — Get JWT tokens and API keys
- [Webhooks](./webhooks.md) — Configure Slack, Zendesk, Intercom, HubSpot deliveries
- [Widget Embedding](./widget-embedding.md) — Add the chat widget to your site
- [Usage Examples](./examples.md) — Copy-paste curl and Python examples

## API Overview

### Tags

| Tag          | Description                         |
| ------------ | ----------------------------------- |
| `auth`       | Authentication & API key management |
| `chat`       | Core chat endpoint with streaming   |
| `rag`        | Document ingestion & retrieval      |
| `tenants`    | Tenant configuration & quotas       |
| `monitoring` | Alerts, cost tracking, metrics      |
| `mcp`        | Model Context Protocol servers      |
| `webhooks`   | Outbound webhook integrations       |
| `widget`     | Embeddable chat widget API          |

### Authentication

Two methods are supported:

1. **Bearer JWT** (recommended for servers):

   ```
   Authorization: Bearer <jwt_token>
   ```

   Obtain via `POST /api/v1/auth/token?api_key=<key>`.

2. **API Key** (simple, for scripts):
   ```
   X-API-Key: <api_key>
   ```
   Create via `POST /api/v1/auth/api-keys`.

Widget endpoints (`/api/v1/widget/*`) are **public** for embedding.

### Rate Limiting

Default: 60 requests/minute per tenant. Response headers:

- `X-RateLimit-Limit`: Maximum requests in window
- `X-RateLimit-Remaining`: Remaining requests in current window

Exceeding the limit returns `429 Too Many Requests`.

### Error Format

All errors return JSON:

```json
{
  "error": "error_code",
  "message": "Human readable description"
}
```

Common status codes:

- `400` — Bad request (validation error)
- `401` — Missing or invalid authentication
- `403` — Tenant mismatch (RLS violation)
- `404` — Resource not found
- `429` — Rate limit exceeded
- `500` — Internal server error

## Environment

| Variable            | Default                           | Description                         |
| ------------------- | --------------------------------- | ----------------------------------- |
| `DATABASE_URL`      | `postgresql+asyncpg://...`        | PostgreSQL connection string        |
| `REDIS_URL`         | `redis://localhost:6379/0`        | Redis connection string             |
| `QDRANT_URL`        | `http://localhost:6333`           | Qdrant vector DB URL                |
| `JWT_SECRET`        | `dev-secret-change-in-production` | JWT signing secret (CHANGE IN PROD) |
| `OPENAI_API_KEY`    | (empty)                           | OpenAI API key                      |
| `ANTHROPIC_API_KEY` | (empty)                           | Anthropic API key                   |
| `GOOGLE_API_KEY`    | (empty)                           | Google AI API key                   |
| `CORS_ORIGINS`      | `*`                               | Allowed CORS origins                |
| `DB_POOL_SIZE`      | `10`                              | Database connection pool size       |
| `DB_MAX_OVERFLOW`   | `20`                              | Max overflow connections            |
| `REDIS_POOL_SIZE`   | `20`                              | Redis connection pool size          |
| `RATE_LIMIT_MAX`    | `60`                              | Max requests per window             |
| `RATE_LIMIT_WINDOW` | `60`                              | Rate limit window in seconds        |
