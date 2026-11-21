import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Investigation from './pages/Investigation';
import KnowledgeBase from './pages/KnowledgeBase';
import History from './pages/History';
import SystemStatus from './pages/SystemStatus';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);

  // Poll system health
  useEffect(() => {
    let isMounted = true;
    async function checkHealth() {
      try {
        const data = await api.healthCheck();
        if (isMounted) {
          setSystemHealth({ healthy: true, ...data });
        }
      } catch (err) {
        if (isMounted) {
          setSystemHealth({ healthy: false, error: err.message });
        }
      }
    }

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Probe every 30s
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // When an investigation is clicked from History or Dashboard
  const handleSelectInvestigation = async (id) => {
    try {
      const fullReport = await api.getInvestigationById(id);
      setSelectedReport(fullReport);
      setActiveTab('investigation');
    } catch (err) {
      console.error('Failed to load investigation details:', err);
    }
  };

  const pageHeaders = {
    dashboard: {
      title: 'Incident Telemetry & Overview',
      subtitle: 'Real-time observability and AI-powered root cause analytics',
    },
    investigation: {
      title: 'Autonomous Incident Investigation',
      subtitle: 'LangGraph multi-node agent RCA reasoning pipeline',
    },
    knowledge: {
      title: 'Runbook & Architecture Knowledge Base',
      subtitle: 'ChromaDB vector collection with Sentence Transformers embeddings',
    },
    history: {
      title: 'Investigation Historical Audit Trail',
      subtitle: 'Past incident investigations persisted in SQLite database',
    },
    status: {
      title: 'System Health & Engine Diagnostics',
      subtitle: 'Component runtime status, dependencies, and API endpoints',
    },
  };

  const currentHeader = pageHeaders[activeTab] || pageHeaders.dashboard;

  return (
    <div className="flex h-screen bg-[#070A11] bg-mesh overflow-hidden text-slate-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          if (tab !== 'investigation') setSelectedReport(null);
          setActiveTab(tab);
        }}
        systemStatus={systemHealth}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Subtle Ambient Top Glow */}
        <div className="absolute top-0 left-1/4 w-96 h-32 bg-indigo-500/10 blur-[100px] pointer-events-none -z-0" />
        <div className="absolute top-0 right-1/4 w-96 h-32 bg-violet-500/10 blur-[100px] pointer-events-none -z-0" />

        {/* Top Header */}
        <Header
          title={currentHeader.title}
          subtitle={currentHeader.subtitle}
          health={systemHealth}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 z-10">
          <div className="max-w-7xl mx-auto space-y-6">
            {activeTab === 'dashboard' && (
              <Dashboard
                onNavigate={setActiveTab}
                onSelectInvestigation={handleSelectInvestigation}
              />
            )}

            {activeTab === 'investigation' && (
              <Investigation
                initialReport={selectedReport}
                onClearInitialReport={() => setSelectedReport(null)}
              />
            )}

            {activeTab === 'knowledge' && <KnowledgeBase />}

            {activeTab === 'history' && (
              <History onSelectInvestigation={handleSelectInvestigation} />
            )}

            {activeTab === 'status' && <SystemStatus systemHealth={systemHealth} />}
          </div>
        </main>
      </div>
    </div>
  );
}
