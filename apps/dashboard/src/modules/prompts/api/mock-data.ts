import type { PromptTemplate } from "../types/prompt";

export const MOCK_PROMPTS: PromptTemplate[] = [
  {
    id: "prompt_01",
    name: "Customer Support Persona (Default)",
    description: "The core system prompt for all tier-1 support agents.",
    content:
      "You are a helpful, empathetic customer support agent for IntegraServe. You must always maintain a professional tone.\n\nContext:\n{{knowledge_context}}\n\nUser Question:\n{{user_message}}\n\nInstructions:\n1. Answer the user's question using only the provided context.\n2. If you don't know the answer, politely offer to escalate to a human.\n3. Do not make promises regarding refunds without checking the policy.",
    version: "v1.4",
    status: "active",
    variables: [
      { name: "knowledge_context", description: "Relevant chunks from the vector database." },
      { name: "user_message", description: "The customer's latest message." },
    ],
    created_at: "2024-01-10T08:00:00Z",
    updated_at: "2024-06-15T09:30:00Z",
  },
  {
    id: "prompt_02",
    name: "Technical Troubleshooting",
    description: "Specialized prompt for guiding users through API and integration issues.",
    content:
      "You are a technical support engineer. Your goal is to help developers debug their API integrations.\n\nAPI Specs:\n{{api_documentation}}\n\nUser Error:\n{{error_log}}\n\nPlease provide code examples where applicable.",
    version: "v2.0",
    status: "draft",
    variables: [
      { name: "api_documentation", description: "Relevant API docs." },
      { name: "error_log", description: "The stack trace or error message provided by the user." },
    ],
    created_at: "2024-05-20T11:00:00Z",
    updated_at: "2024-06-20T14:15:00Z",
  },
  {
    id: "prompt_03",
    name: "Billing Inquiry",
    description: "Prompt for answering subscription and invoicing questions.",
    content:
      "You are a billing specialist. Explain invoice details clearly and concisely.\n\nCustomer Plan: {{customer_plan}}\nLatest Invoice: {{latest_invoice}}\n\nResolve the inquiry:",
    version: "v1.1",
    status: "active",
    variables: [
      { name: "customer_plan", description: "The customer's current subscription tier." },
      { name: "latest_invoice", description: "Details of the most recent charge." },
    ],
    created_at: "2024-03-12T13:00:00Z",
    updated_at: "2024-04-10T10:00:00Z",
  },
];
