import { stageOrder, computeStageMeta } from '../data/mockData';
import { chevronClipPath } from '../utils/chevron';

const statusStyles = {
  done: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100',
  active: 'bg-blue-50 text-blue-700 hover:bg-blue-100',
  pending: 'bg-slate-100 text-slate-500 hover:bg-slate-200',
};

export default function StagePipeline({ currentStage, onSelectStage }) {
  const total = stageOrder.length;
  const stageMeta = computeStageMeta(currentStage);
  return (
    <div className="flex">
      {stageOrder.map((id, index) => {
        const stage = stageMeta[id];
        return (
          <button
            key={id}
            type="button"
            onClick={() => onSelectStage?.(id)}
            className={`flex flex-1 items-center justify-center gap-2 py-3 text-sm font-medium transition ${statusStyles[stage.status]}`}
            style={{
              clipPath: chevronClipPath(index, total),
              marginLeft: index === 0 ? 0 : -18,
            }}
          >
            {stage.status === 'done' ? (
              <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M16.7 5.3a1 1 0 010 1.4l-7 7a1 1 0 01-1.4 0l-3-3a1 1 0 111.4-1.4L8.3 11.6l6.3-6.3a1 1 0 011.4 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : null}
            <span>{stage.label}</span>
            {stage.status === 'active' ? (
              <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-blue-700">
                In progress
              </span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
