from __future__ import annotations

import json
from typing import Any

import structlog

from apps.api.core.interfaces import ToolCall, ToolResult
from apps.api.tools.registry import ToolSpec, register_tool

logger = structlog.get_logger()


async def create_ticket(tool_call: ToolCall) -> ToolResult:
    subject = tool_call.arguments.get("subject", "No subject")
    description = tool_call.arguments.get("description", "")
    priority = tool_call.arguments.get("priority", "normal")
    ticket_id = f"TICKET-{hash(subject + description) % 100000:05d}"
    logger.info("ticket_created", ticket_id=ticket_id, priority=priority)
    return ToolResult(
        tool_call_id=tool_call.id or "",
        output=json.dumps({"ticket_id": ticket_id, "status": "open", "priority": priority}),
    )


async def escalate_human(tool_call: ToolCall) -> ToolResult:
    reason = tool_call.arguments.get("reason", "No reason provided")
    conversation_id = tool_call.arguments.get("conversation_id", "unknown")
    escalation_id = f"ESC-{hash(reason + conversation_id) % 100000:05d}"
    logger.info("escalation_created", escalation_id=escalation_id, reason=reason)
    return ToolResult(
        tool_call_id=tool_call.id or "",
        output=json.dumps({"escalation_id": escalation_id, "status": "assigned"}),
    )


async def get_faq(tool_call: ToolCall) -> ToolResult:
    query = tool_call.arguments.get("query", "")
    faq_db: dict[str, str] = {
        "return": "Returns are accepted within 30 days of purchase.",
        "shipping": "Free shipping on orders over $50. Standard delivery: 5-7 business days.",
        "hours": "Our support hours are Monday-Friday, 9 AM to 6 PM EST.",
        "payment": "We accept Visa, Mastercard, Amex, and PayPal.",
    }
    results = {
        k: v for k, v in faq_db.items() if query.lower() in k.lower() or query.lower() in v.lower()
    }
    if not results:
        results = {"answer": "No matching FAQ found. Try a different query or contact support."}
    logger.info("faq_queried", query=query, matches=len(results))
    return ToolResult(
        tool_call_id=tool_call.id or "",
        output=json.dumps(results),
    )


async def search_docs(tool_call: ToolCall) -> ToolResult:
    query = tool_call.arguments.get("query", "")
    logger.info("doc_search", query=query)
    return ToolResult(
        tool_call_id=tool_call.id or "",
        output=json.dumps({"query": query, "note": "Full doc search handled by RAG pipeline"}),
    )


HARDCODED_TOOLS: dict[str, Any] = {
    "create_ticket": create_ticket,
    "escalate_human": escalate_human,
    "get_faq": get_faq,
    "search_docs": search_docs,
}

_create_ticket_spec = ToolSpec(
    name="create_ticket",
    version="1.0.0",
    description="Create a support ticket for the user's issue",
    input_schema={
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "Ticket subject"},
            "description": {"type": "string", "description": "Detailed issue description"},
            "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
        },
        "required": ["subject"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string"},
            "status": {"type": "string"},
            "priority": {"type": "string"},
        },
    },
)

_escalate_spec = ToolSpec(
    name="escalate_human",
    version="1.0.0",
    description="Escalate the conversation to a human agent",
    input_schema={
        "type": "object",
        "properties": {
            "reason": {"type": "string", "description": "Why escalation is needed"},
            "conversation_id": {"type": "string", "description": "Current conversation ID"},
        },
        "required": ["reason"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "escalation_id": {"type": "string"},
            "status": {"type": "string"},
        },
    },
)

_faq_spec = ToolSpec(
    name="get_faq",
    version="1.0.0",
    description="Look up an answer from the FAQ database",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "FAQ search query"},
        },
        "required": ["query"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
        },
    },
)

_search_docs_spec = ToolSpec(
    name="search_docs",
    version="1.0.0",
    description="Search indexed documentation for relevant information",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
        },
        "required": ["query"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "note": {"type": "string"},
        },
    },
)

for spec in [_create_ticket_spec, _escalate_spec, _faq_spec, _search_docs_spec]:
    register_tool(spec)
