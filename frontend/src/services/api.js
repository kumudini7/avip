import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 45000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      error.message = 'The request took too long to respond. Please try again.';
    }
    return Promise.reject(error);
  },
);

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('avip_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function registerUser(payload) {
  const { data } = await api.post('/auth/register', payload);
  return data;
}

export async function loginUser(payload) {
  const { data } = await api.post('/auth/login', payload);
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get('/auth/me');
  return data;
}

export async function getDemoDashboard() {
  const { data } = await api.get('/demo/dashboard');
  return data;
}

export async function listProjects() {
  const { data } = await api.get('/projects');
  return data;
}

export async function getProjectOverview() {
  const { data } = await api.get('/projects/overview');
  return data;
}

export async function createProject(payload) {
  const { data } = await api.post('/projects', payload);
  return data;
}

export async function updateProject(projectId, payload) {
  const { data } = await api.patch(`/projects/${projectId}`, payload);
  return data;
}

export async function deleteProject(projectId) {
  await api.delete(`/projects/${projectId}`);
}

export async function listDocuments(projectId) {
  const { data } = await api.get(`/projects/${projectId}/documents`);
  return data;
}

export async function getDocument(projectId, documentId) {
  const { data } = await api.get(`/projects/${projectId}/documents/${documentId}`);
  return data;
}

export async function uploadDocument(projectId, file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post(`/projects/${projectId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function updateDocument(projectId, documentId, payload) {
  const { data } = await api.patch(`/projects/${projectId}/documents/${documentId}`, payload);
  return data;
}

export async function deleteDocument(projectId, documentId) {
  await api.delete(`/projects/${projectId}/documents/${documentId}`);
}

export async function downloadDocument(projectId, documentId) {
  const { data } = await api.get(`/projects/${projectId}/documents/${documentId}/download`, {
    responseType: 'blob',
  });
  return data;
}

export async function runAnalysis(projectId) {
  const { data } = await api.post(`/projects/${projectId}/analysis`);
  return data;
}

export async function enqueueAnalysis(projectId) {
  const { data } = await api.post(`/projects/${projectId}/analysis/jobs`);
  return data;
}

export async function getAnalysis(projectId) {
  const { data } = await api.get(`/projects/${projectId}/analysis`);
  return data;
}

export async function listAnalysisJobs(projectId) {
  const { data } = await api.get(`/projects/${projectId}/analysis/jobs`);
  return data;
}

export async function getAnalysisJob(projectId, jobId) {
  const { data } = await api.get(`/projects/${projectId}/analysis/jobs/${jobId}`);
  return data;
}

export async function generateProposal(projectId) {
  const { data } = await api.post(`/projects/${projectId}/proposal`);
  return data;
}

export async function enqueueProposal(projectId) {
  const { data } = await api.post(`/projects/${projectId}/proposal/jobs`);
  return data;
}

export async function getProposal(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal`);
  return data;
}

export async function getProposalPreview(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/preview`);
  return data;
}

export async function listProposalJobs(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/jobs`);
  return data;
}

export async function getProposalJob(projectId, jobId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/jobs/${jobId}`);
  return data;
}

export async function getProposalHistory(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/history`);
  return data;
}

export async function downloadProposalPdf(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/download/pdf`, {
    responseType: 'blob',
  });
  return data;
}

export async function downloadProposalPptx(projectId) {
  const { data } = await api.get(`/projects/${projectId}/proposal/download/pptx`, {
    responseType: 'blob',
  });
  return data;
}

export async function listEngagements() {
  const { data } = await api.get('/gtm/engagements');
  return data;
}

export async function createEngagement(payload) {
  const { data } = await api.post('/gtm/engagements', payload);
  return data;
}

export async function updateEngagement(engagementId, payload) {
  const { data } = await api.patch(`/gtm/engagements/${engagementId}`, payload);
  return data;
}

export async function deleteEngagement(engagementId) {
  await api.delete(`/gtm/engagements/${engagementId}`);
}

export async function addEngagementKpi(engagementId, payload) {
  const { data } = await api.post(`/gtm/engagements/${engagementId}/kpis`, payload);
  return data;
}

export async function updateEngagementKpi(engagementId, kpiId, payload) {
  const { data } = await api.patch(`/gtm/engagements/${engagementId}/kpis/${kpiId}`, payload);
  return data;
}

export async function deleteEngagementKpi(engagementId, kpiId) {
  await api.delete(`/gtm/engagements/${engagementId}/kpis/${kpiId}`);
}

export async function getStageState(engagementId, stage) {
  const { data } = await api.get(`/gtm/engagements/${engagementId}/stages/${stage}`);
  return data;
}

export async function saveStageState(engagementId, stage, payload) {
  const { data } = await api.put(`/gtm/engagements/${engagementId}/stages/${stage}`, payload);
  return data;
}

export async function generatePlaybook(engagementId) {
  const { data } = await api.post(`/gtm/engagements/${engagementId}/generate-playbook`);
  return data;
}

export async function generatePitchContent(industry, painPoints) {
  const { data } = await api.post('/gtm/pitch/generate', { industry, pain_points: painPoints });
  return data;
}

export async function listActivity(limit = 10) {
  const { data } = await api.get('/gtm/activity', { params: { limit } });
  return data;
}

export async function getDashboardSummary() {
  const { data } = await api.get('/gtm/dashboard-summary');
  return data;
}

export async function getKpiTracker(industry) {
  const { data } = await api.get('/gtm/kpi-tracker', { params: { industry } });
  return data;
}

export async function getUseCases() {
  const { data } = await api.get('/gtm/use-cases');
  return data;
}

export async function listDomains() {
  const { data } = await api.get('/domains');
  return data;
}

export async function getQuestionsForAssessment(domainId) {
  const { data } = await api.get('/questions/for-assessment', { params: { domain_id: domainId } });
  return data;
}

export async function createAssessment(payload) {
  const { data } = await api.post('/assessments', payload);
  return data;
}

export async function listAssessments() {
  const { data } = await api.get('/assessments');
  return data;
}

export async function submitAssessmentResponses(assessmentId, responses) {
  const { data } = await api.post(`/assessments/${assessmentId}/responses`, { responses });
  return data;
}

export async function classifyAssessment(assessmentId) {
  const { data } = await api.post(`/assessments/${assessmentId}/classify`);
  return data;
}

export async function getAssessmentResult(assessmentId) {
  const { data } = await api.get(`/assessments/${assessmentId}/result`);
  return data;
}

export async function saveRoiInputs(assessmentId, payload) {
  const { data } = await api.post(`/assessments/${assessmentId}/roi`, payload);
  return data;
}

export async function downloadAssessmentReport(assessmentId) {
  const { data } = await api.get(`/assessments/${assessmentId}/report.pdf`, { responseType: 'blob' });
  return data;
}

export async function listAdminAssessments() {
  const { data } = await api.get('/admin/assessments');
  return data;
}

export async function getAdminAssessmentResult(assessmentId) {
  const { data } = await api.get(`/admin/assessments/${assessmentId}/result`);
  return data;
}

export default api;
