import { useEffect, useRef, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { downloadAssessmentReport, saveRoiInputs } from '../../../services/api';

const CURRENT_COLOR = '#64748b';
const POST_COLOR = '#059669';
const LINE_COLOR = '#1d4ed8';

function formatMoney(value, currency) {
  return `${currency} ${Math.round(value).toLocaleString()}`;
}

export default function RoiCalculatorTab({ assessmentId, result, onRoiUpdated, readOnly = false }) {
  const [volumePerMonth, setVolumePerMonth] = useState(result.roi_input?.volume_per_month ?? 1000);
  const [teamSize, setTeamSize] = useState(result.roi_input?.team_size ?? 5);
  const [avgFteCost, setAvgFteCost] = useState(result.roi_input?.avg_fte_cost ?? 600000);
  const [currency, setCurrency] = useState(result.roi_input?.currency ?? 'INR');
  const [roi, setRoi] = useState(result.roi ?? null);
  const [downloading, setDownloading] = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (readOnly) return undefined;
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      saveRoiInputs(assessmentId, {
        volume_per_month: volumePerMonth,
        team_size: teamSize,
        avg_fte_cost: avgFteCost,
        currency,
      })
        .then((data) => {
          setRoi(data);
          onRoiUpdated?.(data);
        })
        .catch(() => {});
    }, 350);
    return () => clearTimeout(debounceRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [volumePerMonth, teamSize, avgFteCost, currency, assessmentId, readOnly]);

  async function handleDownload() {
    setDownloading(true);
    try {
      const blob = await downloadAssessmentReport(assessmentId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `autoassess-report-${assessmentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setDownloading(false);
    }
  }

  const barData = roi
    ? [
        { name: 'Annual cost', Current: roi.current_annual_cost, 'Post-automation': roi.post_automation_cost },
      ]
    : [];
  const lineData = roi ? roi.chart_series.map((value, index) => ({ month: index + 1, value })) : [];

  return (
    <div className="space-y-6">
      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-900">ROI inputs</h3>
          <div className="flex gap-1 rounded-full bg-slate-100 p-1">
            {['INR', 'USD'].map((option) => (
              <button
                key={option}
                type="button"
                disabled={readOnly}
                onClick={() => setCurrency(option)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  currency === option ? 'bg-blue-700 text-white' : 'text-slate-600 hover:bg-slate-200'
                } disabled:cursor-not-allowed`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-5 grid gap-6 sm:grid-cols-3">
          <div>
            <div className="flex justify-between text-sm text-slate-600">
              <span>Volume per month</span>
              <span className="font-medium text-slate-900">{volumePerMonth.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min={100}
              max={10000}
              step={100}
              value={volumePerMonth}
              disabled={readOnly}
              onChange={(event) => setVolumePerMonth(Number(event.target.value))}
              className="mt-2 w-full accent-blue-700 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <div className="flex justify-between text-sm text-slate-600">
              <span>Team size</span>
              <span className="font-medium text-slate-900">{teamSize}</span>
            </div>
            <input
              type="range"
              min={1}
              max={50}
              step={1}
              value={teamSize}
              disabled={readOnly}
              onChange={(event) => setTeamSize(Number(event.target.value))}
              className="mt-2 w-full accent-blue-700 disabled:cursor-not-allowed"
            />
          </div>
          <div>
            <div className="mb-2 text-sm text-slate-600">Avg FTE cost / year ({currency})</div>
            <input
              type="number"
              min={0}
              value={avgFteCost}
              disabled={readOnly}
              onChange={(event) => setAvgFteCost(Number(event.target.value))}
              className="w-full rounded-lg border-[0.5px] border-slate-200 px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-700 disabled:cursor-not-allowed disabled:bg-slate-50"
            />
          </div>
        </div>
      </div>

      {roi ? (
        <>
          <div className="overflow-hidden rounded-xl border-[0.5px] border-slate-200 bg-white">
            <table className="w-full text-sm">
              <tbody>
                {[
                  ['Current annual cost', formatMoney(roi.current_annual_cost, roi.currency)],
                  ['Post-automation cost', formatMoney(roi.post_automation_cost, roi.currency)],
                  ['Implementation cost', formatMoney(roi.implementation_cost, roi.currency)],
                  ['Year 1 net saving', formatMoney(roi.year1_net_saving, roi.currency)],
                  ['Year 2 saving', formatMoney(roi.year2_saving, roi.currency)],
                  ['Payback period', roi.payback_months ? `${roi.payback_months} months` : 'N/A'],
                ].map(([label, value]) => (
                  <tr key={label} className="border-b-[0.5px] border-slate-100 last:border-0">
                    <td className="px-4 py-3 text-slate-600">{label}</td>
                    <td className="px-4 py-3 text-right font-medium text-slate-900">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-slate-900">Current vs post-automation cost</h3>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip formatter={(value) => formatMoney(value, roi.currency)} />
                    <Legend />
                    <Bar dataKey="Current" fill={CURRENT_COLOR} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Post-automation" fill={POST_COLOR} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-slate-900">Cumulative ROI over 36 months</h3>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={lineData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip formatter={(value) => formatMoney(value, roi.currency)} labelFormatter={(m) => `Month ${m}`} />
                    <Line type="monotone" dataKey="value" stroke={LINE_COLOR} strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {readOnly ? null : (
            <button
              type="button"
              onClick={handleDownload}
              disabled={downloading}
              className="rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {downloading ? 'Preparing report...' : 'Download report'}
            </button>
          )}
        </>
      ) : (
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5 text-sm text-slate-500">
          No ROI inputs saved yet.
        </div>
      )}
    </div>
  );
}
