# Widget Embedding Guide

Add the embeddable chat widget to your website with a single `<script>` tag.

## Quick Start

Add this to your HTML, replacing `your-tenant-id` with your actual tenant ID:

```html
<script
  data-tenant-id="your-tenant-id"
  data-api-base="https://api.your-domain.com/api/v1/widget"
  src="https://api.your-domain.com/chat-widget.js"
></script>
```

That's it! A chat bubble will appear in the bottom-right corner of your page.

## Configuration

The widget reads configuration from the server (`GET /api/v1/widget/settings/{tenant_id}`). You can customize:

| Setting          | Description                             | Default                         |
| ---------------- | --------------------------------------- | ------------------------------- |
| `primary_color`  | Hex color for buttons and user messages | `#2563eb`                       |
| `position`       | `bottom-right` or `bottom-left`         | `bottom-right`                  |
| `title`          | Widget header text                      | `Support`                       |
| `greeting`       | First message shown to visitors         | `Hi! How can I help you today?` |
| `locale`         | `en`, `es`, `fr`, `de`                  | `en`                            |
| `brand_logo_url` | Logo URL shown in header                | (none)                          |
| `show_branding`  | Show "Powered by" footer                | `true`                          |
| `custom_css`     | Additional CSS injected into widget     | (none)                          |

### Updating Widget Settings (Admin)

```bash
curl -X PUT http://localhost:8080/api/v1/widget/settings/my-tenant \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_color": "#10b981",
    "position": "bottom-left",
    "title": "Acme Support",
    "greeting": "Welcome to Acme! How can we help?",
    "show_branding": false,
    "brand_logo_url": "https://acme.com/logo.png"
  }'
```

## Data Attributes

You can override the default `api-base` and `visitor-id` via `data-*` attributes:

```html
<script
  data-tenant-id="your-tenant-id"
  data-api-base="https://api.your-domain.com/api/v1/widget"
  data-visitor-id="user-123"
  src="https://api.your-domain.com/chat-widget.js"
></script>
```

If `data-visitor-id` is omitted, the widget generates a random anonymous ID (stored in `localStorage`).

## Widget Lifecycle

1. **Load**: Widget script loads, fetches settings from API
2. **Render**: Chat bubble appears (invisible by default)
3. **Open**: User clicks bubble → widget expands, session starts
4. **Message**: User sends message → streamed response with citations
5. **Rating**: After each response, user can rate (1-5 emoji)
6. **Close**: User clicks X → widget collapses

## Analytics

The widget automatically tracks these events:

- `widget_loaded` — Widget script loaded successfully
- `widget_opened` — User opened the widget
- `widget_closed` — User closed the widget
- `session_started` — New chat session started
- `message_sent` — User sent a message
- `message_received` — Assistant response received
- `satisfaction_rating` — User rated a response (1-5)

Query analytics:

```bash
curl http://localhost:8080/api/v1/widget/analytics/my-tenant \
  -H "Authorization: Bearer <jwt_token>"
```

Response:

```json
{
  "total_events": 1234,
  "events": [...],
  "breakdown": {
    "widget_opened": 456,
    "message_sent": 789,
    "satisfaction_rating": 123
  }
}
```

### Satisfaction Summary

```bash
curl http://localhost:8080/api/v1/widget/analytics/my-tenant/satisfaction \
  -H "Authorization: Bearer <jwt_token>"
```

Response:

```json
{
  "total": 123,
  "average": 4.2,
  "distribution": {
    "5": 67,
    "4": 32,
    "3": 15,
    "2": 6,
    "1": 3
  }
}
```

## Offline Messaging

If a user sends a message while offline, the widget queues it and delivers when they return. This works via:

1. `POST /api/v1/widget/messages/offline` — Queue a message
2. `GET /api/v1/widget/messages/offline/{tenant_id}/{visitor_id}` — Fetch undelivered messages

The widget handles this automatically.

## Custom CSS

Inject custom CSS to override default styles:

```bash
curl -X PUT http://localhost:8080/api/v1/widget/settings/my-tenant \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_css": "#cs-widget-toggle { width: 64px; height: 64px; }"
  }'
```

## Security

- Widget endpoints are **public** (no authentication required)
- The `tenant_id` is provided by the embedding site — ensure it's your own tenant
- All widget events are scoped to the `tenant_id` in the request
- Visitor IDs are client-generated — use authenticated visitor IDs for logged-in users

## Browser Support

The widget uses vanilla JavaScript and works in all modern browsers:

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari iOS 14+
- Chrome Android 90+

No build step or npm install required — just include the script tag.
