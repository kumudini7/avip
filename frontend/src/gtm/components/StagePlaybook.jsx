import { useEffect, useRef, useState } from 'react';
import { getStageState, saveStageState } from '../../services/api';
import { stageOrder } from '../data/mockData';
import ToolPill from './ToolPill';
import StageProgressPipeline from './StageProgressPipeline';
import EngagementSwitcher from './EngagementSwitcher';
import Toast from './Toast';

function Card({ title, children }) {
  return (
    <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
      <div className="text-sm font-semibold text-slate-900">{title}</div>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function ChevronIcon({ expanded }) {
  return (
    <svg
      viewBox="0 0 20 20"
      className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
      fill="currentColor"
    >
      <path
        fillRule="evenodd"
        d="M5.3 7.3a1 1 0 011.4 0L10 10.6l3.3-3.3a1 1 0 111.4 1.4l-4 4a1 1 0 01-1.4 0l-4-4a1 1 0 010-1.4z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export default function StagePlaybook({
  stageId,
  label,
  engagements = [],
  engagementsLoaded = false,
  selectedEngagementId,
  onSelectEngagement,
  onEngagementChanged,
  onNavigate,
}) {
  const [checklist, setChecklist] = useState(null);
  const [notes, setNotes] = useState('');
  const [content, setContent] = useState(null);
  const [stageCompletion, setStageCompletion] = useState({});
  const [loadingState, setLoadingState] = useState(false);
  const [completionLoading, setCompletionLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [expandedSteps, setExpandedSteps] = useState(() => new Set());
  const [openTool, setOpenTool] = useState(null);
  const [copied, setCopied] = useState(false);
  const [presentMode, setPresentMode] = useState(false);

  const notesTimerRef = useRef(null);
  const toastTimerRef = useRef(null);

  useEffect(() => {
    if (!selectedEngagementId) {
      setChecklist(null);
      setNotes('');
      setContent(null);
      setStageCompletion({});
      return;
    }

    let cancelled = false;
    setCompletionLoading(true);
    setLoadingState(true);
    setError('');

    Promise.all(stageOrder.map((stage) => getStageState(selectedEngagementId, stage)))
      .then((results) => {
        if (cancelled) return;
        const completionMap = {};
        results.forEach((state, index) => {
          completionMap[stageOrder[index]] = state.checklist_json.length > 0 && state.checklist_json.every(Boolean);
        });
        setStageCompletion(completionMap);

        const currentIndex = stageOrder.indexOf(stageId);
        const currentState = results[currentIndex];
        setChecklist(currentState.checklist_json);
        setNotes(currentState.notes || '');
        setContent(currentState.generated_content || null);
      })
      .catch(() => {
        if (!cancelled) setError('Unable to load stage progress for this engagement.');
      })
      .finally(() => {
        if (!cancelled) {
          setCompletionLoading(false);
          setLoadingState(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [selectedEngagementId, stageId]);

  useEffect(
    () => () => {
      if (notesTimerRef.current) clearTimeout(notesTimerRef.current);
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    },
    [],
  );

  useEffect(() => {
    if (!presentMode) return undefined;
    function handleKey(event) {
      if (event.key === 'Escape') setPresentMode(false);
    }
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [presentMode]);

  function showToast(message) {
    setToast(message);
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    toastTimerRef.current = setTimeout(() => setToast(''), 2500);
  }

  async function persist(nextChecklist, nextNotes) {
    setSaving(true);
    setError('');
    try {
      await saveStageState(selectedEngagementId, stageId, {
        checklist_json: nextChecklist,
        notes: nextNotes,
      });
      const complete = nextChecklist.length > 0 && nextChecklist.every(Boolean);
      setStageCompletion((current) => ({ ...current, [stageId]: complete }));
      await onEngagementChanged?.();
      return true;
    } catch (err) {
      setError('Unable to save progress.');
      return false;
    } finally {
      setSaving(false);
    }
  }

  async function toggle(index) {
    if (!checklist) return;
    const next = checklist.map((value, i) => (i === index ? !value : value));
    setChecklist(next);
    await persist(next, notes);
  }

  function handleNotesChange(event) {
    const value = event.target.value;
    setNotes(value);
    if (notesTimerRef.current) clearTimeout(notesTimerRef.current);
    notesTimerRef.current = setTimeout(async () => {
      if (!checklist) return;
      const ok = await persist(checklist, value);
      if (ok) showToast('Saved');
    }, 500);
  }

  function toggleStep(index) {
    setExpandedSteps((current) => {
      const next = new Set(current);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  }

  async function handleCopyPitchLine() {
    if (!content?.pitch_line) return;
    try {
      await navigator.clipboard.writeText(content.pitch_line);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Clipboard API unavailable (e.g. insecure context) - fail silently.
    }
  }

  const completedCount = checklist ? checklist.filter(Boolean).length : 0;
  const totalCount = content?.checklist?.length || 0;
  const isStageComplete = checklist ? completedCount === totalCount && totalCount > 0 : false;

  if (presentMode) {
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto bg-white p-10">
        <div className="mx-auto max-w-3xl space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">GTM stage</div>
              <h1 className="mt-1 text-3xl font-semibold text-slate-900">{label}</h1>
            </div>
            <button
              type="button"
              onClick={() => setPresentMode(false)}
              className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Exit presentation
            </button>
          </div>

          <div>
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">Objective</div>
            <p className="mt-2 text-lg leading-8 text-slate-700">{content?.objective}</p>
          </div>

          <div>
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">Client value</div>
            <p className="mt-2 text-lg leading-8 text-slate-700">{content?.client_value}</p>
          </div>

          <div>
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">Approach</div>
            <ol className="mt-3 space-y-3">
              {(content?.approach || []).map((step, index) => (
                <li key={step.step} className="flex gap-4 text-base text-slate-700">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-medium text-slate-500">
                    {index + 1}
                  </span>
                  <span className="leading-7">{step.step}</span>
                </li>
              ))}
            </ol>
          </div>

          <div>
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">Tools & techniques</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {(content?.tools || []).map((tool) => (
                <span key={tool.name} className="rounded-full bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700">
                  {tool.name}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-xl border-[0.5px] border-slate-200 bg-slate-50 p-6">
            <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">Example pitch line</div>
            <p className="mt-3 text-lg italic leading-8 text-slate-800">{content?.pitch_line}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {engagementsLoaded && engagements.length > 0 ? (
        <StageProgressPipeline
          currentStageId={stageId}
          completion={stageCompletion}
          loading={completionLoading}
          onNavigate={onNavigate}
        />
      ) : null}

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-slate-400">GTM stage</div>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">{label}</h1>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => setPresentMode(true)}
            disabled={!content}
            className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Present mode
          </button>
          {engagementsLoaded && engagements.length > 0 ? (
            <EngagementSwitcher
              engagements={engagements}
              selectedEngagementId={selectedEngagementId}
              onSelect={onSelectEngagement}
            />
          ) : null}
        </div>
      </div>

      {engagementsLoaded && engagements.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-400">
          No engagements yet. Create one from the Engagements page to generate AI playbook content here.
        </div>
      ) : null}

      {loadingState ? (
        <div className="grid gap-6 lg:grid-cols-2">
          {[0, 1, 2, 3].map((key) => (
            <div key={key} className="h-32 animate-pulse rounded-xl bg-slate-50" />
          ))}
        </div>
      ) : content ? (
        <>
          <div className="grid gap-6 lg:grid-cols-2">
            <Card title="Objective">
              <p className="text-sm leading-6 text-slate-600">{content.objective}</p>
            </Card>

            <Card title="Client value">
              <p className="text-sm leading-6 text-slate-600">{content.client_value}</p>
            </Card>

            <Card title="Approach">
              <div className="space-y-0.5">
                {content.approach.map((step, index) => {
                  const isExpanded = expandedSteps.has(index);
                  return (
                    <div key={step.step}>
                      <button
                        type="button"
                        onClick={() => toggleStep(index)}
                        aria-expanded={isExpanded}
                        className="flex w-full items-start gap-3 rounded-lg px-1 py-1.5 text-left text-sm text-slate-600 transition hover:bg-slate-50"
                      >
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-500">
                          {index + 1}
                        </span>
                        <span className="flex-1 leading-5">{step.step}</span>
                        <ChevronIcon expanded={isExpanded} />
                      </button>
                      {isExpanded ? (
                        <p className="ml-8 mr-2 pb-2 pt-0.5 text-xs leading-5 text-slate-500">{step.detail}</p>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </Card>

            <Card title="Tools & techniques">
              <div className="flex flex-wrap gap-2">
                {content.tools.map((tool) => (
                  <ToolPill
                    key={tool.name}
                    label={tool.name}
                    description={tool.description}
                    isOpen={openTool === tool.name}
                    onToggle={(value) => setOpenTool((current) => (current === value ? null : value))}
                  />
                ))}
              </div>
            </Card>
          </div>

          <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <div className="text-sm font-semibold text-slate-900">Example pitch line</div>
              <button
                type="button"
                onClick={handleCopyPitchLine}
                className="flex items-center gap-1.5 rounded-lg border-[0.5px] border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 transition hover:bg-slate-50"
              >
                {copied ? (
                  <span className="text-emerald-700">Copied!</span>
                ) : (
                  <>
                    <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="currentColor">
                      <path d="M7 3a2 2 0 00-2 2v9a2 2 0 002 2h7a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H7zm0 2h3v3a1 1 0 001 1h3v7H7V5z" />
                      <path d="M4 7a1 1 0 00-1 1v9a2 2 0 002 2h7a1 1 0 100-2H5V8a1 1 0 00-1-1z" />
                    </svg>
                    Copy
                  </>
                )}
              </button>
            </div>
            <p className="mt-3 text-sm italic leading-6 text-slate-600">{content.pitch_line}</p>
          </div>

          {selectedEngagementId ? (
            <div className="grid gap-6 lg:grid-cols-2">
              <div
                className={`rounded-xl border-[0.5px] p-5 transition-colors ${
                  isStageComplete ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="text-sm font-semibold text-slate-900">Activity checklist</div>
                  <span className="text-xs text-slate-500">
                    {`${completedCount}/${totalCount} complete`}
                    {saving ? ' · Saving...' : ''}
                  </span>
                </div>

                <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`h-full rounded-full transition-all ${isStageComplete ? 'bg-emerald-500' : 'bg-blue-600'}`}
                    style={{ width: `${totalCount ? (completedCount / totalCount) * 100 : 0}%` }}
                  />
                </div>

                {isStageComplete ? (
                  <div className="mt-3 flex items-center gap-2 rounded-lg bg-emerald-100 px-3 py-2 text-sm font-medium text-emerald-800">
                    <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor">
                      <path
                        fillRule="evenodd"
                        d="M16.7 5.3a1 1 0 010 1.4l-7 7a1 1 0 01-1.4 0l-3-3a1 1 0 111.4-1.4L8.3 11.6l6.3-6.3a1 1 0 011.4 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Stage complete
                  </div>
                ) : null}

                <div className="mt-4 space-y-2">
                  {content.checklist.map((item, index) => (
                    <label
                      key={item}
                      className="flex cursor-pointer items-start gap-3 rounded-lg px-2 py-2 text-sm text-slate-600 hover:bg-slate-50"
                    >
                      <input
                        type="checkbox"
                        checked={Boolean(checklist?.[index])}
                        disabled={!checklist}
                        onChange={() => toggle(index)}
                        className="mt-0.5 h-4 w-4 rounded border-slate-300 text-blue-700 focus:ring-blue-700"
                      />
                      <span className={checklist?.[index] ? 'text-slate-400 line-through' : ''}>{item}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
                <div className="text-sm font-semibold text-slate-900">Notes & client-specific inputs</div>
                <textarea
                  value={notes}
                  onChange={handleNotesChange}
                  rows={8}
                  disabled={!checklist}
                  placeholder={`Capture client-specific findings, decisions, or blockers for the ${label} stage...`}
                  className="mt-3 w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-blue-700"
                />
                <div className="mt-1.5 text-right text-xs text-slate-400">{notes.length} characters</div>
              </div>
            </div>
          ) : null}
        </>
      ) : selectedEngagementId ? (
        <div className="rounded-xl border border-dashed border-slate-200 px-4 py-12 text-center text-sm text-slate-400">
          No content generated yet for this engagement. Go to the Engagements page and click "Generate playbook" to
          create the objective, approach, tools, pitch line, and checklist for all 5 stages.
        </div>
      ) : null}

      {error ? <div className="rounded-lg border-[0.5px] border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      <Toast message={toast} />
    </div>
  );
}
