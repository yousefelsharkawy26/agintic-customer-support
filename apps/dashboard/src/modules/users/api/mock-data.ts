import type { UserAccount } from "../types/user";

export const MOCK_USERS: UserAccount[] = [
  {
    id: "usr_1001",
    name: "Admin System",
    email: "admin@integraserve.ai",
    role: "admin",
    status: "active",
    last_login_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    created_at: "2023-11-01T08:00:00Z",
  },
  {
    id: "usr_1002",
    name: "Sarah Jenkins",
    email: "sarah.j@integraserve.ai",
    role: "manager",
    status: "active",
    last_login_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
    created_at: "2024-01-15T09:30:00Z",
  },
  {
    id: "usr_1003",
    name: "Michael Chen",
    email: "m.chen@integraserve.ai",
    role: "support_agent",
    status: "active",
    last_login_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    created_at: "2024-02-20T11:15:00Z",
  },
  {
    id: "usr_1004",
    name: "Emma Watson",
    email: "emma.w@integraserve.ai",
    role: "support_agent",
    status: "invited",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
  },
  {
    id: "usr_1005",
    name: "David Smith",
    email: "david.s@integraserve.ai",
    role: "viewer",
    status: "suspended",
    last_login_at: "2024-05-10T14:20:00Z",
    created_at: "2024-03-05T10:00:00Z",
  },
];
