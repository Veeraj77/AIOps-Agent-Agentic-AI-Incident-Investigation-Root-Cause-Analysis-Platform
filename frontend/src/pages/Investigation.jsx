import React, { useState } from 'react';
import LogUploader from '../components/LogUploader';
import IncidentSummary from '../components/IncidentSummary';
import InvestigationReport from '../components/InvestigationReport';
import LoadingState from '../components/LoadingState';
import ErrorMessage from '../components/ErrorMessage';
import { api } from '../services/api';

export default function Investigation({ initialReport, onClearInitialReport }) {
  const [logs, setLogs] = useState('');
  const [quickAnalysis, setQuickAnalysis] = useState(null);
  const [report, setReport] = useState(initialReport || null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(1);
  const [error, setError] = useState(null);

  // If parent passed in an initial report (from History click)
  React.useEffect(() => {
    if (initialReport) {
      setReport(initialReport);
      setQuickAnalysis(null);
      setError(null);
    }
  }, [initialReport]);

  // Run Quick Rule-Based Pattern Scan (POST /api/incidents/analyze)
  const handleQuickAnalyze = async (rawLogs) => {
    setIsLoading(true);
    setError(null);
    setLoadingStep(2);

    try {
      const data = await api.analyzeIncident(rawLogs);
      setQuickAnalysis(data);
      setReport(null);
    } catch (err) {
      setError(err.message || 'Pattern analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Run Full LangGraph AI Agent Investigation (POST /api/investigations/run)
  const handleRunInvestigation = async (rawLogs, question) => {
    setIsLoading(true);
    setError(null);
    setReport(null);
    setQuickAnalysis(null);

    // Simulate progressive step transitions for visual feedback while waiting for AI
    setLoadingStep(1);
    const t1 = setTimeout(() => setLoadingStep(2), 2000);
    const t2 = setTimeout(() => setLoadingStep(3), 5000);
    const t3 = setTimeout(() => setLoadingStep(4), 9000);

    try {
      const data = await api.runInvestigation({
        logs: rawLogs,
        question: question || 'Why is the application failing?',
      });
      setReport(data);
    } catch (err) {
      setError(err.message || 'AI Investigation failed. Check if GROQ_API_KEY is configured in backend/.env');
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      setIsLoading(false);
    }
  };

  const handleBackToInput = () => {
    setReport(null);
    setQuickAnalysis(null);
    if (onClearInitialReport) onClearInitialReport();
  };

  return (
    <div className="space-y-6">
      {/* If full report is available, show the report view */}
      {report ? (
        <InvestigationReport report={report} onBack={handleBackToInput} />
      ) : (
        <>
          {/* Telemetry Input Panel */}
          <LogUploader
            logs={logs}
            onLogsChange={setLogs}
            onAnalyze={handleQuickAnalyze}
            onRunInvestigation={handleRunInvestigation}
            isSubmitting={isLoading}
          />

          {/* Error Message */}
          {error && (
            <ErrorMessage
              title="Investigation Engine Notice"
              message={error}
              onRetry={() => handleRunInvestigation(logs)}
            />
          )}

          {/* Loading Animation with Multistep Progress */}
          {isLoading && (
            <LoadingState
              message="Investigating incident telemetry via LangGraph agent..."
              currentStep={loadingStep}
            />
          )}

          {/* Quick Analysis Results */}
          {quickAnalysis && !isLoading && (
            <IncidentSummary analysis={quickAnalysis} />
          )}
        </>
      )}
    </div>
  );
}
