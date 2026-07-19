import { useEffect, useState } from 'react';
import Topbar from '../../components/Topbar';
import ResultDashboard from '../../assessment/steps/ResultDashboard';
import { getAdminAssessmentResult, listAdminAssessments } from '../../../services/api';

const STATUS_BADGE = {
  in_progress: 'bg-amber-50 text-amber-700',
  completed: 'bg-emerald-50 text-emerald-700',
};

const CATEGORY_LABEL = {
  pure_rpa: 'Pure RPA',
  rpa_ai: 'RPA + AI',
  rpa_ui: 'RPA + UI',
};

function formatDate(value) {
  if (!value) return '--';
  return new Date(value).toLocaleDateString();
}

export default function ClientAssessments() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    listAdminAssessments()
      .then((data) => {
        if (!cancelled) setAssessments(data);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (selectedId) {
    return (
      <div className="space-y-6">
        <Topbar
          crumb="Client Assessments"
          title={`Assessment #${selectedId}`}
          actions={
            <button
              type="button"
              onClick={() => setSelectedId(null)}
              className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Back to list
            </button>
          }
        />
        <ResultDashboard assessmentId={selectedId} readOnly fetchResult={getAdminAssessmentResult} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Topbar crumb="Client Assessments" />

      <div className="overflow-hidden rounded-xl border-[0.5px] border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-[0.5px] border-slate-200 text-xs text-slate-500">
              <th className="px-4 py-3 text-left font-medium">Client</th>
              <th className="px-4 py-3 text-left font-medium">Company</th>
              <th className="px-4 py-3 text-left font-medium">Domain</th>
              <th className="px-4 py-3 text-left font-medium">Status</th>
              <th className="px-4 py-3 text-left font-medium">Date</th>
              <th className="px-4 py-3 text-left font-medium">Classification</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  Loading...
                </td>
              </tr>
            ) : assessments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                  No client assessments yet.
                </td>
              </tr>
            ) : (
              assessments.map((assessment) => (
                <tr
                  key={assessment.id}
                  onClick={() => setSelectedId(assessment.id)}
                  className="cursor-pointer border-b-[0.5px] border-slate-100 last:border-0 hover:bg-slate-50"
                >
                  <td className="px-4 py-3 text-slate-900">{assessment.client_name}</td>
                  <td className="px-4 py-3 text-slate-600">{assessment.company || '--'}</td>
                  <td className="px-4 py-3 text-slate-600">{assessment.domain}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_BADGE[assessment.status] || 'bg-slate-100 text-slate-600'}`}>
                      {assessment.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(assessment.completed_at || assessment.created_at)}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {assessment.category ? (
                      <>
                        {CATEGORY_LABEL[assessment.category] || assessment.category}
                        {assessment.matched_use_case ? ` - ${assessment.matched_use_case}` : ''}
                      </>
                    ) : (
                      '--'
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
