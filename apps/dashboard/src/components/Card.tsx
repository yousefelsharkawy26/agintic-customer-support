export function Card({ title, value, sub }: { title: string; value: string; sub?: string }) {
  return (
    <div style={{ background: '#fff', borderRadius: 10, padding: 20, border: '1px solid #e2e8f0', flex: 1 }}>
      <div style={{ fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
      {sub && <div style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>{sub}</div>}
    </div>
  );
}
