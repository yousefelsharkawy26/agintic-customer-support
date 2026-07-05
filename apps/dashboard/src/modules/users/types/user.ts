export type UserRole = "admin" | "support_agent" | "viewer" | "manager";
export type UserStatus = "active" | "invited" | "suspended";

export interface UserAccount {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  last_login_at?: string;
  created_at: string;
}
