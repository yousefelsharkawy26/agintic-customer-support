import { apiClient } from "../api-client";

export interface PromptCreate {
  name: string;
  template: string;
}

export interface PromptResponse {
  id: number;
  name: string;
  version: number;
  template: string;
  is_active: boolean;
  created_at: string;
}

export const promptsService = {
  async listPrompts() {
    return apiClient<PromptResponse[]>("/api/v1/prompts");
  },

  async createPrompt(data: PromptCreate) {
    return apiClient<PromptResponse>("/api/v1/prompts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getPrompt(name: string) {
    return apiClient<PromptResponse>(`/api/v1/prompts/${name}`);
  },

  async rollbackPrompt(name: string, version: number) {
    return apiClient<PromptResponse>(`/api/v1/prompts/${name}/rollback?version=${version}`, {
      method: "POST",
    });
  },
};
