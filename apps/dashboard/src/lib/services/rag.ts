import { apiClient } from "../api-client";

export interface DocumentIngestRequest {
  content: string;
  source_type?: string;
  source_url?: string;
  title?: string;
}

export interface DocumentResponse {
  id: string;
  title: string | null;
  source_type: string;
  chunk_count: number;
  version: number;
  created_at: string;
}

export const ragService = {
  async ingestDocument(data: DocumentIngestRequest) {
    return apiClient<{ chunks_indexed: number; tenant_id: string }>("/api/v1/documents/ingest", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listDocuments() {
    return apiClient<{ documents: DocumentResponse[] }>("/api/v1/documents/");
  },

  async deleteDocument(id: string) {
    return apiClient<{ status: string; document_id: string }>(`/api/v1/documents/${id}`, {
      method: "DELETE",
    });
  },
};
