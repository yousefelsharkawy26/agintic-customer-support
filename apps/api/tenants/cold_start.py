from __future__ import annotations

COLD_START_FAQ: dict[str, str] = {
    "hours": "Our support team is available Monday to Friday, 9 AM to 6 PM EST.",
    "contact": "You can reach us through this chat widget or email us at support@example.com.",
    "response_time": "We typically respond within 1-2 hours during business hours.",
    "general": "Welcome! I'm your AI support assistant. How can I help you today?",
}


def get_cold_start_response(query: str) -> str:
    q = query.lower()
    for keyword, response in COLD_START_FAQ.items():
        if keyword in q:
            return response
    return COLD_START_FAQ["general"]
