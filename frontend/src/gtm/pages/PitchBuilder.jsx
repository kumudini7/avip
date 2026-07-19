import { useState } from 'react';
import Topbar from '../components/Topbar';
import { pitchBuilderIndustries, painPointsByIndustry } from '../data/mockData';
import { addEngagementKpi, createEngagement, generatePitchContent } from '../../services/api';

const steps = ['Industry', 'Pain points', 'Generate', 'Export'];

function pitchKey(industry, painPoints) {
  return `${industry}|${painPoints.slice().sort().join(',')}`;
}

export default function PitchBuilder({ onEngagementCreated, onNavigate }) {
  const [step, setStep] = useState(0);
  const [industry, setIndustry] = useState('');
  const [painPoints, setPainPoints] = useState([]);
  const [clientName, setClientName] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');
  const [created, setCreated] = useState(false);
  const [pitchContent, setPitchContent] = useState(null);
  const [generatedKey, setGeneratedKey] = useState('');
  const [pitchGenerating, setPitchGenerating] = useState(false);
  const [pitchError, setPitchError] = useState('');

  function togglePainPoint(point) {
    setPainPoints((current) =>
      current.includes(point) ? current.filter((item) => item !== point) : [...current, point],
    );
  }

  function goNext() {
    setStep((current) => Math.min(current + 1, steps.length - 1));
  }

  function goBack() {
    setStep((current) => Math.max(current - 1, 0));
  }

  const currentKey = pitchKey(industry, painPoints);
  const isStale = pitchContent !== null && generatedKey !== currentKey;

  const canProceedStep0 = Boolean(industry);
  const canProceedStep1 = painPoints.length > 0;
  const canProceedStep2 = Boolean(pitchContent) && !isStale;

  const asIs = pitchContent?.as_is || [];
  const toBe = pitchContent?.to_be || [];
  const kpiTemplate = pitchContent?.kpi_template || [];

  const slideOutline = [
    { title: 'Client challenge', body: painPoints.join(', ') || 'No pain points selected' },
    { title: 'As-is workflow', body: asIs.join(' → ') },
    { title: 'To-be workflow with agentic layers', body: toBe.join(' → ') },
    { title: 'KPI targets', body: kpiTemplate.map((item) => `${item.kpi}: ${item.baseline} → ${item.target}`).join('; ') },
    { title: 'Why Jade Global', body: 'Proven agentic AI delivery across manufacturing, BFSI, healthcare, and IT engagements.' },
  ];

  async function handleGeneratePitch() {
    setPitchGenerating(true);
    setPitchError('');
    try {
      const response = await generatePitchContent(industry, painPoints);
      setPitchContent(response.content);
      setGeneratedKey(currentKey);
    } catch (err) {
      setPitchError(err?.response?.data?.detail || 'Unable to generate pitch content. Try again.');
    } finally {
      setPitchGenerating(false);
    }
  }

  function handleExportOutline() {
    const lines = [`# ${industry} pitch outline — Jade Global Agentic AI Practice`, ''];
    slideOutline.forEach((slide, index) => {
      lines.push(`## Slide ${index + 1}: ${slide.title}`);
      lines.push(slide.body || '—');
      lines.push('');
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${(clientName || industry || 'pitch').toLowerCase().replace(/\s+/g, '-')}-outline.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function handleCreateEngagement() {
    if (!clientName.trim()) return;
    setCreating(true);
    setCreateError('');
    try {
      const engagement = await createEngagement({
        client_name: clientName,
        industry,
        stage: 'discovery',
        health: 'on_track',
      });
      await Promise.all(
        kpiTemplate.map((row) =>
          addEngagementKpi(engagement.id, {
            label: row.kpi,
            baseline_value: row.baseline,
            target_value: row.target,
            current_value: row.baseline,
            progress: 0,
          }),
        ),
      );
      await onEngagementCreated?.();
      setCreated(true);
    } catch (err) {
      setCreateError(err?.response?.data?.detail || 'Unable to create engagement.');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-6">
      <Topbar crumb="Pitch Builder" title="Generate a client-ready pitch" />

      <div className="flex items-center gap-2">
        {steps.map((label, index) => (
          <div key={label} className="flex flex-1 items-center gap-2">
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                index === step
                  ? 'bg-blue-700 text-white'
                  : index < step
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'bg-slate-100 text-slate-500'
              }`}
            >
              {index + 1}
            </div>
            <span className={`text-sm ${index === step ? 'font-medium text-slate-900' : 'text-slate-500'}`}>
              {label}
            </span>
            {index < steps.length - 1 ? <div className="h-px flex-1 bg-slate-200" /> : null}
          </div>
        ))}
      </div>

      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-6">
        {step === 0 ? (
          <div>
            <div className="text-sm font-semibold text-slate-900">Select industry vertical</div>
            <p className="mt-1 text-sm text-slate-500">Choose the client's industry to tailor the pitch.</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3">
              {pitchBuilderIndustries.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => {
                    setIndustry(item);
                    setPainPoints([]);
                  }}
                  className={`rounded-lg border-[0.5px] px-4 py-3 text-left text-sm font-medium transition ${
                    industry === item
                      ? 'border-blue-700 bg-blue-50 text-blue-700'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {step === 1 ? (
          <div>
            <div className="text-sm font-semibold text-slate-900">Select client pain points</div>
            <p className="mt-1 text-sm text-slate-500">Choose all that apply for {industry}.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {(painPointsByIndustry[industry] || []).map((point) => {
                const selected = painPoints.includes(point);
                return (
                  <button
                    key={point}
                    type="button"
                    onClick={() => togglePainPoint(point)}
                    className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition ${
                      selected ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {point}
                  </button>
                );
              })}
            </div>
          </div>
        ) : null}

        {step === 2 ? (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-slate-900">AI-generated workflow & KPIs</div>
                <p className="mt-1 text-sm text-slate-500">
                  Tailored to {industry}: {painPoints.join(', ')}.
                </p>
              </div>
              <button
                type="button"
                onClick={handleGeneratePitch}
                disabled={pitchGenerating}
                className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {pitchGenerating ? 'Generating...' : pitchContent ? 'Regenerate with AI' : 'Generate with AI'}
              </button>
            </div>
            {isStale ? (
              <p className="mt-2 text-xs text-amber-600">Pain points changed — regenerate to update the content below.</p>
            ) : null}
            {pitchError ? (
              <p className="mt-2 max-h-24 overflow-y-auto whitespace-pre-wrap text-xs text-rose-600">{pitchError}</p>
            ) : null}

            {pitchGenerating ? (
              <div className="mt-6 grid gap-4">
                {[0, 1, 2].map((key) => (
                  <div key={key} className="h-24 animate-pulse rounded-lg bg-slate-50" />
                ))}
              </div>
            ) : pitchContent && !isStale ? (
              <div className="mt-6 space-y-6">
                <div>
                  <div className="text-sm font-semibold text-slate-900">As-is workflow</div>
                  <ol className="mt-3 space-y-2">
                    {asIs.map((item, index) => (
                      <li key={item} className="flex gap-3 text-sm text-slate-600">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-500">
                          {index + 1}
                        </span>
                        {item}
                      </li>
                    ))}
                  </ol>
                </div>

                <div>
                  <div className="text-sm font-semibold text-slate-900">To-be workflow with agentic layers</div>
                  <ol className="mt-3 space-y-2">
                    {toBe.map((item, index) => (
                      <li key={item} className="flex gap-3 text-sm text-slate-600">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-medium text-blue-700">
                          {index + 1}
                        </span>
                        {item}
                      </li>
                    ))}
                  </ol>
                </div>

                <div>
                  <div className="text-sm font-semibold text-slate-900">KPI template</div>
                  <div className="mt-3 overflow-hidden rounded-lg border-[0.5px] border-slate-200">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b-[0.5px] border-slate-200 text-xs text-slate-500">
                          <th className="px-4 py-2 font-medium">KPI</th>
                          <th className="px-4 py-2 font-medium">Baseline</th>
                          <th className="px-4 py-2 font-medium">Target</th>
                        </tr>
                      </thead>
                      <tbody>
                        {kpiTemplate.map((row) => (
                          <tr key={row.kpi} className="border-b-[0.5px] border-slate-100 last:border-0">
                            <td className="px-4 py-2 text-slate-700">{row.kpi}</td>
                            <td className="px-4 py-2 text-slate-500">{row.baseline}</td>
                            <td className="px-4 py-2 font-medium text-slate-900">{row.target}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-6 rounded-lg border border-dashed border-slate-200 px-4 py-12 text-center text-sm text-slate-400">
                Click "Generate with AI" to create the as-is workflow, to-be workflow, and KPI template for this pitch.
              </div>
            )}
          </div>
        ) : null}

        {step === 3 ? (
          <div>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-slate-900">Slide outline</div>
                <p className="mt-1 text-sm text-slate-500">
                  {industry} pitch, {painPoints.length} pain point{painPoints.length === 1 ? '' : 's'} addressed.
                </p>
              </div>
              <button
                type="button"
                onClick={handleExportOutline}
                className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
              >
                Export outline
              </button>
            </div>
            <div className="mt-4 space-y-3">
              {slideOutline.map((slide, index) => (
                <div key={slide.title} className="rounded-lg border-[0.5px] border-slate-200 p-4">
                  <div className="text-xs font-medium text-slate-400">Slide {index + 1}</div>
                  <div className="mt-1 text-sm font-semibold text-slate-900">{slide.title}</div>
                  <p className="mt-1.5 text-sm leading-6 text-slate-600">{slide.body}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-lg border-[0.5px] border-slate-200 bg-slate-50 p-4">
              {created ? (
                <div className="flex items-center justify-between">
                  <div className="text-sm text-emerald-700">
                    Engagement created for {clientName}. Track it from the Engagements page.
                  </div>
                  <button
                    type="button"
                    onClick={() => onNavigate?.('engagements')}
                    className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800"
                  >
                    View engagements
                  </button>
                </div>
              ) : (
                <div className="flex flex-wrap items-end gap-3">
                  <label className="block flex-1 text-sm">
                    <span className="mb-1.5 block text-slate-600">Client name</span>
                    <input
                      value={clientName}
                      onChange={(event) => setClientName(event.target.value)}
                      placeholder="Acme Manufacturing"
                      className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-700"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={handleCreateEngagement}
                    disabled={creating || !clientName.trim()}
                    className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {creating ? 'Creating...' : 'Create engagement from this pitch'}
                  </button>
                </div>
              )}
              {createError ? <div className="mt-2 text-sm text-rose-600">{createError}</div> : null}
            </div>
          </div>
        ) : null}
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          onClick={goBack}
          disabled={step === 0}
          className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Back
        </button>
        {step < steps.length - 1 ? (
          <button
            type="button"
            onClick={goNext}
            disabled={(step === 0 && !canProceedStep0) || (step === 1 && !canProceedStep1) || (step === 2 && !canProceedStep2)}
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        ) : null}
      </div>
    </div>
  );
}
