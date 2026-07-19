import { useEffect, useState } from 'react';
import { getAssessmentResult } from '../../../services/api';
import OverviewTab from './OverviewTab';
import ArchitectureTab from './ArchitectureTab';
import RoiCalculatorTab from './RoiCalculatorTab';
import AssessmentHistoryPanel from './AssessmentHistoryPanel';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'roi', label: 'ROI Calculator' },
];

const CATEGORY_META = {
  pure_rpa: { label: 'Pure RPA', badge: 'bg-blue-50 text-blue-700 border border-blue-200' },
  rpa_ai: { label: 'RPA + AI', badge: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  rpa_ui: { label: 'RPA + UI', badge: 'bg-purple-50 text-purple-700 border border-purple-200' },
};

function ResultBanner({ result }) {
  const classification = result.classification;
  if (!classification) return null;
  const categoryMeta = CATEGORY_META[classification.category] || CATEGORY_META.pure_rpa;

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
      <div>
        <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${categoryMeta.badge}`}>
          {categoryMeta.label}
        </span>
        <h2 className="mt-2 text-lg font-semibold text-slate-900">{classification.matched_use_case}</h2>
        <div className="mt-1 text-xs text-slate-500">{result.domain}</div>
      </div>
      <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-4 border-blue-700 text-sm font-semibold text-slate-900">
        {Math.round(classification.confidence_score)}%
      </div>
    </div>
  );
}

export default function ResultDashboard({
  assessmentId,
  initialResult,
  readOnly = false,
  fetchResult = getAssessmentResult,
  assessments = [],
  onSelectAssessment,
  activeAssessmentId = null,
}) {
  const [result, setResult] = useState(initialResult ?? null);
  const [loading, setLoading] = useState(!initialResult);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (initialResult) return;
    let cancelled = false;
    setLoading(true);
    fetchResult(assessmentId)
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId]);

  if (loading || !result) {
    return <div className="text-sm text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <ResultBanner result={result} />

      <div className="flex gap-1 rounded-full bg-slate-100 p-1 w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              activeTab === tab.id ? 'bg-blue-700 text-white' : 'text-slate-600 hover:bg-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' ? <OverviewTab result={result} /> : null}
      {activeTab === 'architecture' ? <ArchitectureTab result={result} /> : null}
      {activeTab === 'roi' ? (
        <RoiCalculatorTab
          assessmentId={assessmentId}
          result={result}
          readOnly={readOnly}
          onRoiUpdated={(roi) => setResult((current) => ({ ...current, roi }))}
        />
      ) : null}

      <AssessmentHistoryPanel
        assessments={assessments}
        onSelectAssessment={onSelectAssessment}
        activeAssessmentId={activeAssessmentId}
      />
    </div>
  );
}
