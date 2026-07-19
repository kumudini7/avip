import { useEffect, useRef, useState } from 'react';
import { classifyAssessment } from '../../../services/api';

const LOADING_MESSAGES = [
  'Analysing your process...',
  'Mapping to use case knowledge base...',
  'Computing automation fit score...',
];

const CATEGORY_META = {
  pure_rpa: { label: 'Pure RPA', badge: 'bg-blue-50 text-blue-700 border border-blue-200' },
  rpa_ai: { label: 'RPA + AI', badge: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  rpa_ui: { label: 'RPA + UI', badge: 'bg-purple-50 text-purple-700 border border-purple-200' },
};

const RECOMMENDATION_META = {
  'Manual Process': { badge: 'bg-slate-100 text-slate-700 border border-slate-200', ring: '#64748b' },
  RPA: { badge: 'bg-blue-50 text-blue-700 border border-blue-200', ring: '#1d4ed8' },
  'RPA + Native UiPath AI': { badge: 'bg-emerald-50 text-emerald-700 border border-emerald-200', ring: '#059669' },
  'RPA + External AI': { badge: 'bg-purple-50 text-purple-700 border border-purple-200', ring: '#7e22ce' },
};

const COMPLEXITY_BADGE = {
  low: 'bg-emerald-50 text-emerald-700',
  medium: 'bg-amber-50 text-amber-700',
  high: 'bg-rose-50 text-rose-700',
};

function ScoreRing({ value, label, color = '#1d4ed8' }) {
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

function ConfidenceRing({ value }) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(100, Math.max(0, value)) / 100) * circumference;
  return (
    <svg viewBox="0 0 100 100" className="h-24 w-24">
      <circle cx="50" cy="50" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" />
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#1d4ed8"
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 50 50)"
      />
      <text x="50" y="55" textAnchor="middle" fontSize="20" fontWeight="600" fill="#0f172a">
        {Math.round(value)}%
      </text>
    </svg>
  );
}

export default function ClassificationStep({ assessmentId, onContinue, onCompleted }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [messageIndex, setMessageIndex] = useState(0);
  const startedRef = useRef(false);

  useEffect(() => {
    // Guard against React StrictMode's dev-only double-invoke: classify is not idempotent
    // (it calls the LLM and mutates the assessment), so it must fire at most once per mount,
    // and the resulting promise must not be discarded by a synthetic cleanup.
    if (startedRef.current) return;
    startedRef.current = true;

      classifyAssessment(assessmentId)
        .then((data) => {
          setResult(data);
          setLoading(false);
          onCompleted?.();
        })
      .catch((err) => {
        setError(err?.response?.data?.detail || 'Classification failed. Please try again.');
        setLoading(false);
      });
  }, [assessmentId]);

  useEffect(() => {
    if (!loading) return undefined;
    const timer = setInterval(() => {
      setMessageIndex((current) => (current + 1) % LOADING_MESSAGES.length);
    }, 1500);
    return () => clearInterval(timer);
  }, [loading]);

  if (loading) {
    return (
      <div className="mx-auto flex max-w-xl flex-col items-center justify-center rounded-xl border-[0.5px] border-slate-200 bg-white p-12 text-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-700" />
        <div className="mt-5 text-sm font-medium text-slate-700">{LOADING_MESSAGES[messageIndex]}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-xl rounded-xl border-[0.5px] border-slate-200 bg-white p-8 text-center">
        <div className="text-sm font-medium text-rose-600">{error}</div>
      </div>
    );
  }

  const categoryMeta = CATEGORY_META[result.category] || CATEGORY_META.pure_rpa;
  const recommendationMeta = RECOMMENDATION_META[result.recommendation] || RECOMMENDATION_META.RPA;
  const hasScores = result.recommendation != null;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {hasScores ? (
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-6">
          <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${recommendationMeta.badge}`}>
            {result.recommendation}
          </span>
          <h2 className="mt-3 text-lg font-semibold text-slate-900">Automation readiness scores</h2>

          <div className="mt-5 flex justify-around gap-4">
            <ScoreRing value={result.ai_readiness_score} label="AI Readiness" color={recommendationMeta.ring} />
            <ScoreRing value={result.automation_maturity_score} label="Automation Maturity" color={recommendationMeta.ring} />
            <ScoreRing value={result.migration_readiness_score} label="Migration Readiness" color={recommendationMeta.ring} />
          </div>

          {result.business_justification?.length ? (
            <div className="mt-6">
              <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Business justification</div>
              <div className="space-y-2">
                {result.business_justification.map((reason, index) => (
                  <div key={index} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-700" />
                    {reason}
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {result.roi_estimate ? (
            <div className="mt-5 rounded-lg bg-slate-50 p-4 text-sm text-slate-700">
              <span className="font-semibold text-slate-900">Estimated ROI: </span>
              {result.roi_estimate}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-6">
        <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${categoryMeta.badge}`}>
          {categoryMeta.label}
        </span>
        <h2 className="mt-3 text-xl font-semibold text-slate-900">{result.matched_use_case}</h2>

        <div className="mt-5 flex items-center gap-6">
          <ConfidenceRing value={result.confidence_score} />
          <div className="space-y-2">
            {result.reasoning.map((reason, index) => (
              <div key={index} className="flex items-start gap-2 text-sm text-slate-600">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-700" />
                {reason}
              </div>
            ))}
          </div>
        </div>

        {result.similar_use_cases?.length ? (
          <div className="mt-6">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Similar use cases</div>
            <div className="grid gap-3 sm:grid-cols-2">
              {result.similar_use_cases.map((title) => (
                <div key={title} className="rounded-lg border-[0.5px] border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
                  {title}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${COMPLEXITY_BADGE[result.complexity] || COMPLEXITY_BADGE.medium}`}>
            Complexity: {result.complexity}
          </span>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            Timeline: {result.estimated_timeline}
          </span>
        </div>

        <button
          type="button"
          onClick={onContinue}
          className="mt-8 w-full rounded-lg bg-blue-700 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-800 sm:w-auto"
        >
          View dashboard &amp; ROI
        </button>
      </div>
    </div>
  );
}
