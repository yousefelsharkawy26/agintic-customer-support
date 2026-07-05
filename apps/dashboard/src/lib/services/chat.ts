import { apiClient, apiStreamClient } from "../api-client";

export interface ChatRequest {
  conversation_id?: string | null;
  message: string;
  stream?: boolean;
  user_id?: string | null;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  model: string;
  citations: string[];
}

export interface ConversationMessage {
  role: string;
  content: string;
  model: string;
  created_at: string;
}

export interface ConversationHistory {
  conversation_id: string;
  status: string;
  messages: ConversationMessage[];
}

export const chatService = {
  async sendMessageStream(data: ChatRequest) {
    return apiStreamClient("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify({ ...data, stream: true }),
    });
  },

  async sendMessage(data: ChatRequest) {
    return apiClient<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify({ ...data, stream: false }),
    });
  },

  async getConversation(conversationId: string) {
    return apiClient<ConversationHistory>(`/api/v1/conversations/${conversationId}`);
  },

  async listConversations() {
    return apiClient<ConversationHistory[]>("/api/v1/conversations");
  },
};
