import { stageOrder, stageLabels } from '../data/mockData';
import { chevronClipPath } from '../utils/chevron';

const statusStyles = {
  done: 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 cursor-pointer',
  current: 'bg-blue-600 text-white cursor-default',
  available: 'bg-slate-100 text-slate-600 hover:bg-slate-200 cursor-pointer',
  locked: 'bg-slate-50 text-slate-300 cursor-not-allowed',
};

export default function StageProgressPipeline({ currentStageId, completion, loading, onNavigate }) {
  const total = stageOrder.length;
  const currentIndex = stageOrder.indexOf(currentStageId);

  return (
    <div className="flex">
      {stageOrder.map((id, index) => {
        const isCurrent = id === currentStageId;
        const isComplete = completion[id] === true;
        const previousComplete = index === 0 || completion[stageOrder[index - 1]] === true;
        const isLocked = !loading && !isCurrent && !previousComplete;

        let status = 'available';
        if (isCurrent) status = 'current';
        else if (isComplete) status = 'done';
        else if (isLocked) status = 'locked';

        return (
          <button
            key={id}
            type="button"
            disabled={isLocked || loading}
            onClick={() => !isLocked && !isCurrent && onNavigate?.(id)}
            className={`flex flex-1 items-center justify-center gap-2 py-2.5 text-sm font-medium transition ${statusStyles[status]}`}
            style={{
              clipPath: chevronClipPath(index, total),
              marginLeft: index === 0 ? 0 : -18,
            }}
          >
            {status === 'done' ? (
              <svg viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M16.7 5.3a1 1 0 010 1.4l-7 7a1 1 0 01-1.4 0l-3-3a1 1 0 111.4-1.4L8.3 11.6l6.3-6.3a1 1 0 011.4 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : null}
            {status === 'locked' ? (
              <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M10 2a4 4 0 00-4 4v2H5a1 1 0 00-1 1v7a2 2 0 002 2h8a2 2 0 002-2v-7a1 1 0 00-1-1h-1V6a4 4 0 00-4-4zm2 6V6a2 2 0 10-4 0v2h4z"
                  clipRule="evenodd"
                />
              </svg>
            ) : null}
            <span>{stageLabels[id]}</span>
            {currentIndex === index && loading ? <span className="text-xs opacity-70">…</span> : null}
          </button>
        );
      })}
    </div>
  );
}
