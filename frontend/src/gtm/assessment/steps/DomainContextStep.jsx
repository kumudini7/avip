const DOMAIN_ICON_PATHS = {
  Manufacturing: 'M4 21V8l5-3 5 3v3l5-3v13H4Zm2-2h3v-3H6v3Zm5 0h3v-3h-3v3Zm5 0h2v-6l-2 1.2V19ZM6 14h3v-3H6v3Zm5 0h3v-3h-3v3Z',
  BFSI: 'M12 2 3 7v2h18V7l-9-5Zm-7 9v7H4v2h16v-2h-1v-7h-2v7h-3v-7h-2v7H9v-7H7v7H6v-7H5Z',
  Healthcare: 'M11 2h2v7h7v2h-7v7h-2v-7H4V9h7V2Z',
  'IT Services': 'm8 16-4-4 4-4 1.4 1.4L6.8 12l2.6 2.6L8 16Zm8 0-1.4-1.4L17.2 12l-2.6-2.6L16 8l4 4-4 4Z',
  'Retail & Customer Service':
    'M6 2h12l1 4h2v2h-2.2l-1.1 10.1A2 2 0 0 1 15.7 20H8.3a2 2 0 0 1-2-1.9L5.2 8H3V6h2l1-4Zm1.9 4h8.2l-.5-2H8.4l-.5 2ZM7.2 8l1 10h7.6l1-10H7.2Z',
};

const CONTEXT_QUESTIONS = [
  {
    key: 'prior_automation',
    question: 'Has your organisation tried automation before?',
    options: ['Never', 'Tried but failed', 'Currently using'],
  },
  {
    key: 'documentation_level',
    question: 'How well is this process documented?',
    options: ['Ad-hoc', 'Partially', 'Fully documented'],
  },
  {
    key: 'data_quality',
    question: 'What is the data quality in this process?',
    options: ['Poor', 'Mixed', 'Clean and structured'],
  },
  {
    key: 'volume_consistency',
    question: 'Is transaction volume consistent?',
    options: ['Varies wildly', 'Somewhat', 'Very consistent'],
  },
];

function DomainIcon({ name }) {
  const path = DOMAIN_ICON_PATHS[name];
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-6 w-6">
      {path ? <path d={path} /> : <circle cx="12" cy="12" r="8" />}
    </svg>
  );
}

function ChipGroup({ options, value, onChange }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isActive = value === option;
        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            className={`rounded-full px-3 py-1 text-[11px] font-medium transition ${
              isActive ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {option}
          </button>
        );
      })}
    </div>
  );
}

export default function DomainContextStep({
  domains,
  domainsLoading,
  selectedDomainId,
  onSelectDomain,
  businessContext,
  onChangeContext,
  onContinue,
}) {
  const allAnswered = CONTEXT_QUESTIONS.every((q) => Boolean(businessContext[q.key]));
  const canContinue = Boolean(selectedDomainId) && allAnswered;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-base font-medium text-slate-900">Select your domain</h2>
        <p className="mt-1 text-xs text-slate-500">Choose the area of the business this process belongs to.</p>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {domainsLoading ? (
            <div className="col-span-full text-xs text-slate-500">Loading domains...</div>
          ) : (
            domains.map((domain) => {
              const isActive = selectedDomainId === domain.id;
              return (
                <button
                  key={domain.id}
                  type="button"
                  onClick={() => onSelectDomain(domain.id)}
                  className={`flex items-start gap-3 rounded-xl border-[0.5px] bg-white p-4 text-left transition ${
                    isActive ? 'border-blue-700 ring-1 ring-blue-700' : 'border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${isActive ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-500'}`}>
                    <DomainIcon name={domain.name} />
                  </span>
                  <span>
                    <span className="block text-xs font-semibold text-slate-900">{domain.name}</span>
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {selectedDomainId ? (
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <h3 className="text-xs font-semibold text-slate-900">A bit more context</h3>
          <div className="mt-4 space-y-5">
            {CONTEXT_QUESTIONS.map((q) => (
              <div key={q.key}>
                <div className="mb-2 text-xs text-slate-700">{q.question}</div>
                <ChipGroup
                  options={q.options}
                  value={businessContext[q.key]}
                  onChange={(value) => onChangeContext(q.key, value)}
                />
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="flex justify-end">
        <button
          type="button"
          disabled={!canContinue}
          onClick={onContinue}
          className="rounded-lg bg-blue-700 px-4 py-2 text-xs font-medium text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Continue
        </button>
      </div>
    </div>
  );
}

export { CONTEXT_QUESTIONS };
