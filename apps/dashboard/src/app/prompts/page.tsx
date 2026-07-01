'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';

export default function PromptsPage() {
  const [activePrompt, setActivePrompt] = useState('0');
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Prompt Registry</h1>
      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ width: 280 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span style={{ fontWeight: 600, fontSize: 14 }}>Prompts</span>
            <button style={{ padding: '4px 12px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontSize: 13 }}>+ New</button>
          </div>
          {['customer_support.system', 'faq.answer', 'escalation.transfer', 'ticket.creation'].map((name, i) => (
            <div key={name} onClick={() => setActivePrompt(String(i))}
              style={{
                padding: '10px 12px', borderRadius: 6, cursor: 'pointer', fontSize: 14, marginBottom: 4,
                background: activePrompt === String(i) ? '#eff6ff' : 'transparent',
                border: activePrompt === String(i) ? '1px solid #bfdbfe' : '1px solid transparent',
              }}>
              <div style={{ fontWeight: 500 }}>{name}</div>
              <div style={{ fontSize: 12, color: '#64748b' }}>v3 • active</div>
            </div>
          ))}
        </div>
        <div style={{ flex: 1, background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 600 }}>customer_support.system</h2>
              <div style={{ fontSize: 13, color: '#64748b' }}>Version 3 • Active • Last edited 2026-07-01</div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button style={{ padding: '6px 12px', border: '1px solid #e2e8f0', borderRadius: 4, fontSize: 13, background: '#fff' }}>Rollback</button>
              <button style={{ padding: '6px 12px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, fontSize: 13 }}>Save</button>
            </div>
          </div>
          <textarea rows={12} defaultValue={"You are a helpful customer support assistant for {company_name}.\n\nContext:\n{context}\n\nInstructions:\n- Answer based on the context provided\n- Cite sources using [Source N]\n- If unsure, say you don't know"} style={{ fontFamily: 'monospace', fontSize: 13, lineHeight: 1.6 }} />
          <div style={{ marginTop: 16, display: 'flex', gap: 16 }}>
            <div><span style={{ fontSize: 12, color: '#64748b' }}>Variables</span><div style={{ fontSize: 14 }}>company_name, context</div></div>
            <div><span style={{ fontSize: 12, color: '#64748b' }}>Eval Score</span><div style={{ fontSize: 14 }}>0.92</div></div>
            <div><span style={{ fontSize: 12, color: '#64748b' }}>Avg Tokens</span><div style={{ fontSize: 14 }}>245</div></div>
          </div>
          <div style={{ marginTop: 16, borderTop: '1px solid #e2e8f0', paddingTop: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>Version History</h3>
            {[{ v: 'v3', date: '2026-07-01', score: 0.92 }, { v: 'v2', date: '2026-06-15', score: 0.88 }, { v: 'v1', date: '2026-06-01', score: 0.85 }].map(v => (
              <div key={v.v} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f5f9', fontSize: 14 }}>
                <span style={{ fontWeight: 500 }}>{v.v}</span>
                <span style={{ color: '#64748b' }}>{v.date}</span>
                <span>Score: {v.score}</span>
              </div>
            ))}
          </div>
        </div>
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
