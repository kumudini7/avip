import Topbar from '../components/Topbar';
import { caseStudies } from '../data/mockData';

export default function CaseStudies() {
  return (
    <div className="space-y-6">
      <Topbar crumb="Case Studies" title="Proof points to anchor a pitch" />

      <div className="grid gap-5 sm:grid-cols-2">
        {caseStudies.map((study) => (
          <div key={study.client} className="flex flex-col rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-sm font-semibold text-slate-500">
                {study.client.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <div className="text-sm font-semibold text-slate-900">{study.client}</div>
                <div className="text-xs text-slate-500">{study.industry}</div>
              </div>
            </div>

            <p className="mt-4 text-sm leading-6 text-slate-600">{study.summary}</p>

            <div className="mt-4 flex flex-wrap gap-2">
              {study.kpis.map((kpi) => (
                <span key={kpi.label} className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                  {kpi.label}: {kpi.value}
                </span>
              ))}
            </div>

            <button
              type="button"
              className="mt-5 self-start rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Use as anchor
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
