const STEP_LABELS = ['Welcome', 'Domain & Context', 'Questionnaire', 'Classification', 'Dashboard & ROI'];

function initials(name) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function BoltIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
      <path d="M13 2 3 14h7l-1 8 11-14h-8l1-6z" />
    </svg>
  );
}

function StepDot({ state }) {
  if (state === 'done') {
    return (
      <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-400 text-blue-900">
        <svg viewBox="0 0 20 20" fill="currentColor" className="h-3.5 w-3.5">
          <path
            fillRule="evenodd"
            d="M16.7 5.3a1 1 0 0 1 0 1.4l-7.5 7.5a1 1 0 0 1-1.4 0l-3.5-3.5a1 1 0 1 1 1.4-1.4l2.8 2.8 6.8-6.8a1 1 0 0 1 1.4 0Z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    );
  }
  if (state === 'active') {
    return <div className="h-6 w-6 shrink-0 rounded-full border-2 border-white bg-white/20" />;
  }
  return <div className="h-6 w-6 shrink-0 rounded-full border-2 border-white/20" />;
}

export default function AssessmentSidebar({ currentStep, companyName, contactName, onReset, onSignOut }) {
  const progressPct = Math.round(((currentStep - 1) / (STEP_LABELS.length - 1)) * 100);

  return (
    <aside className="flex h-screen w-[320px] shrink-0 flex-col overflow-hidden bg-black">
      <div className="border-b border-white/10 px-4 py-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-white/15 text-amber-300">
            <BoltIcon />
          </span>
          AutoAssess
        </div>
        <div className="mt-0.5 text-xs text-blue-300">Jade GTM Playbook</div>
      </div>

      <div className="flex items-center gap-2.5 border-b border-white/10 px-4 py-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/15 text-xs font-semibold text-white">
          {initials(contactName)}
        </div>
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-white">{companyName || 'Your company'}</div>
          <div className="truncate text-xs text-blue-300">{contactName || 'Client'}</div>
        </div>
      </div>

      <nav className="flex-1 space-y-3 px-4 py-3">
        {STEP_LABELS.map((label, index) => {
          const stepNumber = index + 1;
          const state = stepNumber < currentStep ? 'done' : stepNumber === currentStep ? 'active' : 'pending';
          return (
            <div key={label} className="flex items-center gap-2.5">
              <StepDot state={state} />
              <span className={`text-xs ${state === 'pending' ? 'text-blue-300' : 'text-white'} ${state === 'active' ? 'font-medium' : ''}`}>
                {label}
              </span>
            </div>
          );
        })}
      </nav>

      <div className="space-y-2 border-t border-white/10 px-4 py-3">
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-emerald-400 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <div className="text-xs text-blue-300">{progressPct}% complete</div>
        <button
          type="button"
          onClick={onReset}
          className="mt-1 block text-xs font-medium text-blue-200 underline-offset-2 hover:text-white hover:underline"
        >
          Start new assessment
        </button>
        {onSignOut ? (
          <button
            type="button"
            onClick={onSignOut}
            className="block text-xs font-medium text-blue-300/70 underline-offset-2 hover:text-white hover:underline"
          >
            Sign out
          </button>
        ) : null}
      </div>
    </aside>
  );
}
