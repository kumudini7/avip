const RECOMMENDATION_META = {
  'Manual Process': { badge: 'bg-slate-100 text-slate-700 border border-slate-200', ring: '#64748b' },
  RPA: { badge: 'bg-blue-50 text-blue-700 border border-blue-200', ring: '#1d4ed8' },
  'RPA + Native UiPath AI': { badge: 'bg-emerald-50 text-emerald-700 border border-emerald-200', ring: '#059669' },
  'RPA + External AI': { badge: 'bg-purple-50 text-purple-700 border border-purple-200', ring: '#7e22ce' },
};

function KpiCard({ label, value }) {
  return (
    <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}

function ScoreRing({ value, label, color }) {
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const safeValue = Math.min(100, Math.max(0, value ?? 0));
  const offset = circumference - (safeValue / 100) * circumference;
  return (
    <div className="flex flex-col items-center gap-2">
      <svg viewBox="0 0 84 84" className="h-20 w-20">
        <circle cx="42" cy="42" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="8" />
        <circle
          cx="42"
          cy="42"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 42 42)"
        />
        <text x="42" y="47" textAnchor="middle" fontSize="16" fontWeight="600" fill="#0f172a">
          {Math.round(safeValue)}
        </text>
      </svg>
      <div className="max-w-[7rem] text-center text-xs font-medium text-slate-600">{label}</div>
    </div>
  );
}

export default function OverviewTab({ result }) {
  const { classification, use_case: useCase, roi } = result;
  if (!classification) return null;

  const paybackDisplay = roi?.payback_months ? `${roi.payback_months} mo` : useCase ? `${useCase.roi_benchmarks.payback_months} mo` : '--';
  const annualSavingDisplay = roi
    ? `${roi.currency} ${Math.round(roi.year1_net_saving).toLocaleString()}`
    : useCase
      ? `${useCase.roi_benchmarks.annual_saving_multiplier}x FTE cost`
      : '--';

  const recommendationMeta = RECOMMENDATION_META[classification.recommendation] || RECOMMENDATION_META.RPA;
  const hasScores = classification.recommendation != null;

  return (
    <div className="space-y-6">
      {hasScores ? (
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${recommendationMeta.badge}`}>
            {classification.recommendation}
          </span>
          <div className="mt-4 flex justify-around gap-4">
            <ScoreRing value={classification.ai_readiness_score} label="AI Readiness" color={recommendationMeta.ring} />
            <ScoreRing value={classification.automation_maturity_score} label="Automation Maturity" color={recommendationMeta.ring} />
            <ScoreRing value={classification.migration_readiness_score} label="Migration Readiness" color={recommendationMeta.ring} />
          </div>
          {classification.business_justification?.length ? (
            <div className="mt-5 space-y-2">
              {classification.business_justification.map((reason, index) => (
                <div key={index} className="flex items-start gap-2 text-sm text-slate-600">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-700" />
                  {reason}
                </div>
              ))}
            </div>
          ) : null}
          {classification.roi_estimate ? (
            <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
              <span className="font-semibold text-slate-900">Estimated ROI: </span>
              {classification.roi_estimate}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Auto-processing %" value={`${useCase?.roi_benchmarks.auto_processing_pct ?? '--'}%`} />
        <KpiCard label="Time saved / transaction" value={`${useCase?.roi_benchmarks.time_saved_mins ?? '--'} min`} />
        <KpiCard label="Payback period" value={paybackDisplay} />
        <KpiCard label="Annual saving estimate" value={annualSavingDisplay} />
      </div>

      {useCase ? (
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold text-slate-900">Value proposition</h3>
          <ul className="mt-3 space-y-2">
            {useCase.value_props.map((prop, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                {prop}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
