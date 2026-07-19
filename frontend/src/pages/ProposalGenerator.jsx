import SectionCard from '../components/SectionCard';

const exportsList = ['Executive Summary', 'ROI', 'Risks', 'Roadmap', 'PDF', 'PowerPoint', 'Word'];

export default function ProposalGenerator() {
  return (
    <SectionCard
      id="proposal-generator"
      title="Proposal Generator"
      description="Create consultant-ready outputs with a single workflow: analysis, recommendation, business case, and presentation."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="text-sm font-medium text-slate-950">Included Outputs</div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {exportsList.map((item) => (
              <div key={item} className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="text-sm font-medium text-slate-950">Scenario Comparison</div>
          <div className="mt-4 space-y-3 text-sm text-slate-600">
            <div className="rounded-xl bg-slate-50 px-4 py-3">Scenario A: Only RPA - ROI 120%</div>
            <div className="rounded-xl bg-slate-50 px-4 py-3">Scenario B: RPA + OCR - ROI 185%</div>
            <div className="rounded-xl bg-slate-50 px-4 py-3">Scenario C: RPA + LLM - ROI 290%</div>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
