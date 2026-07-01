'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/', label: 'Overview', icon: '📊' },
  { href: '/knowledge-base', label: 'Knowledge Base', icon: '📚' },
  { href: '/tools', label: 'Tools', icon: '🔧' },
  { href: '/conversations', label: 'Conversations', icon: '💬' },
  { href: '/analytics', label: 'Analytics', icon: '📈' },
  { href: '/settings', label: 'Settings', icon: '⚙️' },
  { href: '/prompts', label: 'Prompts', icon: '📝' },
  { href: '/widget-config', label: 'Widget', icon: '🎨' },
];

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside style={{ width: 240, background: '#fff', borderRight: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '20px 16px', fontWeight: 700, fontSize: 18, borderBottom: '1px solid #e2e8f0' }}>
        CS Dashboard
      </div>
      <nav style={{ flex: 1, padding: 8 }}>
        {NAV_ITEMS.map(item => {
          const active = path === item.href;
          return (
            <Link key={item.href} href={item.href}
              style={{
                display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px',
                borderRadius: 8, fontSize: 14, fontWeight: active ? 600 : 400,
                background: active ? '#eff6ff' : 'transparent',
                color: active ? '#2563eb' : '#475569',
              }}>
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
