'use client';

import Sidebar from '@/components/Sidebar';
import { Card } from '@/components/Card';

export default function AnalyticsPage() {
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Analytics</h1>
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <Card title="Total Questions" value="8,456" sub="+8% vs last week" />
        <Card title="Avg Latency" value="1.2s" sub="p95: 2.8s" />
        <Card title="Tool Calls" value="1,023" sub="+15% vs last week" />
        <Card title="Escalation Rate" value="5.2%" sub="-1.2% vs last week" />
      </div>
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, border: '1px solid #e2e8f0', marginBottom: 16 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Questions by Day</h2>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 120 }}>
          {[40, 65, 35, 80, 55, 90, 70].map((h, i) => (
            <div key={i} style={{ flex: 1, background: '#2563eb', height: `${h}%`, borderRadius: '4px 4px 0 0', minWidth: 20 }} />
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 12, color: '#64748b' }}>
          <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
        </div>
      </div>
      <div style={{ background: '#fff', borderRadius: 10, padding: 20, border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Top Intents</h2>
        <table>
          <thead><tr><th>Intent</th><th>Count</th><th>%</th></tr></thead>
          <tbody>
            {[{ intent: 'FAQ', count: 3450, pct: 40.8 },
              { intent: 'Complex Query', count: 2100, pct: 24.8 },
              { intent: 'Tool Needed', count: 1856, pct: 21.9 },
              { intent: 'Escalation', count: 1050, pct: 12.4 },
            ].map(r => (
              <tr key={r.intent}><td>{r.intent}</td><td>{r.count.toLocaleString()}</td><td>{r.pct}%</td></tr>
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
