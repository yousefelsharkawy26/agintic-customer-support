export type ApiKeyStatus = "active" | "revoked";

export interface ApiKey {
  id: string;
  name: string;
  key_hint: string; // The masked key like sk_live_...1234
  status: ApiKeyStatus;
  created_at: string;
  last_used_at?: string;
}
