const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchApi(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getTenantConfig(tenantId: string) {
  return fetchApi(`/api/v1/tenants/${tenantId}/config`);
}

export async function updateTenantConfig(tenantId: string, data: Record<string, unknown>) {
  return fetchApi(`/api/v1/tenants/${tenantId}/config`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getConversations(tenantId: string) {
  return fetchApi(`/api/v1/conversations?tenant_id=${tenantId}`);
}

export async function getConversation(id: string) {
  return fetchApi(`/api/v1/conversations/${id}`);
}
