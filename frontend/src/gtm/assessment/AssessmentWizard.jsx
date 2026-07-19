import { useEffect, useState } from 'react';
import AssessmentSidebar from './AssessmentSidebar';
import WelcomeStep from './steps/WelcomeStep';
import DomainContextStep from './steps/DomainContextStep';
import QuestionnaireStep from './steps/QuestionnaireStep';
import ClassificationStep from './steps/ClassificationStep';
import ResultDashboard from './steps/ResultDashboard';
import { listAssessments } from '../../services/api';
import {
  createAssessment,
  getQuestionsForAssessment,
  listDomains,
  submitAssessmentResponses,
} from '../../services/api';

const INITIAL_CONTEXT = {
  prior_automation: '',
  documentation_level: '',
  data_quality: '',
  volume_consistency: '',
};

export default function AssessmentWizard({ user, onSignOut }) {
  const [step, setStep] = useState(1);
  const [domains, setDomains] = useState([]);
  const [domainsLoading, setDomainsLoading] = useState(true);
  const [selectedDomainId, setSelectedDomainId] = useState(null);
  const [businessContext, setBusinessContext] = useState(INITIAL_CONTEXT);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [assessmentId, setAssessmentId] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [assessments, setAssessments] = useState([]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([listDomains(), listAssessments()])
      .then(([domainData, assessmentData]) => {
        if (cancelled) return;
        setDomains(domainData);
        setAssessments(assessmentData);
      })
      .finally(() => {
        if (!cancelled) setDomainsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function refreshAssessments() {
    const data = await listAssessments();
    setAssessments(data);
    return data;
  }

  function handleReset() {
    setStep(1);
    setSelectedDomainId(null);
    setBusinessContext(INITIAL_CONTEXT);
    setQuestions([]);
    setAnswers({});
    setAssessmentId(null);
  }

  function openAssessmentAssessment(item) {
    setAssessmentId(item.id);
    setStep(5);
  }

  async function handleContinueFromContext() {
    setSubmitting(true);
    try {
      const assessment = await createAssessment({ domain_id: selectedDomainId, business_context: businessContext });
      setAssessmentId(assessment.id);
      await refreshAssessments();
      const questionList = await getQuestionsForAssessment(selectedDomainId);
      setQuestions(questionList);
      setStep(3);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmitAnswers() {
    setSubmitting(true);
    try {
      const responses = Object.entries(answers).map(([questionKey, response]) => ({
        question_key: questionKey,
        response,
      }));
      await submitAssessmentResponses(assessmentId, responses);
      setStep(4);
    } finally {
      setSubmitting(false);
    }
  }

  const companyName = user?.company;
  const contactName = user?.full_name || user?.email;

  return (
    <div className="flex h-screen overflow-hidden bg-white text-slate-900">
      <AssessmentSidebar
        currentStep={step}
        companyName={companyName}
        contactName={contactName}
        onReset={handleReset}
        onSignOut={onSignOut}
      />
      <main className="min-w-0 flex-1 overflow-y-auto bg-slate-50 p-8 text-[1.03rem]">
        {step === 1 ? (
          <WelcomeStep
            clientName={contactName}
            assessments={assessments}
            onStart={() => setStep(2)}
            onSelectAssessment={openAssessmentAssessment}
            activeAssessmentId={assessmentId}
          />
        ) : null}

        {step === 2 ? (
          <DomainContextStep
            domains={domains}
            domainsLoading={domainsLoading}
            selectedDomainId={selectedDomainId}
            onSelectDomain={setSelectedDomainId}
            businessContext={businessContext}
            onChangeContext={(key, value) => setBusinessContext((current) => ({ ...current, [key]: value }))}
            onContinue={handleContinueFromContext}
          />
        ) : null}

        {step === 3 && questions.length > 0 ? (
          <QuestionnaireStep
            questions={questions}
            answers={answers}
            onChangeAnswer={(questionId, value) => setAnswers((current) => ({ ...current, [questionId]: value }))}
            onSubmit={handleSubmitAnswers}
          />
        ) : null}

        {step === 4 ? (
          <ClassificationStep
            assessmentId={assessmentId}
            onCompleted={refreshAssessments}
            onContinue={() => setStep(5)}
          />
        ) : null}

        {step === 5 ? (
          <ResultDashboard
            assessmentId={assessmentId}
            assessments={assessments}
            onSelectAssessment={openAssessmentAssessment}
            activeAssessmentId={assessmentId}
          />
        ) : null}

        {submitting ? <div className="mt-4 text-center text-xs text-slate-400">Working...</div> : null}
      </main>
    </div>
  );
}
