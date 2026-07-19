const items = [
  { id: 'dashboard', label: 'Overview', href: '#dashboard' },
  { id: 'workspace', label: 'Workspace', href: '#workspace' },
  { id: 'documents', label: 'Uploads', href: '#documents' },
  { id: 'analysis', label: 'Analysis', href: '#analysis' },
  { id: 'proposal', label: 'Proposal', href: '#proposal' },
];

export default function Sidebar({ activePage = 'dashboard' }) {
  return (
    <aside className="glass-panel flex h-screen min-h-0 flex-col overflow-hidden rounded-none border-r border-slate-200 p-6 shadow-none">
      <div className="mb-10">
        <div className="text-xs uppercase tracking-[0.35em] text-blue-900">AVIP</div>
        <h1 className="mt-3 text-2xl font-semibold text-slate-950">Value Intelligence Platform</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Pre-sales automation discovery, scoring, and proposal support.
        </p>
      </div>
      <nav className="min-h-0 flex-1 space-y-2 overflow-hidden">
        {items.map((item) => {
          const isActive = activePage === item.id;
          return (
            <a
              key={item.href}
              href={item.href}
              aria-current={isActive ? 'page' : undefined}
              className={`block rounded-none border-b px-4 py-4 text-sm font-medium transition ${
                isActive
                  ? 'border-blue-900 bg-blue-900 text-white shadow-sm'
                  : 'border-slate-200 text-slate-700 hover:bg-blue-900/10 hover:text-blue-900'
              }`}
            >
              {item.label}
            </a>
          );
        })}
      </nav>
    </aside>
  );
}
