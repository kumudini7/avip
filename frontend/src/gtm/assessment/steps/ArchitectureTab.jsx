const COMPLEXITY_BADGE = {
  low: 'bg-emerald-50 text-emerald-700',
  medium: 'bg-amber-50 text-amber-700',
  high: 'bg-rose-50 text-rose-700',
};

export default function ArchitectureTab({ result }) {
  const { classification, use_case: useCase } = result;
  if (!classification || !useCase) return null;

  return (
    <div className="space-y-6">
      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Solution architecture</h3>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {useCase.process_flow.map((step, index) => (
            <div key={index} className="flex items-center gap-2">
              <div className="rounded-lg border-[0.5px] border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700">
                {step}
              </div>
              {index < useCase.process_flow.length - 1 ? (
                <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4 shrink-0 text-slate-400">
                  <path
                    d="M7 4l6 6-6 6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              ) : null}
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Systems involved</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {useCase.systems_involved.map((system) => (
            <span key={system} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
              {system}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold text-slate-900">Delivery estimate</h3>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-medium ${
              COMPLEXITY_BADGE[classification.complexity] || COMPLEXITY_BADGE.medium
            }`}
          >
            Complexity: {classification.complexity}
          </span>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            Timeline: {classification.estimated_timeline}
          </span>
        </div>
      </div>
    </div>
  );
}
