import { useEffect, useState } from 'react';
import Topbar from '../components/Topbar';
import { kpiLibrary as fallbackKpiLibrary } from '../data/mockData';
import { addEngagementKpi, getUseCases } from '../../services/api';

function toKpiRow(entry) {
  if (entry?.title) {
    const benchmarks = entry.roi_benchmarks || {};
    const automation = benchmarks.auto_processing_pct ?? 0;
    const payback = benchmarks.payback_months ?? 'n/a';
    const timeSaved = benchmarks.time_saved_mins ?? 0;
    return {
      industry: entry.domain,
      useCase: entry.title,
      baseline: 'Current manual process',
      target: timeSaved ? `~${timeSaved} mins per cycle` : `${automation}% automated`,
      improvement: timeSaved ? `${timeSaved} mins saved` : `+${automation}% automation`,
      outcome: entry.value_props?.[0] || `Payback ~${payback} months`,
    };
  }
  return entry;
}

export default function KpiLibrary({ engagements = [], onEngagementChanged }) {
  const [filter, setFilter] = useState('All');
  const [openRow, setOpenRow] = useState(null);
  const [targetEngagement, setTargetEngagement] = useState('');
  const [cloning, setCloning] = useState(false);
  const [clonedRow, setClonedRow] = useState(null);
  const [rows, setRows] = useState(fallbackKpiLibrary);

  useEffect(() => {
    let active = true;
    getUseCases()
      .then((data) => {
        if (!active) return;
        setRows(data.map(toKpiRow));
      })
      .catch(() => {
        if (active) setRows(fallbackKpiLibrary);
      });
    return () => {
      active = false;
    };
  }, []);

  const industryFilters = ['All', ...Array.from(new Set(rows.map((row) => row.industry)))];
  const visibleRows = filter === 'All' ? rows : rows.filter((row) => row.industry === filter);

  function openCloneRow(rowKey) {
    setOpenRow(rowKey);
    setClonedRow(null);
    setTargetEngagement(engagements[0]?.id || '');
  }

  async function handleClone(row) {
    if (!targetEngagement) return;
    setCloning(true);
    try {
      await addEngagementKpi(targetEngagement, {
        label: row.useCase,
        baseline_value: row.baseline,
        target_value: row.target,
        current_value: row.baseline,
        progress: 0,
      });
      await onEngagementChanged?.();
      setClonedRow(`${row.industry}-${row.useCase}`);
      setOpenRow(null);
    } finally {
      setCloning(false);
    }
  }

  return (
    <div className="space-y-6">
      <Topbar crumb="KPI Library" title="Benchmarked KPI templates by industry" />

      <div className="flex flex-wrap gap-2">
        {industryFilters.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setFilter(item)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              filter === item ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="overflow-hidden rounded-xl border-[0.5px] border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b-[0.5px] border-slate-200 text-xs text-slate-500">
              <th className="px-5 py-3 font-medium">Industry</th>
              <th className="px-5 py-3 font-medium">Use case</th>
              <th className="px-5 py-3 font-medium">Baseline metric</th>
              <th className="px-5 py-3 font-medium">Target metric</th>
              <th className="px-5 py-3 font-medium">% improvement</th>
              <th className="px-5 py-3 font-medium">Business outcome</th>
              <th className="px-5 py-3 font-medium" />
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => {
              const rowKey = `${row.industry}-${row.useCase}`;
              return (
                <tr key={rowKey} className="border-b-[0.5px] border-slate-100 last:border-0 hover:bg-slate-50">
                  <td className="px-5 py-4 text-slate-600">{row.industry}</td>
                  <td className="px-5 py-4 font-medium text-slate-900">{row.useCase}</td>
                  <td className="px-5 py-4 text-slate-500">{row.baseline}</td>
                  <td className="px-5 py-4 text-slate-900">{row.target}</td>
                  <td className="px-5 py-4 font-medium text-emerald-700">{row.improvement}</td>
                  <td className="px-5 py-4 text-slate-600">{row.outcome}</td>
                  <td className="px-5 py-4">
                    {clonedRow === rowKey ? (
                      <span className="text-xs font-medium text-emerald-700">Added</span>
                    ) : openRow === rowKey ? (
                      <div className="flex items-center gap-2">
                        <select
                          value={targetEngagement}
                          onChange={(event) => setTargetEngagement(Number(event.target.value))}
                          className="rounded-lg border-[0.5px] border-slate-200 px-2 py-1.5 text-xs outline-none focus:border-blue-700"
                        >
                          {engagements.map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.client_name}
                            </option>
                          ))}
                        </select>
                        <button
                          type="button"
                          onClick={() => handleClone(row)}
                          disabled={cloning || !targetEngagement}
                          className="rounded-lg bg-blue-700 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-blue-800 disabled:opacity-50"
                        >
                          {cloning ? 'Adding...' : 'Add'}
                        </button>
                        <button
                          type="button"
                          onClick={() => setOpenRow(null)}
                          className="text-xs text-slate-400 hover:text-slate-600"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => openCloneRow(rowKey)}
                        disabled={engagements.length === 0}
                        className="rounded-lg border-[0.5px] border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                        title={engagements.length === 0 ? 'Create an engagement first' : undefined}
                      >
                        Clone to engagement
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
