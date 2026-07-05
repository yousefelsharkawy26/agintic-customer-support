import type { CustomTool } from "../types/tool";

export const MOCK_TOOLS: CustomTool[] = [
  {
    id: "tool_1",
    name: "Customer Data API",
    description: "Fetches customer CRM data, including recent tickets and billing history.",
    type: "rest_api",
    endpoint_url: "https://api.internal.com/v1/customers",
    status: "active",
    last_used_at: "2024-06-21T10:30:00Z",
    created_at: "2024-01-15T08:00:00Z",
    arguments: [
      {
        name: "customer_id",
        type: "string",
        description: "The UUID of the customer.",
        required: true,
      },
    ],
  },
  {
    id: "tool_2",
    name: "Stripe Refund Action",
    description: "Issues a refund for a specific charge ID through the Stripe MCP.",
    type: "mcp_server",
    endpoint_url: "mcp://stripe-server",
    status: "active",
    last_used_at: "2024-06-20T14:15:00Z",
    created_at: "2024-02-10T11:00:00Z",
    arguments: [
      { name: "charge_id", type: "string", description: "The Stripe charge ID.", required: true },
      {
        name: "amount",
        type: "number",
        description: "Amount to refund. Full refund if omitted.",
        required: false,
      },
    ],
  },
  {
    id: "tool_3",
    name: "Inventory Check",
    description: "Checks real-time stock levels across warehouses.",
    type: "openapi_spec",
    status: "error",
    created_at: "2024-05-05T09:00:00Z",
  },
];
