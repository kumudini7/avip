import { useState } from 'react';
import Topbar from '../components/Topbar';
import { industries as industryOptions, stageLabels, stageOrder } from '../data/mockData';
import { createEngagement, generatePlaybook } from '../../services/api';

const healthOptions = ['on_track', 'at_risk'];

const healthStyles = {
  on_track: 'bg-emerald-50 text-emerald-700',
  at_risk: 'bg-amber-50 text-amber-700',
};

const healthLabels = {
  on_track: 'On track',
  at_risk: 'At risk',
};

const stageStyles = {
  discovery: 'bg-emerald-50 text-emerald-700',
  design: 'bg-emerald-50 text-emerald-700',
  integration: 'bg-blue-50 text-blue-700',
  measurement: 'bg-slate-100 text-slate-500',
  scale: 'bg-slate-100 text-slate-500',
};

const defaultForm = {
  client_name: '',
  industry: industryOptions[0],
  stage: 'discovery',
  health: 'on_track',
};

export default function Engagements({ engagements = [], engagementsLoaded = false, onEngagementChanged }) {
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(defaultForm);
  const [saving, setSaving] = useState(false);
  const [generatingId, setGeneratingId] = useState(null);
  const [resultById, setResultById] = useState({});

  async function handleCreate(event) {
    event.preventDefault();
    if (!form.client_name.trim()) return;

    setSaving(true);
    setError('');
    try {
      await createEngagement(form);
      setForm(defaultForm);
      setShowForm(false);
      await onEngagementChanged?.();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create engagement.');
    } finally {
      setSaving(false);
    }
  }

  async function handleGeneratePlaybook(engagementId) {
    setGeneratingId(engagementId);
    setResultById((current) => ({ ...current, [engagementId]: null }));
    try {
      const response = await generatePlaybook(engagementId);
      const generated = response.results.filter((item) => item.status === 'generated').length;
      const failed = response.results.filter((item) => item.status === 'failed');
      setResultById((current) => ({
        ...current,
        [engagementId]: { generated, total: response.results.length, failed },
      }));
      await onEngagementChanged?.();
    } catch (err) {
      setResultById((current) => ({
        ...current,
        [engagementId]: { error: err?.response?.data?.detail || 'Unable to generate playbook.' },
      }));
    } finally {
      setGeneratingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <Topbar
        crumb="Engagements"
        title="All active client engagements"
        actions={
          <button
            type="button"
            onClick={() => setShowForm((value) => !value)}
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800"
          >
            New engagement
          </button>
        }
      />

      {error ? <div className="rounded-lg border-[0.5px] border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      {showForm ? (
        <form onSubmit={handleCreate} className="grid gap-4 rounded-xl border-[0.5px] border-slate-200 bg-white p-5 sm:grid-cols-2 lg:grid-cols-4">
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-600">Client name</span>
            <input
              value={form.client_name}
              onChange={(event) => setForm({ ...form, client_name: event.target.value })}
              className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-700"
              placeholder="Acme Manufacturing"
              required
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-600">Industry</span>
            <select
              value={form.industry}
              onChange={(event) => setForm({ ...form, industry: event.target.value })}
              className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-700"
            >
              {industryOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-600">Starting stage</span>
            <select
              value={form.stage}
              onChange={(event) => setForm({ ...form, stage: event.target.value })}
              className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-700"
            >
              {stageOrder.map((id) => (
                <option key={id} value={id}>
                  {stageLabels[id]}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="mb-1.5 block text-slate-600">Health</span>
            <select
              value={form.health}
              onChange={(event) => setForm({ ...form, health: event.target.value })}
              className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-700"
            >
              {healthOptions.map((id) => (
                <option key={id} value={id}>
                  {healthLabels[id]}
                </option>
              ))}
            </select>
          </label>
          <div className="sm:col-span-2 lg:col-span-4">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800 disabled:opacity-60"
            >
              {saving ? 'Creating...' : 'Create engagement'}
            </button>
          </div>
        </form>
      ) : null}

      <div className="overflow-hidden rounded-xl border-[0.5px] border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b-[0.5px] border-slate-200 text-xs text-slate-500">
              <th className="px-5 py-3 font-medium">Client</th>
              <th className="px-5 py-3 font-medium">Industry</th>
              <th className="px-5 py-3 font-medium">Stage</th>
              <th className="px-5 py-3 font-medium">Owner</th>
              <th className="px-5 py-3 font-medium">Start date</th>
              <th className="px-5 py-3 font-medium">Health</th>
              <th className="px-5 py-3 font-medium">AI playbook</th>
            </tr>
          </thead>
          <tbody>
            {!engagementsLoaded ? (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-sm text-slate-400">
                  Loading engagements...
                </td>
              </tr>
            ) : engagements.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-sm text-slate-400">
                  No engagements yet. Create one to get started.
                </td>
              </tr>
            ) : (
              engagements.map((item) => {
                const result = resultById[item.id];
                return (
                  <tr key={item.id} className="border-b-[0.5px] border-slate-100 last:border-0 hover:bg-slate-50">
                    <td className="px-5 py-4 font-medium text-slate-900">{item.client_name}</td>
                    <td className="px-5 py-4 text-slate-600">{item.industry}</td>
                    <td className="px-5 py-4">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${stageStyles[item.stage]}`}>
                        {stageLabels[item.stage]}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-slate-600">{item.owner_name}</td>
                    <td className="px-5 py-4 text-slate-600">{item.started_at}</td>
                    <td className="px-5 py-4">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${healthStyles[item.health]}`}>
                        {healthLabels[item.health] || item.health}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <button
                        type="button"
                        onClick={() => handleGeneratePlaybook(item.id)}
                        disabled={generatingId === item.id}
                        className="rounded-lg border-[0.5px] border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {generatingId === item.id ? 'Generating...' : 'Generate playbook'}
                      </button>
                      {result ? (
                        result.error ? (
                          <div className="mt-1 max-w-[220px] text-xs text-rose-600">{result.error}</div>
                        ) : (
                          <div className="mt-1 text-xs text-slate-500">
                            {result.generated}/{result.total} stages generated
                            {result.failed.length > 0 ? ` (${result.failed.length} failed)` : ''}
                          </div>
                        )
                      ) : null}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
