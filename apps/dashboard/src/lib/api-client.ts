import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface FetchOptions extends RequestInit {
  requireAuth?: boolean;
}

const getApiUrl = () => {
  return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

export async function apiClient<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { requireAuth = true, headers = {}, ...rest } = options;
  const url = `${getApiUrl()}${path.startsWith("/") ? path : `/${path}`}`;

  const mergedHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  if (requireAuth) {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      redirect("/login");
    }

    mergedHeaders["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...rest,
    headers: mergedHeaders,
  });

  if (!response.ok) {
    if (response.status === 401) {
      redirect("/login");
    }

    let errorData;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(response.status, "unknown_error", `HTTP error ${response.status}`);
    }

    throw new ApiError(
      response.status,
      errorData.error || "api_error",
      errorData.message || errorData.detail || `HTTP error ${response.status}`
    );
  }

  // Handle empty responses
  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return {} as T;
  }

  return response.json();
}

/**
 * Specifically for streaming responses, bypassing JSON parsing
 */
export async function apiStreamClient(path: string, options: FetchOptions = {}): Promise<Response> {
  const { requireAuth = true, headers = {}, ...rest } = options;
  const url = `${getApiUrl()}${path.startsWith("/") ? path : `/${path}`}`;

  const mergedHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string>),
  };

  if (requireAuth) {
    const cookieStore = cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      throw new ApiError(401, "unauthorized", "Missing access token");
    }

    mergedHeaders["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...rest,
    headers: mergedHeaders,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(response.status, "unknown_error", `HTTP error ${response.status}`);
    }

    throw new ApiError(
      response.status,
      errorData.error || "api_error",
      errorData.message || errorData.detail || `HTTP error ${response.status}`
    );
  }

  return response;
}
