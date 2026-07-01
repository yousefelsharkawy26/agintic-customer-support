'use client';

import Sidebar from '@/components/Sidebar';
import { Card } from '@/components/Card';

export default function OverviewPage() {
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Overview</h1>
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <Card title="Conversations" value="1,234" sub="+12% this week" />
        <Card title="Messages" value="8,456" sub="+8% this week" />
        <Card title="Avg Response" value="1.2s" sub="p95: 2.8s" />
        <Card title="Deflection Rate" value="78%" sub="+5% this month" />
      </div>
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Recent Conversations</h2>
        <table>
          <thead><tr><th>ID</th><th>User</th><th>Status</th><th>Messages</th><th>Date</th></tr></thead>
          <tbody>
            {[{ id: 'conv_001', user: 'Alice', status: 'active', msgs: 12, date: '2026-07-01' },
              { id: 'conv_002', user: 'Bob', status: 'resolved', msgs: 5, date: '2026-06-30' },
              { id: 'conv_003', user: 'Charlie', status: 'escalated', msgs: 8, date: '2026-06-30' },
            ].map(c => (
              <tr key={c.id}><td>{c.id}</td><td>{c.user}</td><td>{c.status}</td><td>{c.msgs}</td><td>{c.date}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
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
