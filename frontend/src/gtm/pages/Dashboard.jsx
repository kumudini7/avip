import { useEffect, useState } from 'react';
import Topbar from '../components/Topbar';
import StagePipeline from '../components/StagePipeline';
import MetricCard from '../components/MetricCard';
import { activityDotColor, timeAgo } from '../data/mockData';
import { getDashboardSummary, getKpiTracker, listActivity } from '../../services/api';

function formatDays(value) {
  return value === null || value === undefined ? '—' : `${value}d`;
}

function formatCurrency(value) {
  if (!value) return '$0';
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value}`;
}

export default function Dashboard({ onNavigate, engagements = [] }) {
  const availableIndustries = Array.from(
    new Set(engagements.map((item) => item.industry).filter(Boolean)),
  );
  const [industry, setIndustry] = useState('');
  const [summary, setSummary] = useState(null);
  const [kpiRows, setKpiRows] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');
      try {
        const [summaryData, activityData] = await Promise.all([getDashboardSummary(), listActivity(5)]);
        if (cancelled) return;
        setSummary(summaryData);
        setActivity(activityData);
      } catch (err) {
        if (!cancelled) setError('Unable to load dashboard data.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const primaryEngagement = engagements.find((item) => !item.closed_at) || null;
  const primaryStage = primaryEngagement ? primaryEngagement.stage : null;

  useEffect(() => {
    if (availableIndustries.length === 0) {
      setIndustry('');
      setKpiRows([]);
      return;
    }

    if (!industry || !availableIndustries.includes(industry)) {
      setIndustry(availableIndustries[0]);
    }
  }, [availableIndustries, industry]);

  useEffect(() => {
    if (!industry) {
      setKpiRows([]);
      return undefined;
    }

    let cancelled = false;

    getKpiTracker(industry)
      .then((rows) => {
        if (!cancelled) setKpiRows(rows);
      })
      .catch(() => {
        if (!cancelled) setKpiRows([]);
      });

    return () => {
      cancelled = true;
    };
  }, [industry]);

  const metrics = summary
    ? [
        { label: 'Active engagements', value: String(summary.active_engagements), hint: null },
        {
          label: 'Avg. cycle time',
          value: formatDays(summary.avg_cycle_time_days),
          hint: summary.baseline_cycle_time_days !== null ? `vs ${formatDays(summary.baseline_cycle_time_days)} baseline` : null,
        },
        { label: 'KPIs on track', value: `${summary.kpis_on_track}/${summary.kpis_total}`, hint: null },
        { label: 'Est. ROI delivered', value: formatCurrency(summary.est_roi_delivered), hint: null },
      ]
    : [];

  return (
    <div className="space-y-6">
      <Topbar
        crumb="Dashboard"
        title="Active engagements overview"
        actions={
          <>
            <button
              type="button"
              className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Export
            </button>
            <button
              type="button"
              onClick={() => onNavigate?.('pitch-builder')}
              className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-800"
            >
              New engagement
            </button>
          </>
        }
      />

      {error ? <div className="rounded-lg border-[0.5px] border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}

      <StagePipeline currentStage={primaryStage} onSelectStage={onNavigate} />

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {[0, 1, 2, 3].map((key) => (
            <div key={key} className="h-24 animate-pulse rounded-xl bg-slate-50" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <MetricCard key={metric.label} label={metric.label} value={metric.value} hint={metric.hint} />
          ))}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="text-sm font-semibold text-slate-900">KPI tracker</div>
            <div className="flex flex-wrap gap-2">
              {availableIndustries.length === 0 ? (
                <span className="text-xs text-slate-400">Create engagements to see industry KPIs.</span>
              ) : (
                availableIndustries.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => setIndustry(item)}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                      industry === item ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {item}
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="mt-5 space-y-4">
            {kpiRows.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-400">
                No KPI data yet for {industry}. Add KPIs to an engagement to see them here.
              </div>
            ) : (
              kpiRows.map((row) => (
                <div key={row.label} className="grid grid-cols-[1fr_auto] items-center gap-4">
                  <div>
                    <div className="flex items-center justify-between text-sm text-slate-700">
                      <span>{row.label}</span>
                    </div>
                    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-blue-600" style={{ width: `${row.progress}%` }} />
                    </div>
                  </div>
                  <div className="text-sm font-semibold text-slate-900">{row.current_value ?? `${row.progress}%`}</div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <div className="text-sm font-semibold text-slate-900">Recent activity</div>
          <div className="mt-4 space-y-4">
            {activity.length === 0 ? (
              <div className="rounded-lg border border-dashed border-slate-200 px-4 py-8 text-center text-sm text-slate-400">
                No activity yet. Create an engagement to get started.
              </div>
            ) : (
              activity.map((item) => (
                <div key={item.id} className="flex gap-3">
                  <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${activityDotColor(item.type)}`} />
                  <div className="min-w-0">
                    <div className="text-sm leading-5 text-slate-700">{item.text}</div>
                    <div className="mt-0.5 text-xs text-slate-400">
                      {timeAgo(item.created_at)} &middot; {item.author}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
