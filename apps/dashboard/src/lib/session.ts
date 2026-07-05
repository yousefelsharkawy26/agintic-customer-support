import { cookies } from "next/headers";

export interface JWTPayload {
  tenant_id: string;
  tenant_name: string;
  tenant_slug: string;
  plan: string;
  auth_method: string;
  key_id?: number;
  exp?: number;
}

export function getSession(): JWTPayload | null {
  const cookieStore = cookies();
  const token = cookieStore.get("access_token")?.value;

  if (!token) {
    return null;
  }

  try {
    // We only decode the payload, as the token is fully verified by FastAPI
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );

    return JSON.parse(jsonPayload) as JWTPayload;
  } catch {
    return null;
  }
}

export function getTenantId(): string | null {
  const session = getSession();
  return session?.tenant_id || null;
}

export function getAccessToken(): string | null {
  const cookieStore = cookies();
  return cookieStore.get("access_token")?.value || null;
}
