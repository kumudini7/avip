export default function ToolPill({ label, description, isOpen, onToggle }) {
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => onToggle(label)}
        aria-expanded={isOpen}
        className={`rounded-full px-3 py-1 text-xs font-medium transition ${
          isOpen ? 'bg-blue-700 text-white' : 'bg-blue-50 text-blue-700 hover:bg-blue-100'
        }`}
      >
        {label}
      </button>
      {isOpen ? (
        <div className="absolute left-0 top-full z-20 mt-2 w-64 rounded-lg border-[0.5px] border-slate-200 bg-white p-3 text-xs leading-5 text-slate-600 shadow-lg">
          {description}
        </div>
      ) : null}
    </div>
  );
}
