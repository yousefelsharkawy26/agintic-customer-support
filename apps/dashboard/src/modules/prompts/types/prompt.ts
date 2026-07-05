export type PromptStatus = "active" | "draft" | "archived";

export interface PromptVariable {
  name: string;
  description: string;
}

export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  content: string;
  version: string;
  status: PromptStatus;
  variables: PromptVariable[];
  created_at: string;
  updated_at: string;
}
