import type { SystemLog, SystemStatus } from "../types/log";

export const MOCK_LOGS: SystemLog[] = [
  {
    id: "log_001",
    timestamp: new Date(Date.now() - 1000 * 2).toISOString(),
    level: "info",
    source: "agent_engine",
    message: "Successfully generated response for conversation conv_104",
    latency_ms: 1240,
    details: '{"tokens_used": 450, "model": "gpt-4o"}',
  },
  {
    id: "log_002",
    timestamp: new Date(Date.now() - 1000 * 45).toISOString(),
    level: "error",
    source: "mcp_tool",
    message: "Stripe API timeout during refund action",
    latency_ms: 5002,
    details: '{"tool_id": "tool_2", "error": "ETIMEDOUT"}',
  },
  {
    id: "log_003",
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    level: "warning",
    source: "vector_db",
    message: "High latency detected during semantic search query",
    latency_ms: 850,
  },
  {
    id: "log_004",
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    level: "info",
    source: "webhook",
    message: "Received incoming Zendesk ticket sync",
    latency_ms: 120,
  },
  {
    id: "log_005",
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    level: "critical",
    source: "auth_service",
    message: "Multiple failed login attempts detected for IP 192.168.1.45",
  },
];

export const MOCK_SYSTEM_STATUS: SystemStatus[] = [
  { service: "Agent Engine (LLM API)", status: "operational", uptime: "99.9%" },
  { service: "Vector Database (Pinecone)", status: "degraded", uptime: "98.5%" },
  { service: "MCP Tool Executor", status: "operational", uptime: "99.9%" },
  { service: "PostgreSQL Database", status: "operational", uptime: "99.99%" },
];
