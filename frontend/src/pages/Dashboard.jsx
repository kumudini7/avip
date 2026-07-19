import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { benchmarks, stats } from '../data/mock';
import SectionCard from '../components/SectionCard';
import StatCard from '../components/StatCard';

const coverageData = [
  { name: 'Automation', value: 74 },
  { name: 'AI', value: 61 },
  { name: 'Manual', value: 26 },
];

const palette = ['#1e3a8a', '#0f172a', '#1d4ed8'];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((item) => (
          <StatCard key={item.label} {...item} />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <SectionCard
          id="dashboard"
          title="Executive Dashboard"
          description="A concise view of automation coverage, AI confidence, business value, and delivery risk."
        >
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={coverageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
                <XAxis dataKey="name" stroke="#cbd5e1" />
                <YAxis stroke="#cbd5e1" />
                <Tooltip />
                <Bar dataKey="value" radius={[12, 12, 0, 0]}>
                  {coverageData.map((entry, index) => (
                    <Cell key={entry.name} fill={palette[index]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>

        <SectionCard
          title="Business Benchmarking"
          description="Compare proposals against historical patterns to reduce subjective estimates."
        >
          <div className="space-y-4">
            {benchmarks.map((item) => (
              <div key={item.label} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-slate-950">{item.label}</div>
                  <div className="text-sm text-slate-600">{item.payback}</div>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-sm text-slate-600">
                  <div>Automation: {item.automation}%</div>
                  <div>ROI: {item.roi}%</div>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Decision Intelligence Score"
          description="A simple placeholder for the platform's readiness index and enterprise-fit evaluation."
        >
          <div className="space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-blue-900">Automation Readiness</div>
              <div className="mt-2 text-4xl font-semibold text-slate-950">89/100</div>
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-600">
              AI Readiness 84/100
              <br />
              Business Impact 95/100
              <br />
              Overall: Enterprise Ready
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  );
}
