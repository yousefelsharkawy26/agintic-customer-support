'use client';

import Sidebar from '@/components/Sidebar';

export default function KnowledgeBasePage() {
  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Knowledge Base</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <input placeholder="Website URL..." style={{ width: 280 }} />
          <button style={{ padding: '8px 16px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 500 }}>Crawl</button>
        </div>
      </div>
      <div style={{ marginBottom: 16, padding: 20, background: '#fff', borderRadius: 10, border: '1px solid #e2e8f0' }}>
        <label style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, padding: 32, border: '2px dashed #e2e8f0', borderRadius: 8, cursor: 'pointer' }}>
          <span style={{ fontSize: 32 }}>📄</span>
          <span style={{ fontSize: 14, color: '#64748b' }}>Drop files here or click to upload (PDF, Markdown, HTML)</span>
          <input type="file" multiple style={{ display: 'none' }} />
        </label>
      </div>
      <table>
        <thead><tr><th>Title</th><th>Source</th><th>Chunks</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          {[{ title: 'Getting Started Guide', src: 'PDF', chunks: 24, date: '2026-07-01', status: 'indexed' },
            { title: 'FAQ', src: 'Markdown', chunks: 15, date: '2026-06-28', status: 'indexed' },
          ].map(d => (
            <tr key={d.title}>
              <td style={{ fontWeight: 500 }}>{d.title}</td>
              <td>{d.src}</td>
              <td>{d.chunks}</td>
              <td>{d.date}</td>
              <td><span style={{ color: '#059669' }}>● {d.status}</span></td>
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
