import { apiClient } from "../api-client";

export interface MCPServerCreate {
  name: string;
  server_url: string;
  api_key?: string | null;
  transport?: string;
  timeout_ms?: number;
}

export interface MCPServerResponse {
  id: string;
  tenant_id: string;
  name: string;
  server_url: string;
  transport: string;
  is_active: boolean;
  health_status: string;
  timeout_ms: number;
}

export const mcpService = {
  async registerServer(data: MCPServerCreate) {
    return apiClient<{ id: string }>("/api/v1/tools/servers", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listServers() {
    return apiClient<MCPServerResponse[]>("/api/v1/tools/servers");
  },

  async deleteServer(id: string) {
    return apiClient<{ deleted: boolean }>(`/api/v1/tools/servers/${id}`, {
      method: "DELETE",
    });
  },
};
