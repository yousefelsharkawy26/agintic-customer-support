export type ConversationStatus =
  "active" | "resolved" | "archived" | "bot_handling" | "human_escalated";

export interface ConversationMessage {
  id: string;
  role: "user" | "agent" | "system" | "human_agent";
  content: string;
  created_at: string;
}

export interface ConversationRow {
  conversation_id: string;
  agent_id: string;
  customer_name: string;
  customer_email: string;
  status: ConversationStatus;
  messages_count: number;
  last_message_preview: string;
  last_message_at: string;
  created_at: string;
  messages?: ConversationMessage[];
}
