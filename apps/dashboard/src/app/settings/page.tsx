'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';

export default function SettingsPage() {
  const [tab, setTab] = useState('llm');
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Settings</h1>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['LLM', 'API Keys', 'Billing'].map(t => (
          <button key={t} onClick={() => setTab(t.toLowerCase().replace(' ', '_'))}
            style={{
              padding: '8px 16px', borderRadius: 6, border: '1px solid #e2e8f0', fontWeight: 500,
              background: tab === t.toLowerCase().replace(' ', '_') ? '#2563eb' : '#fff',
              color: tab === t.toLowerCase().replace(' ', '_') ? '#fff' : '#475569',
            }}>{t}</button>
        ))}
      </div>
      {tab === 'llm' && (
        <div style={{ background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>LLM Model</label>
            <select style={{ width: 300 }}><option>gpt-4o</option><option>gpt-4o-mini</option><option>claude-3-5-sonnet</option><option>gemini-1.5-pro</option></select></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>OpenAI API Key</label>
            <input type="password" placeholder="sk-..." style={{ width: 400 }} /></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Anthropic API Key</label>
            <input type="password" placeholder="sk-..." style={{ width: 400 }} /></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Daily Request Limit</label>
            <input type="number" defaultValue={1000} style={{ width: 200 }} /></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Monthly Token Limit</label>
            <input type="number" defaultValue={1000000} style={{ width: 200 }} /></div>
          <div><button style={{ padding: '10px 24px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 500, alignSelf: 'flex-start' }}>Save Changes</button></div>
        </div>
      )}
      {tab === 'api_keys' && (
        <div style={{ background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600 }}>API Keys</h2>
            <button style={{ padding: '8px 16px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6 }}>+ Generate Key</button>
          </div>
          <table>
            <thead><tr><th>Label</th><th>Key</th><th>Created</th><th>Status</th></tr></thead>
            <tbody>
              {[{ label: 'Production', key: 'cs_...a1b2', date: '2026-06-01', status: 'Active' },
                { label: 'Development', key: 'cs_...c3d4', date: '2026-06-15', status: 'Active' },
              ].map(k => (
                <tr key={k.label}><td>{k.label}</td><td style={{ fontFamily: 'monospace', fontSize: 13 }}>{k.key}</td><td>{k.date}</td><td><span style={{ color: '#059669' }}>● {k.status}</span></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {tab === 'billing' && (
        <div style={{ background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0' }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Usage & Billing</h2>
          <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
            <div style={{ flex: 1, padding: 16, background: '#f8fafc', borderRadius: 8 }}><div style={{ fontSize: 12, color: '#64748b' }}>Current Plan</div><div style={{ fontSize: 20, fontWeight: 700 }}>Pro</div></div>
            <div style={{ flex: 1, padding: 16, background: '#f8fafc', borderRadius: 8 }}><div style={{ fontSize: 12, color: '#64748b' }}>Monthly Usage</div><div style={{ fontSize: 20, fontWeight: 700 }}>456,789 / 1M</div></div>
            <div style={{ flex: 1, padding: 16, background: '#f8fafc', borderRadius: 8 }}><div style={{ fontSize: 12, color: '#64748b' }}>Est. Cost</div><div style={{ fontSize: 20, fontWeight: 700 }}>$45.67</div></div>
          </div>
          <table>
            <thead><tr><th>Date</th><th>Requests</th><th>Tokens</th><th>Cost</th></tr></thead>
            <tbody>
              {[{ date: '2026-07-01', req: 1234, tokens: 45678, cost: '$4.57' },
                { date: '2026-06-30', req: 1100, tokens: 42300, cost: '$4.23' },
              ].map(r => (
                <tr key={r.date}><td>{r.date}</td><td>{r.req.toLocaleString()}</td><td>{r.tokens.toLocaleString()}</td><td>{r.cost}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
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
