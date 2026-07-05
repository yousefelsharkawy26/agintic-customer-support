export type AgentStatus = "active" | "inactive" | "draft";
export type LLMModel =
  "claude-3-5-sonnet" | "claude-3-opus" | "gpt-4o" | "gpt-4o-mini" | "gemini-1-5-pro";

export interface Agent {
  id: string;
  name: string;
  description: string;
  model: LLMModel;
  status: AgentStatus;
  system_prompt?: string;
  temperature: number;
  max_tokens: number;
  enabled_tool_ids: string[];
  knowledge_collection_ids: string[];
  tools_count: number;
  kb_count: number;
  conversations_count: number;
  created_at: string;
  updated_at: string;
}
