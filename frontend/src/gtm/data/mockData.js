export const stageOrder = ['discovery', 'design', 'integration', 'measurement', 'scale'];

export const stageLabels = {
  discovery: 'Discovery',
  design: 'Design',
  integration: 'Integration',
  measurement: 'Measurement',
  scale: 'Scale',
};

// Derives each step's done/active/pending status from a real engagement's current stage
// (or null when there's no engagement yet, in which case every step is pending).
export function computeStageMeta(currentStage) {
  const currentIndex = currentStage ? stageOrder.indexOf(currentStage) : -1;
  const meta = {};
  stageOrder.forEach((id, index) => {
    let status = 'pending';
    if (currentIndex >= 0) {
      if (index < currentIndex) status = 'done';
      else if (index === currentIndex) status = 'active';
    }
    meta[id] = { label: stageLabels[id], status };
  });
  return meta;
}

export const industries = ['Manufacturing', 'BFSI', 'Healthcare', 'IT Services'];

const dotColor = {
  update: 'bg-blue-500',
  milestone: 'bg-emerald-500',
  'data-entry': 'bg-amber-500',
};

export function activityDotColor(type) {
  return dotColor[type] || 'bg-slate-400';
}

export function timeAgo(isoString) {
  if (!isoString) return '';
  // Backend timestamps are naive UTC (no offset suffix) - treat them as UTC explicitly.
  const hasTimezone = /Z$|[+-]\d\d:\d\d$/.test(isoString);
  const then = new Date(hasTimezone ? isoString : `${isoString}Z`);
  const diffMs = Date.now() - then.getTime();
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days}d ago`;
  return then.toLocaleDateString();
}

export const pitchBuilderIndustries = ['Manufacturing', 'BFSI', 'Healthcare', 'IT Services', 'Retail'];

export const painPointsByIndustry = {
  Manufacturing: [
    'High RCA resolution time',
    'Manual compliance checks',
    'Fragmented shop-floor data',
    'Slow supplier exception handling',
  ],
  BFSI: [
    'Slow claims turnaround',
    'Manual fraud review',
    'Regulatory reporting overhead',
    'High reconciliation effort',
  ],
  Healthcare: [
    'Slow prior authorization',
    'Manual chart documentation',
    'Compliance audit overhead',
    'Fragmented patient data',
  ],
  'IT Services': [
    'High ticket volume',
    'Manual triage and routing',
    'SLA breaches',
    'Slow change approval cycles',
  ],
  Retail: [
    'Manual inventory reconciliation',
    'Slow demand forecasting',
    'High return-processing effort',
    'Fragmented customer data',
  ],
};

export const kpiLibrary = [
  {
    industry: 'Manufacturing',
    useCase: 'Root cause analysis',
    baseline: '5.1 days',
    target: '2.1 days',
    improvement: '-59%',
    outcome: 'Faster line recovery, reduced downtime cost',
  },
  {
    industry: 'Manufacturing',
    useCase: 'Compliance audit checks',
    baseline: '12% error rate',
    target: '4% error rate',
    improvement: '-67%',
    outcome: 'Lower regulatory exposure',
  },
  {
    industry: 'BFSI',
    useCase: 'Claims adjudication',
    baseline: '4.5 days',
    target: '1.8 days',
    improvement: '-60%',
    outcome: 'Improved policyholder satisfaction',
  },
  {
    industry: 'BFSI',
    useCase: 'Fraud detection',
    baseline: '81% accuracy',
    target: '96% accuracy',
    improvement: '+19%',
    outcome: 'Reduced fraud losses',
  },
  {
    industry: 'Healthcare',
    useCase: 'Prior authorization',
    baseline: '6.0 days',
    target: '3.2 days',
    improvement: '-47%',
    outcome: 'Faster patient care access',
  },
  {
    industry: 'Healthcare',
    useCase: 'Clinical documentation review',
    baseline: '15% error rate',
    target: '6% error rate',
    improvement: '-60%',
    outcome: 'Improved compliance and reimbursement accuracy',
  },
  {
    industry: 'IT Services',
    useCase: 'Ticket triage and routing',
    baseline: '3.1 days',
    target: '1.4 days',
    improvement: '-55%',
    outcome: 'Higher first-contact resolution',
  },
  {
    industry: 'IT Services',
    useCase: 'SLA compliance',
    baseline: '22% breach rate',
    target: '8% breach rate',
    improvement: '-64%',
    outcome: 'Stronger customer trust and retention',
  },
];

export const caseStudies = [
  {
    client: 'Lenovo',
    industry: 'IT Services',
    summary:
      'Deployed an agentic triage layer across the global support desk to auto-classify and resolve L1 tickets.',
    kpis: [
      { label: 'Ticket resolution time', value: '-52%' },
      { label: 'First-contact resolution', value: '+31%' },
    ],
  },
  {
    client: 'Zurich Insurance',
    industry: 'BFSI',
    summary:
      'Built an agentic claims intake and fraud-scoring pipeline that routes only exceptions to human adjusters.',
    kpis: [
      { label: 'Claims cycle time', value: '-58%' },
      { label: 'Fraud detection accuracy', value: '+15%' },
    ],
  },
  {
    client: 'IBM HR',
    industry: 'IT Services',
    summary:
      'Automated employee query resolution and onboarding workflows with an agentic HR assistant.',
    kpis: [
      { label: 'Query resolution time', value: '-46%' },
      { label: 'Onboarding cycle time', value: '-33%' },
    ],
  },
  {
    client: 'Deloitte',
    industry: 'BFSI',
    summary:
      'Implemented an agentic audit evidence-gathering assistant to accelerate compliance reviews.',
    kpis: [
      { label: 'Audit prep time', value: '-41%' },
      { label: 'Audit pass rate', value: '+9%' },
    ],
  },
];
