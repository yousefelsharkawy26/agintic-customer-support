export type ToolType = "mcp_server" | "rest_api" | "openapi_spec" | "custom_function";

export interface ToolArgument {
  name: string;
  type: "string" | "number" | "boolean" | "object";
  description: string;
  required: boolean;
}

export interface CustomTool {
  id: string;
  name: string;
  description: string;
  type: ToolType;
  endpoint_url?: string;
  arguments?: ToolArgument[];
  status: "active" | "inactive" | "error";
  last_used_at?: string;
  created_at: string;
}
