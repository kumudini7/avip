export default function SectionCard({ title, description, children, id }) {
  return (
    <section id={id} className="glass-panel rounded-3xl p-6 shadow-soft">
      <div className="mb-5">
        <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
      </div>
      {children}
    </section>
  );
}
