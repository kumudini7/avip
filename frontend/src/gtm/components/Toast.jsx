export default function Toast({ message }) {
  if (!message) return null;
  return (
    <div className="gtm-toast fixed bottom-6 right-6 z-50 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-lg">
      {message}
    </div>
  );
}
