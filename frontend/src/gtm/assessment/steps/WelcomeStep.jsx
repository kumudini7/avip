import AssessmentHistoryPanel from './AssessmentHistoryPanel';

export default function WelcomeStep({ clientName, onStart, assessments = [], onSelectAssessment, activeAssessmentId = null }) {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-8">
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">AutoAssess</div>
        <h1 className="mt-3 text-2xl font-semibold text-slate-900">Welcome, {clientName || 'there'}</h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          AutoAssess is a short, guided assessment that helps us understand your process and business context.
          Answer a handful of questions and we'll tailor the automation fit, show relevant examples, and build an ROI
          model around your numbers.
        </p>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border-[0.5px] border-slate-200 bg-slate-50 p-4">
            <div className="text-lg font-semibold text-slate-900">~5 mins</div>
            <div className="text-xs text-slate-500">to complete</div>
          </div>
          <div className="rounded-lg border-[0.5px] border-slate-200 bg-slate-50 p-4">
            <div className="text-lg font-semibold text-slate-900">Tailored</div>
            <div className="text-xs text-slate-500">to your process</div>
          </div>
          <div className="rounded-lg border-[0.5px] border-slate-200 bg-slate-50 p-4">
            <div className="text-lg font-semibold text-slate-900">Client-ready</div>
            <div className="text-xs text-slate-500">summary & ROI view</div>
          </div>
        </div>
        <button
          type="button"
          onClick={onStart}
          className="mt-8 w-full rounded-lg bg-blue-700 px-4 py-3 text-sm font-medium text-white transition hover:bg-blue-800 sm:w-auto"
        >
          Start assessment
        </button>
      </div>

      <AssessmentHistoryPanel
        assessments={assessments}
        onSelectAssessment={onSelectAssessment}
        activeAssessmentId={activeAssessmentId}
      />
    </div>
  );
}
