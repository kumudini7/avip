export default function StatCard({ label, value, hint }) {
  return (
    <div className="glass-panel rounded-3xl p-5 shadow-soft">
      <div className="text-sm text-slate-600">{label}</div>
      <div className="mt-3 text-3xl font-semibold text-slate-950">{value}</div>
      <div className="mt-2 text-sm text-slate-500">{hint}</div>
    </div>
  );
}
