import { apiClient } from "../api-client";

export interface TenantConfig {
  tenant_id: string;
  llm_model: string;
  embeddings_model: string;
  daily_request_limit: number;
  monthly_token_limit: number;
}

export interface TenantConfigUpdate {
  llm_api_key?: string;
  llm_model?: string;
  embeddings_model?: string;
  daily_request_limit?: number;
  monthly_token_limit?: number;
}

export interface TenantQuota {
  within_quota: boolean;
  requests_today: number;
  daily_limit: number;
  tokens_this_month: number;
  monthly_limit: number;
}

export const tenantService = {
  async getConfig() {
    return apiClient<TenantConfig>("/api/v1/tenants/config");
  },

  async updateConfig(data: TenantConfigUpdate) {
    return apiClient<TenantConfig>("/api/v1/tenants/config", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  async getQuota() {
    return apiClient<TenantQuota>("/api/v1/tenants/quota");
  },

  async getEngagement(since?: string) {
    const url = since ? `/api/v1/tenants/engagement?since=${since}` : "/api/v1/tenants/engagement";
    return apiClient<unknown>(url);
  },

  async getMonitoringData() {
    return apiClient<unknown>("/api/v1/tenants/monitoring");
  },
};
