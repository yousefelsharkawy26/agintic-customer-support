'use client';

import Sidebar from '@/components/Sidebar';

export default function ConversationsPage() {
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Conversations</h1>
      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        <input placeholder="Search conversations..." style={{ flex: 1 }} />
        <select style={{ width: 160 }}><option>All statuses</option><option>Active</option><option>Resolved</option><option>Escalated</option></select>
      </div>
      <table>
        <thead><tr><th>ID</th><th>User</th><th>Tenant</th><th>Messages</th><th>Status</th><th>Created</th></tr></thead>
        <tbody>
          {[{ id: 'c1', user: 'alice@co.com', tenant: 'tenant_a', msgs: 12, status: 'active', date: '2026-07-01' },
            { id: 'c2', user: 'bob@co.com', tenant: 'tenant_a', msgs: 5, status: 'resolved', date: '2026-06-30' },
            { id: 'c3', user: 'charlie@co.com', tenant: 'tenant_b', msgs: 8, status: 'escalated', date: '2026-06-30' },
          ].map(c => (
            <tr key={c.id}>
              <td style={{ fontWeight: 500, fontFamily: 'monospace' }}>{c.id}</td>
              <td>{c.user}</td>
              <td>{c.tenant}</td>
              <td>{c.msgs}</td>
              <td><StatusBadge status={c.status} /></td>
              <td>{c.date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = { active: '#2563eb', resolved: '#059669', escalated: '#d97706' };
  return <span style={{ color: colors[status] || '#64748b' }}>● {status}</span>;
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <main style={{ flex: 1, padding: 32, overflowY: 'auto' }}>{children}</main>
    </div>
  );
}
