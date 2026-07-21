function Card({ title, children }) {
  return (
    <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      <div className="mt-4">{children}</div>
    </div>
  );
}

function Bar({ label, pct, color = 'bg-blue-700' }) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span>{label}</span>
        <span className="font-medium text-slate-900">{pct}%</span>
      </div>
      <div className="mt-1 h-2 rounded-full bg-slate-100">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.min(100, Math.max(0, pct))}%` }} />
      </div>
    </div>
  );
}

function BusinessObjectiveBlock({ data }) {
  return (
    <Card title="1. Business Objective — Why are we automating?">
      <div className="grid gap-2 sm:grid-cols-2">
        {data.options.map((option) => (
          <div
            key={option.key}
            className={`flex items-center gap-2 rounded-lg border-[0.5px] px-3 py-2 text-sm ${
              option.selected ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-slate-200 text-slate-400'
            }`}
          >
            <span>{option.selected ? '✔️' : '—'}</span>
            {option.label}
          </div>
        ))}
      </div>
    </Card>
  );
}

function ProcessDnaBlock({ data }) {
  return (
    <Card title="2. Process DNA (Unique)">
      <div className="space-y-3">
        {data.characteristics.map((item) => (
          <Bar key={item.name} label={item.name} pct={item.pct} />
        ))}
      </div>
      <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
        <span className="font-semibold text-slate-900">Interpretation: </span>
        {data.interpretation}
      </div>
    </Card>
  );
}

function ScoreTable({ rows, outputLabel, outputValue }) {
  return (
    <>
      <div className="space-y-3">
        {rows.map((row) => (
          <Bar key={row.name} label={row.name} pct={row.score} color="bg-purple-700" />
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between rounded-lg bg-slate-50 p-3 text-sm">
        <span className="font-semibold text-slate-900">{outputLabel}</span>
        <span className="text-lg font-semibold text-slate-900">{outputValue}</span>
      </div>
    </>
  );
}

function DecisionComplexityBlock({ data }) {
  return (
    <Card title="3. Decision Complexity">
      <ScoreTable rows={data.parameters} outputLabel="Complexity Score" outputValue={data.complexity_score} />
    </Card>
  );
}

function AiReadinessBlock({ data }) {
  return (
    <Card title="4. AI Readiness">
      <ScoreTable rows={data.areas} outputLabel="AI Readiness %" outputValue={`${data.ai_readiness_pct}%`} />
    </Card>
  );
}

const LANE_ORDER = [
  { key: 'manual', label: 'Manual' },
  { key: 'rpa', label: 'RPA' },
  { key: 'ai', label: 'AI' },
  { key: 'agentic', label: 'Agentic' },
];

function AutomationHeatmapBlock({ data }) {
  return (
    <Card title="5. Automation Opportunity Heatmap">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="pb-2">Process Step</th>
              {LANE_ORDER.map((lane) => (
                <th key={lane.key} className="pb-2 text-center">
                  {lane.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row) => (
              <tr key={row.process_step} className="border-t border-slate-100">
                <td className="py-2 font-medium text-slate-900">{row.process_step}</td>
                {LANE_ORDER.map((lane) => (
                  <td key={lane.key} className="py-2 text-center">
                    {row.lanes[lane.key] ? '✔️' : ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-slate-500">This immediately identifies automation opportunities.</p>
    </Card>
  );
}

function ValuePropositionBlock({ items }) {
  return (
    <Card title="6. Value Proposition">
      {items.length ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[360px] text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
                <th className="pb-2">Opportunity</th>
                <th className="pb-2">Business Outcome</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, index) => (
                <tr key={index} className="border-t border-slate-100">
                  <td className="py-2 text-slate-900">{item.opportunity}</td>
                  <td className="py-2 text-slate-600">{item.business_outcome}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-slate-400">Select a business objective in the questionnaire to populate this.</p>
      )}
    </Card>
  );
}

function BusinessCaseBlock({ data }) {
  return (
    <Card title="7. Business Case">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="pb-2">KPI</th>
              <th className="pb-2 text-right">Before</th>
              <th className="pb-2 text-right">After</th>
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row) => (
              <tr key={row.kpi} className="border-t border-slate-100">
                <td className="py-2 text-slate-900">{row.kpi}</td>
                <td className="py-2 text-right text-slate-600">
                  {typeof row.before === 'number' ? row.before.toLocaleString() : row.before}
                  {row.unit === '%' ? '%' : ''}
                </td>
                <td className="py-2 text-right font-medium text-slate-900">
                  {typeof row.after === 'number' ? row.after.toLocaleString() : row.after}
                  {row.unit === '%' ? '%' : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex items-center justify-between rounded-lg bg-slate-50 p-3 text-sm">
        <span className="font-semibold text-slate-900">Business Value Score</span>
        <span className="text-lg font-semibold text-slate-900">{data.business_value_score}</span>
      </div>
    </Card>
  );
}

function FinalRecommendationBlock({ data }) {
  return (
    <Card title="8. Final Recommendation — Executive Scorecard">
      <div className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
        <span className="font-semibold text-slate-900">Recommended strategy: </span>
        {data.strategy}
      </div>
      <div className="mt-4 space-y-3">
        {data.dimensions.map((dimension) => (
          <div key={dimension.name} className="flex items-center gap-3">
            <div className="w-40 shrink-0 text-xs text-slate-600">{dimension.name}</div>
            <div className="h-2 flex-1 rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-emerald-600"
                style={{ width: `${Math.min(100, Math.max(0, dimension.score))}%` }}
              />
            </div>
            <div className="w-16 shrink-0 text-right text-xs font-medium text-slate-900">{dimension.score}</div>
            <div className="w-14 shrink-0 text-right text-[11px] text-slate-400">{dimension.weight}%</div>
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center justify-between rounded-lg bg-emerald-50 p-3 text-sm">
        <span className="font-semibold text-emerald-900">Weighted Final Score</span>
        <span className="text-lg font-semibold text-emerald-900">{data.weighted_total} / 100</span>
      </div>
    </Card>
  );
}

export default function ScorecardTab({ result }) {
  const metrics = result?.classification?.dashboard_metrics;

  if (!metrics) {
    return (
      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5 text-sm text-slate-500">
        Classify this assessment to generate the executive scorecard.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <BusinessObjectiveBlock data={metrics.business_objective} />
      <div className="grid gap-6 lg:grid-cols-2">
        <ProcessDnaBlock data={metrics.process_dna} />
        <DecisionComplexityBlock data={metrics.decision_complexity} />
      </div>
      <AiReadinessBlock data={metrics.ai_readiness} />
      <AutomationHeatmapBlock data={metrics.automation_heatmap} />
      <ValuePropositionBlock items={metrics.value_proposition} />
      <BusinessCaseBlock data={metrics.business_case} />
      <FinalRecommendationBlock data={metrics.final_recommendation} />
    </div>
  );
}
