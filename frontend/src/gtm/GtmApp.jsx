import { useCallback, useEffect, useState } from 'react';
import { Route, Routes } from 'react-router-dom';
import GtmSidebar from './components/GtmSidebar';
import Dashboard from './pages/Dashboard';
import Engagements from './pages/Engagements';
import PitchBuilder from './pages/PitchBuilder';
import Discovery from './pages/stages/Discovery';
import Design from './pages/stages/Design';
import Integration from './pages/stages/Integration';
import Measurement from './pages/stages/Measurement';
import Scale from './pages/stages/Scale';
import KpiLibrary from './pages/KpiLibrary';
import CaseStudies from './pages/CaseStudies';
import Settings from './pages/Settings';
import ClientAssessments from './pages/admin/ClientAssessments';
import { listEngagements } from '../services/api';

export default function GtmApp({ user, onSignOut }) {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [engagements, setEngagements] = useState([]);
  const [engagementsLoaded, setEngagementsLoaded] = useState(false);
  const [selectedEngagementId, setSelectedEngagementId] = useState(null);

  const userName = user?.full_name || user?.email || 'Consultant';
  const userRole = user?.role || 'Consultant';

  const refreshEngagements = useCallback(async () => {
    const data = await listEngagements();
    setEngagements(data);
    setEngagementsLoaded(true);
    return data;
  }, []);

  useEffect(() => {
    refreshEngagements().catch(() => setEngagementsLoaded(true));
  }, [refreshEngagements]);

  useEffect(() => {
    if (selectedEngagementId === null && engagements.length > 0) {
      setSelectedEngagementId(engagements[0].id);
    }
  }, [engagements, selectedEngagementId]);

  const engagementCount = engagements.filter((item) => !item.closed_at).length;

  const stageProps = {
    engagements,
    engagementsLoaded,
    selectedEngagementId,
    onSelectEngagement: setSelectedEngagementId,
    onEngagementChanged: refreshEngagements,
    onNavigate: setActiveNav,
  };

  function renderPage() {
    switch (activeNav) {
      case 'dashboard':
        return <Dashboard onNavigate={setActiveNav} engagements={engagements} />;
      case 'engagements':
        return <Engagements engagements={engagements} engagementsLoaded={engagementsLoaded} onEngagementChanged={refreshEngagements} />;
      case 'pitch-builder':
        return <PitchBuilder onEngagementCreated={refreshEngagements} onNavigate={setActiveNav} />;
      case 'discovery':
        return <Discovery {...stageProps} />;
      case 'design':
        return <Design {...stageProps} />;
      case 'integration':
        return <Integration {...stageProps} />;
      case 'measurement':
        return <Measurement {...stageProps} />;
      case 'scale':
        return <Scale {...stageProps} />;
      case 'kpi-library':
        return <KpiLibrary engagements={engagements} onEngagementChanged={refreshEngagements} />;
      case 'case-studies':
        return <CaseStudies />;
      case 'settings':
        return <Settings userName={userName} userEmail={user?.email} userRole={userRole} onSignOut={onSignOut} />;
      case 'client-assessments':
        return <ClientAssessments onNavigate={setActiveNav} />;
      default:
        return <Dashboard onNavigate={setActiveNav} engagements={engagements} />;
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-white text-slate-900">
      <GtmSidebar
        activeNav={activeNav}
        onNavigate={setActiveNav}
        userName={userName}
        userRole={userRole}
        engagementCount={engagementCount}
      />
      <main className="min-w-0 flex-1 overflow-y-auto bg-white p-8 text-[1.03rem]">
        <Routes>
          <Route path="client-assessments" element={<ClientAssessments onNavigate={setActiveNav} />} />
          <Route path="*" element={renderPage()} />
        </Routes>
      </main>
    </div>
  );
}
