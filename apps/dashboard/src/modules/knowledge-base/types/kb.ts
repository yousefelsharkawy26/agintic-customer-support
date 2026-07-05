export type SyncStatus = "idle" | "syncing" | "failed" | "completed";

export interface KnowledgeCollection {
  id: string;
  name: string;
  description: string;
  document_count: number;
  chunk_count: number;
  last_synced_at: string;
  status: SyncStatus;
  created_at: string;
  updated_at: string;
}

export type DocumentType = "pdf" | "markdown" | "url" | "text";

export interface KnowledgeDocument {
  id: string;
  collection_id: string;
  title: string;
  type: DocumentType;
  size_bytes: number;
  chunk_count: number;
  status: SyncStatus;
  source_url?: string;
  created_at: string;
  updated_at: string;
}
