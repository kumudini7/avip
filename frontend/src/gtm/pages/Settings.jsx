import Topbar from '../components/Topbar';

export default function Settings({ userName, userEmail, userRole, onSignOut }) {
  return (
    <div className="space-y-6">
      <Topbar crumb="Settings" title="Account and workspace preferences" />

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <div className="text-sm font-semibold text-slate-900">Profile</div>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between border-b-[0.5px] border-slate-100 pb-3">
              <span className="text-slate-500">Name</span>
              <span className="font-medium text-slate-900">{userName}</span>
            </div>
            <div className="flex items-center justify-between border-b-[0.5px] border-slate-100 pb-3">
              <span className="text-slate-500">Email</span>
              <span className="font-medium text-slate-900">{userEmail}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Role</span>
              <span className="font-medium text-slate-900">{userRole}</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
          <div className="text-sm font-semibold text-slate-900">Workspace</div>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between border-b-[0.5px] border-slate-100 pb-3">
              <span className="text-slate-500">Practice</span>
              <span className="font-medium text-slate-900">Agentic AI Practice</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Organization</span>
              <span className="font-medium text-slate-900">Jade Global</span>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border-[0.5px] border-slate-200 bg-white p-5">
        <div className="text-sm font-semibold text-slate-900">Session</div>
        <p className="mt-1 text-sm text-slate-500">Sign out of the GTM Playbook workspace on this device.</p>
        <button
          type="button"
          onClick={onSignOut}
          className="mt-4 rounded-lg border-[0.5px] border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
