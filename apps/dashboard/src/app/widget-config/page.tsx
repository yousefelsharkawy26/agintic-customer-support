'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';

export default function WidgetConfigPage() {
  const [color, setColor] = useState('#2563eb');
  const [position, setPosition] = useState('bottom-right');
  return (
    <Layout>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 24 }}>Widget Configuration</h1>
      <div style={{ display: 'flex', gap: 24 }}>
        <div style={{ flex: 1, background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Widget Title</label>
            <input defaultValue="Support" /></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Primary Color</label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input type="color" value={color} onChange={e => setColor(e.target.value)} style={{ width: 48, height: 40, padding: 2 }} />
              <input value={color} onChange={e => setColor(e.target.value)} style={{ width: 120 }} />
            </div></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Position</label>
            <select value={position} onChange={e => setPosition(e.target.value)} style={{ width: 200 }}>
              <option value="bottom-right">Bottom Right</option>
              <option value="bottom-left">Bottom Left</option>
            </select></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Logo URL</label>
            <input placeholder="https://example.com/logo.png" /></div>
          <div><label style={{ fontSize: 14, fontWeight: 500, display: 'block', marginBottom: 4 }}>Locale</label>
            <select style={{ width: 200 }}><option value="en">English</option><option value="es">Español</option><option value="fr">Français</option><option value="de">Deutsch</option></select></div>
          <div><button style={{ padding: '10px 24px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, fontWeight: 500, alignSelf: 'flex-start' }}>Save Config</button></div>
        </div>
        <div style={{ width: 300, background: '#f8fafc', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Preview</h3>
          <div style={{
            width: 240, height: 180, background: '#fff', borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            display: 'flex', flexDirection: 'column', overflow: 'hidden',
          }}>
            <div style={{ padding: 12, background: color, color: '#fff', fontSize: 14, fontWeight: 600 }}>Support</div>
            <div style={{ flex: 1, padding: 12 }}>
              <div style={{ padding: '6px 10px', background: '#f1f5f9', borderRadius: 8, fontSize: 13, maxWidth: '70%', alignSelf: 'flex-start' }}>How can I help?</div>
            </div>
            <div style={{ padding: 8, borderTop: '1px solid #e2e8f0', display: 'flex', gap: 4 }}>
              <div style={{ flex: 1, height: 28, background: '#f1f5f9', borderRadius: 4 }} />
              <div style={{ width: 48, height: 28, background: color, borderRadius: 4 }} />
            </div>
          </div>
        </div>
      </div>
      <div style={{ marginTop: 24, background: '#fff', borderRadius: 10, padding: 24, border: '1px solid #e2e8f0' }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Installation Script</h2>
        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 12 }}>Add this script to your website:</p>
        <pre style={{ background: '#1e293b', color: '#e2e8f0', padding: 16, borderRadius: 8, fontSize: 13, overflow: 'auto' }}>
{`<script src="https://cdn.example.com/widget.js" data-primary-color="${color}" data-position="${position}" data-title="Support"></script>`}
        </pre>
        <button style={{ marginTop: 8, padding: '8px 16px', border: '1px solid #e2e8f0', borderRadius: 6, background: '#fff' }}>Copy Script</button>
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
