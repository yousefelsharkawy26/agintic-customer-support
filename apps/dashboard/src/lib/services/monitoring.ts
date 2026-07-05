import { apiClient } from "../api-client";

export interface AlertRule {
  id: string;
  name: string;
  metric: string;
  operator: string;
  threshold: number;
  window_minutes: number;
  enabled: boolean;
}

export interface AlertEvent {
  id: string;
  rule_name: string;
  metric: string;
  value: number;
  threshold: number;
  message: string;
  resolved: boolean;
  created_at: string;
}

export interface CostSummary {
  tenant_id: string;
  total_cost: number;
  total_requests: number;
  daily_avg_cost: number;
}

export interface CostRecord {
  tenant_id: string;
  date: string;
  cost_usd: number;
  model: string;
}

export const monitoringService = {
  async getAlertRules() {
    return apiClient<AlertRule[]>("/api/v1/monitoring/alerts/rules");
  },

  async getAlertEvents(limit: number = 50) {
    return apiClient<AlertEvent[]>(`/api/v1/monitoring/alerts/events?limit=${limit}`);
  },

  async getCosts(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    const query = params.toString();
    const url = query ? `/api/v1/monitoring/costs?${query}` : "/api/v1/monitoring/costs";
    return apiClient<{ records: CostRecord[]; total_cost: number }>(url);
  },

  async getCostSummary() {
    return apiClient<CostSummary>("/api/v1/monitoring/costs/summary");
  },
};
