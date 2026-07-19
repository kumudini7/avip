function formatDateTime(value) {
  if (!value) return 'Pending';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'Pending';
  return parsed.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function statusLabel(status) {
  if (status === 'completed') return 'Completed';
  if (status === 'in_progress') return 'In progress';
  return status || 'Unknown';
}

export default function AssessmentHistoryPanel({ assessments = [], onSelectAssessment, activeAssessmentId = null }) {
  return (
    <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Recent assessments</h3>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600">
          {assessments.length}
        </span>
      </div>

      <div className="mt-4 space-y-3">
        {assessments.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-400">
            No assessments yet. Your completed assessments will appear here.
          </div>
        ) : (
          assessments.slice(0, 5).map((item) => {
            const isSelected = activeAssessmentId === item.id;
            const canOpen = item.status === 'completed' && typeof onSelectAssessment === 'function';
            return (
            <button
              key={item.id}
              type="button"
              onClick={() => canOpen && onSelectAssessment(item)}
              disabled={!canOpen}
              className={`w-full rounded-lg border-[0.5px] px-4 py-3 text-left transition ${
                isSelected
                  ? 'border-blue-700 bg-blue-50'
                  : canOpen
                    ? 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                    : 'border-slate-200 bg-slate-50 opacity-70'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-900">{item.domain}</div>
                  <div className="mt-0.5 text-xs text-slate-500">
                    {formatDateTime(item.completed_at || item.created_at)}
                  </div>
                </div>
                <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-medium text-slate-600">
                  {statusLabel(item.status)}
                </span>
              </div>
              {item.matched_use_case ? (
                <div className="mt-2 truncate text-xs text-slate-600">{item.matched_use_case}</div>
              ) : null}
              {canOpen ? (
                <div className="mt-2 text-[11px] font-medium text-blue-700">Open dashboard and ROI</div>
              ) : null}
            </button>
            );
          })
        )}
      </div>
    </div>
  );
}
