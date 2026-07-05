export type LogLevel = "info" | "warning" | "error" | "critical";
export type LogSource = "agent_engine" | "vector_db" | "mcp_tool" | "auth_service" | "webhook";

export interface SystemLog {
  id: string;
  timestamp: string;
  level: LogLevel;
  source: LogSource;
  message: string;
  latency_ms?: number;
  details?: string;
}

export interface SystemStatus {
  service: string;
  status: "operational" | "degraded" | "down";
  uptime: string;
}
