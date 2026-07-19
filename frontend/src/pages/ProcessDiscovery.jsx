import SectionCard from '../components/SectionCard';
import { processSteps } from '../data/mock';

export default function ProcessDiscovery() {
  return (
    <SectionCard
      id="process-discovery"
      title="Process Discovery Module"
      description="Upload documents or describe a process manually, then map steps, decision points, and manual work."
    >
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
            Upload workflow, SOP, BPMN, Visio, or PDF documents.
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-5">
            <div className="mb-4 text-sm font-medium text-slate-950">Detected Process Steps</div>
            <div className="space-y-3">
              {processSteps.map((item, index) => (
                <div
                  key={item.step}
                  className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3"
                >
                  <div className="text-sm text-slate-700">
                    Step {index + 1}: {item.step}
                  </div>
                  <div className="rounded-full bg-blue-900/10 px-3 py-1 text-xs font-semibold text-blue-900">
                    {item.recommendation}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="text-sm font-medium text-slate-950">AI Extracted Signals</div>
          <ul className="mt-4 space-y-3 text-sm text-slate-600">
            <li>Process steps</li>
            <li>Decision points</li>
            <li>Exception handling</li>
            <li>Human involvement</li>
            <li>System interactions</li>
          </ul>
        </div>
      </div>
    </SectionCard>
  );
}
