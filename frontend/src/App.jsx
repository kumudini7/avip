import { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { getCurrentUser, loginUser, registerUser } from './services/api';
import GtmApp from './gtm/GtmApp';
import AssessmentWizard from './gtm/assessment/AssessmentWizard';

const defaultAuthForm = {
  email: '',
  password: '',
  full_name: '',
  company: '',
};

const demoAuthForm = {
  email: 'demo@avip.test',
  password: 'Demo@12345',
};

export default function App() {
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [authForm, setAuthForm] = useState(defaultAuthForm);
  const [loading, setLoading] = useState({ auth: false });
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('avip_token');
    if (!token) {
      return;
    }

    const bootstrap = async () => {
      try {
        const current = await getCurrentUser();
        setUser(current);
      } catch (err) {
        localStorage.removeItem('avip_token');
      }
    };

    bootstrap();
  }, []);

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setError('');
    setNotice('');
    setLoading((state) => ({ ...state, auth: true }));

    try {
      const payload = {
        email: authForm.email,
        password: authForm.password,
      };
      if (authMode === 'register') {
        payload.full_name = authForm.full_name;
        payload.company = authForm.company;
      }

      const response = authMode === 'register' ? await registerUser(payload) : await loginUser(payload);
      localStorage.setItem('avip_token', response.access_token);
      setUser(response.user);
      setNotice(`${authMode === 'register' ? 'Account created' : 'Logged in'} successfully.`);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Authentication failed.');
    } finally {
      setLoading((state) => ({ ...state, auth: false }));
    }
  }

  function handleSignOut() {
    localStorage.removeItem('avip_token');
    setUser(null);
    setNotice('Signed out.');
  }

  if (!user) {
    const loginScreen = (
      <div className="min-h-screen bg-slate-50 text-slate-900 lg:flex lg:overflow-hidden">
        <section className="flex flex-col justify-between bg-black px-8 py-10 text-white lg:sticky lg:top-0 lg:h-screen lg:w-[48%] lg:overflow-hidden">
          <div>
            <div className="text-[10px] uppercase tracking-[0.3em] text-blue-300/90">
              Automation Workspace
            </div>
            <h2 className="mt-4 max-w-2xl text-3xl font-semibold leading-tight text-white">
              Assess automation opportunities and manage client workflows.
            </h2>
            <p className="mt-4 max-w-2xl text-xs leading-6 text-blue-100/80">
              AVIP combines client assessment, KPI tracking, and engagement management in one workspace so teams
              can review fit, capture outcomes, and keep work moving.
            </p>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-[10px] uppercase tracking-[0.28em] text-blue-200">Why this matters</div>
              <div className="mt-3 text-base font-semibold text-white">
                One place for assessments and tracking.
              </div>
              <p className="mt-2 text-xs leading-5 text-blue-100/75">
                Keep assessments, automation fit, KPI benchmarks, and activity history together in a single flow.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="text-[10px] uppercase tracking-[0.28em] text-blue-200">What you get</div>
              <div className="mt-3 text-base font-semibold text-white">
                Assessments, dashboards, and insights.
              </div>
              <p className="mt-2 text-xs leading-5 text-blue-100/75">
                Create a client or consultant account, then sign in to continue your workflow.
              </p>
            </div>
          </div>
        </section>

        <section className="bg-slate-50 px-8 py-10 lg:h-screen lg:flex-1 lg:overflow-y-auto">
          <div className="mx-auto max-w-xl">
            <div className="mb-8">
              <div className="text-xs uppercase tracking-[0.35em] text-blue-900">Access AVIP</div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Create a client or consultant account to get started.
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Sign in to continue a client assessment or manage the GTM workspace, depending on your role.
              </p>
            </div>

            <form className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm" onSubmit={handleAuthSubmit}>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setAuthMode('login')}
                  className={`rounded-full px-4 py-2 text-sm font-medium ${
                    authMode === 'login'
                    ? 'bg-blue-900 text-white'
                      : 'bg-slate-100 text-slate-700'
                  }`}
                >
                  Login
                </button>
                <button
                  type="button"
                  onClick={() => setAuthMode('register')}
                  className={`rounded-full px-4 py-2 text-sm font-medium ${
                    authMode === 'register'
                    ? 'bg-blue-900 text-white'
                      : 'bg-slate-100 text-slate-700'
                  }`}
                >
                  Register
                </button>
              </div>

              {authMode === 'login' ? (
                <div className="flex flex-wrap items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-600">
                  <span>
                    New here? Register with your work email, or use the seeded demo account for a quick walkthrough.
                  </span>
                  <button
                    type="button"
                    onClick={() => setAuthForm({ ...defaultAuthForm, ...demoAuthForm })}
                    className="rounded-full bg-slate-900 px-3 py-1.5 font-medium text-white transition hover:bg-slate-800"
                  >
                    Fill demo account
                  </button>
                </div>
              ) : null}

              {authMode === 'register' ? (
                <>
                  <label className="block">
                    <span className="mb-2 block text-sm text-slate-600">Full name</span>
                    <input
                      value={authForm.full_name}
                      onChange={(event) => setAuthForm({ ...authForm, full_name: event.target.value })}
                      className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 outline-none transition focus:border-blue-900"
                      placeholder="Your name"
                    />
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm text-slate-600">Company</span>
                    <input
                      value={authForm.company}
                      onChange={(event) => setAuthForm({ ...authForm, company: event.target.value })}
                      className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 outline-none transition focus:border-blue-900"
                      placeholder="Company name"
                    />
                  </label>
                </>
              ) : null}

              <label className="block">
                <span className="mb-2 block text-sm text-slate-600">Email</span>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(event) => setAuthForm({ ...authForm, email: event.target.value })}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 outline-none transition focus:border-blue-900"
                  placeholder="name@company.com"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-sm text-slate-600">Password</span>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 outline-none transition focus:border-blue-900"
                  placeholder="At least 8 characters"
                />
              </label>

              <button
                type="submit"
                disabled={loading.auth}
                className="w-full rounded-2xl bg-blue-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:opacity-60"
              >
                {loading.auth ? 'Working...' : authMode === 'register' ? 'Create account' : 'Sign in'}
              </button>

              {error ? <div className="text-sm text-rose-600">{error}</div> : null}
              {notice ? <div className="text-sm text-emerald-700">{notice}</div> : null}
            </form>
          </div>
        </section>
      </div>
    );

    return (
      <Routes>
        <Route path="/login" element={loginScreen} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  const landingPath = user.role === 'client' ? '/assessment' : '/dashboard';

  return (
    <Routes>
      <Route
        path="/dashboard/*"
        element={user.role !== 'client' ? <GtmApp user={user} onSignOut={handleSignOut} /> : <Navigate to={landingPath} replace />}
      />
      <Route
        path="/assessment/*"
        element={user.role === 'client' ? <AssessmentWizard user={user} onSignOut={handleSignOut} /> : <Navigate to={landingPath} replace />}
      />
      <Route path="/login" element={<Navigate to={landingPath} replace />} />
      <Route path="/" element={<Navigate to={landingPath} replace />} />
      <Route path="*" element={<Navigate to={landingPath} replace />} />
    </Routes>
  );
}
