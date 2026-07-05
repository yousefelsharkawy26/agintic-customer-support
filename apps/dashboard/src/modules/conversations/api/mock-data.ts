import type { ConversationRow, ConversationMessage } from "../types/conversation";

export const MOCK_CONVERSATIONS: ConversationRow[] = [
  {
    conversation_id: "conv_101",
    agent_id: "agent_01",
    customer_name: "Alice Johnson",
    customer_email: "alice@example.com",
    status: "bot_handling",
    messages_count: 5,
    last_message_preview: "Let me check the refund status for you.",
    last_message_at: new Date(Date.now() - 1000 * 60 * 2).toISOString(), // 2 mins ago
    created_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
  },
  {
    conversation_id: "conv_102",
    agent_id: "agent_02",
    customer_name: "Bob Smith",
    customer_email: "bob@techcorp.com",
    status: "human_escalated",
    messages_count: 12,
    last_message_preview: "I need to speak to a real person about my enterprise billing.",
    last_message_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 mins ago
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    conversation_id: "conv_103",
    agent_id: "agent_01",
    customer_name: "Carol White",
    customer_email: "carol@design.co",
    status: "resolved",
    messages_count: 8,
    last_message_preview: "Thank you, that solved my login issue!",
    last_message_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // 1 day ago
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 25).toISOString(),
  },
];

export const MOCK_MESSAGES: Record<string, ConversationMessage[]> = {
  conv_101: [
    {
      id: "msg_1",
      role: "user",
      content: "Hi, I requested a refund yesterday but haven't received an email confirmation.",
      created_at: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    },
    {
      id: "msg_2",
      role: "agent",
      content:
        "Hello Alice. I can help with that. Could you please provide the order number for the refund?",
      created_at: new Date(Date.now() - 1000 * 60 * 9).toISOString(),
    },
    {
      id: "msg_3",
      role: "user",
      content: "Yes, it's ORD-99231.",
      created_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    },
    {
      id: "msg_4",
      role: "system",
      content: "[Tool Execution: Stripe Refund Action] Result: Refund is processing.",
      created_at: new Date(Date.now() - 1000 * 60 * 3).toISOString(),
    },
    {
      id: "msg_5",
      role: "agent",
      content:
        "Let me check the refund status for you. It looks like it is currently processing and should appear in your inbox within the next hour.",
      created_at: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    },
  ],
};
