'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';

export default function ToolsPage() {
  const [showForm, setShowForm] = useState(false);
  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>MCP Tools</h1>
        <button onClick={() => setShowForm(!showForm)}
          style={{ padding: '8px 16px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 500 }}>
          + Add Server
        </button>
      </div>
      {showForm && (
        <div style={{ padding: 20, background: '#fff', borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input placeholder="Server name" />
          <input placeholder="Server URL (https://...)" />
          <input placeholder="API key (optional)" type="password" />
          <div style={{ display: 'flex', gap: 8 }}>
            <button style={{ padding: '8px 16px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6 }}>Save</button>
            <button onClick={() => setShowForm(false)} style={{ padding: '8px 16px', background: '#fff', color: '#64748b', border: '1px solid #e2e8f0', borderRadius: 6 }}>Cancel</button>
          </div>
        </div>
      )}
      <table>
        <thead><tr><th>Name</th><th>URL</th><th>Status</th><th>Tools</th><th>Added</th></tr></thead>
        <tbody>
          {[{ name: 'Stripe MCP', url: 'https://mcp.example.com/stripe', status: 'healthy', tools: 12, added: '2026-06-15' },
            { name: 'Zendesk MCP', url: 'https://mcp.example.com/zendesk', status: 'degraded', tools: 8, added: '2026-06-20' },
          ].map(s => (
            <tr key={s.name}>
              <td style={{ fontWeight: 500 }}>{s.name}</td>
              <td style={{ color: '#64748b', fontSize: 13 }}>{s.url}</td>
              <td><span style={{ color: s.status === 'healthy' ? '#059669' : '#d97706' }}>● {s.status}</span></td>
              <td>{s.tools}</td>
              <td>{s.added}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <main style={{ flex: 1, padding: 32, overflowY: 'auto' }}>{children}</main>
    </div>
  );
}
