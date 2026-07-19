export default function Topbar({ crumb, title, actions }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div className="text-sm text-slate-500">
        <span className="text-slate-900">{crumb}</span>
        {title ? <span> / {title}</span> : null}
      </div>
      {actions ? <div className="flex items-center gap-3">{actions}</div> : null}
    </div>
  );
}
