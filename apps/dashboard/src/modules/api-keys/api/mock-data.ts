import type { ApiKey } from "../types/api-key";

export const MOCK_API_KEYS: ApiKey[] = [
  {
    id: "key_001",
    name: "Production Website Integration",
    key_hint: "sk_live_••••••••••••9a2f",
    status: "active",
    created_at: "2024-01-10T08:00:00Z",
    last_used_at: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: "key_002",
    name: "Local Development Sandbox",
    key_hint: "sk_test_••••••••••••b41c",
    status: "active",
    created_at: "2024-04-15T11:30:00Z",
    last_used_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    id: "key_003",
    name: "Old Marketing Site",
    key_hint: "sk_live_••••••••••••7e5d",
    status: "revoked",
    created_at: "2023-11-20T09:15:00Z",
    last_used_at: "2024-01-09T14:20:00Z",
  },
];
