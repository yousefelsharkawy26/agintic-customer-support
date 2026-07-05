import { apiClient } from "@/lib/api-client";

export interface AgentConfig {
  id: string;
  tenant_id: string;
  name: string;
  description: string;
  model: string;
  status: "active" | "inactive" | "draft";
  system_prompt: string;
  temperature: number;
  max_tokens: number;
  enabled_tool_ids: string[];
  knowledge_collection_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface AgentCreatePayload {
  name: string;
  description?: string;
  model?: string;
  status?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  enabled_tool_ids?: string[];
  knowledge_collection_ids?: string[];
}

export interface AgentUpdatePayload extends Partial<AgentCreatePayload> {}

export const agentsService = {
  listAgents(): Promise<AgentConfig[]> {
    return apiClient<AgentConfig[]>("/api/v1/agents");
  },

  createAgent(body: AgentCreatePayload): Promise<AgentConfig> {
    return apiClient<AgentConfig>("/api/v1/agents", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getAgent(agentId: string): Promise<AgentConfig> {
    return apiClient<AgentConfig>(`/api/v1/agents/${agentId}`);
  },

  updateAgent(agentId: string, body: AgentUpdatePayload): Promise<AgentConfig> {
    return apiClient<AgentConfig>(`/api/v1/agents/${agentId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  },

  deleteAgent(agentId: string): Promise<{ deleted: boolean }> {
    return apiClient<{ deleted: boolean }>(`/api/v1/agents/${agentId}`, {
      method: "DELETE",
    });
  },
};
