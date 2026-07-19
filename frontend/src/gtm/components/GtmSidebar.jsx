import { useLocation, useNavigate } from 'react-router-dom';

function buildWorkspaceItems(engagementCount) {
  return [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'engagements', label: 'Engagements', badge: engagementCount > 0 ? engagementCount : null },
    { id: 'pitch-builder', label: 'Pitch Builder' },
    { id: 'client-assessments', label: 'Client Assessments', path: '/dashboard/client-assessments' },
  ];
}

const stageItems = [
  { id: 'discovery', label: 'Discovery' },
  { id: 'design', label: 'Design' },
  { id: 'integration', label: 'Integration' },
  { id: 'measurement', label: 'Measurement' },
  { id: 'scale', label: 'Scale' },
];

const resourceItems = [
  { id: 'kpi-library', label: 'KPI Library' },
  { id: 'case-studies', label: 'Case Studies' },
  { id: 'settings', label: 'Settings' },
];

function NavSection({ title, items, activeNav, onNavigate }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div>
      <div className="px-3 text-xs font-semibold tracking-wide text-blue-300/90">{title}</div>
      <div className="mt-2 space-y-0.5">
        {items.map((item) => {
          const isActive = item.path
            ? location.pathname === item.path
            : location.pathname === '/dashboard' && activeNav === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                if (item.path) {
                  navigate(item.path);
                } else {
                  navigate('/dashboard');
                  onNavigate(item.id);
                }
              }}
              className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition ${
                isActive ? 'bg-white/15 font-medium text-white' : 'text-blue-100 hover:bg-white/10 hover:text-white'
              }`}
            >
              <span>{item.label}</span>
              {item.badge ? (
                <span className="rounded-full bg-white/15 px-2 py-0.5 text-xs font-medium text-blue-50">
                  {item.badge}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function initials(name) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export default function GtmSidebar({ activeNav, onNavigate, userName, userRole, engagementCount = 0 }) {
  const workspaceItems = buildWorkspaceItems(engagementCount);
  return (
    <aside className="flex h-screen w-[320px] shrink-0 flex-col bg-black">
      <div className="border-b border-white/10 px-5 py-6">
        <div className="text-base font-semibold text-white">Jade GTM Playbook</div>
        <div className="mt-1 text-sm text-blue-300">Agentic AI Practice</div>
      </div>

      <nav className="flex-1 space-y-7 overflow-y-auto px-3 py-5">
        <NavSection title="Workspace" items={workspaceItems} activeNav={activeNav} onNavigate={onNavigate} />
        <NavSection title="GTM stages" items={stageItems} activeNav={activeNav} onNavigate={onNavigate} />
        <NavSection title="Resources" items={resourceItems} activeNav={activeNav} onNavigate={onNavigate} />
      </nav>

      <div className="flex items-center gap-3 border-t border-white/10 px-5 py-5">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/15 text-xs font-semibold text-white">
          {initials(userName)}
        </div>
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-white">{userName}</div>
          <div className="truncate text-xs text-blue-300">{userRole}</div>
        </div>
      </div>
    </aside>
  );
}
