import { useEffect, useRef, useState } from 'react';

export default function EngagementSwitcher({ engagements, selectedEngagementId, onSelect }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selected = engagements.find((item) => item.id === selectedEngagementId) || null;

  if (engagements.length === 0) return null;

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex items-center gap-2 rounded-lg border-[0.5px] border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
      >
        <span className="max-w-[220px] truncate">{selected ? selected.client_name : 'Select engagement'}</span>
        <svg
          viewBox="0 0 20 20"
          className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.3 7.3a1 1 0 011.4 0L10 10.6l3.3-3.3a1 1 0 111.4 1.4l-4 4a1 1 0 01-1.4 0l-4-4a1 1 0 010-1.4z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {open ? (
        <div className="absolute right-0 top-full z-20 mt-2 w-64 rounded-lg border-[0.5px] border-slate-200 bg-white py-1.5 shadow-lg">
          {engagements.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                onSelect(item.id);
                setOpen(false);
              }}
              className={`flex w-full flex-col items-start px-3 py-2 text-left text-sm transition hover:bg-slate-50 ${
                item.id === selectedEngagementId ? 'bg-blue-50' : ''
              }`}
            >
              <span className="font-medium text-slate-900">{item.client_name}</span>
              <span className="text-xs text-slate-500">{item.industry}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
