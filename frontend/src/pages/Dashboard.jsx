import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import SeverityBadge from '../components/SeverityBadge';
import { api } from '../services/api';
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  BookOpen,
  History,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Zap,
  Layers,
  ChevronRight,
  Database,
  KeyRound,
  MemoryStick,
  RefreshCw,
} from 'lucide-react';

export default function Dashboard({ onNavigate, onSelectInvestigation }) {
  const [stats, setStats] = useState({
    totalInvestigations: 0,
    criticalCount: 0,
    highCount: 0,
    totalDocuments: 0,
  });
  const [recentInvestigations, setRecentInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [investigationsData, docStats] = await Promise.allSettled([
        api.getInvestigations(10),
        api.getDocumentStats(),
      ]);

      let invList = [];
      if (investigationsData.status === 'fulfilled' && Array.isArray(investigationsData.value)) {
        invList = investigationsData.value;
        setRecentInvestigations(invList);
      }

      let docCount = 0;
      if (docStats.status === 'fulfilled' && docStats.value) {
        docCount = docStats.value.document_count || 0;
      }

      const critical = invList.filter((i) => i.severity === 'CRITICAL').length;
      const high = invList.filter((i) => i.severity === 'HIGH').length;

      setStats({
        totalInvestigations: invList.length,
        criticalCount: critical,
        highCount: high,
        totalDocuments: docCount,
      });
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="space-y-7">
      {/* Hero Welcome Banner */}
      <div className="glass-panel-elevated rounded-3xl p-7 md:p-8 border border-indigo-500/25 shadow-2xl relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Ambient Gradient Glows */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-indigo-500/20 via-purple-500/10 to-transparent rounded-full blur-3xl pointer-events-none -z-0" />
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-80" />

        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[10px] font-mono font-bold uppercase tracking-wider">
            <Zap className="w-3 h-3 text-indigo-400" />
            <span>Autonomous Incident Intelligence</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            Enterprise DevOps Telemetry & RCA Platform
          </h2>
          <p className="text-xs md:text-sm text-slate-300 font-medium leading-relaxed">
            Multi-node LangGraph agent evaluating error frequencies, correlating incident signatures,
            retrieving technical runbooks from ChromaDB, and producing evidence-backed root cause reports.
          </p>
        </div>

        <button
          onClick={() => onNavigate('investigation')}
          className="relative z-10 flex items-center gap-2.5 px-6 py-3.5 rounded-2xl text-xs font-bold bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-glow-md shadow-indigo-500/30 transition-all duration-200 shrink-0 active:scale-95 group"
        >
          <Sparkles className="w-4 h-4 text-indigo-100 group-hover:rotate-12 transition-transform" />
          <span>New Incident Investigation</span>
          <ArrowRight className="w-4 h-4 text-indigo-200 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>

      {/* Primary Telemetry Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Investigations"
          value={stats.totalInvestigations}
          icon={Activity}
          subtitle="Processed by Agentic Engine"
          color="indigo"
        />
        <StatCard
          title="Critical Outages"
          value={stats.criticalCount}
          icon={AlertOctagon}
          subtitle="Immediate Triage Incidents"
          color="red"
        />
        <StatCard
          title="High Severity Incidents"
          value={stats.highCount}
          icon={AlertTriangle}
          subtitle="Service Degradation Events"
          color="orange"
        />
        <StatCard
          title="Runbooks in ChromaDB"
          value={stats.totalDocuments}
          icon={BookOpen}
          subtitle="384-dim Embedded Chunks"
          color="emerald"
        />
      </div>

      {/* Interactive Quick Start Telemetry Scanner */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4 mb-5">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Simulate Real Infrastructure Failures</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Select a benchmark failure scenario to launch an automated multi-node investigation
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/25 self-start sm:self-auto">
            Ready to Investigate
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            onClick={() => onNavigate('investigation')}
            className="p-4 rounded-xl bg-[#090D17] border border-slate-800/80 hover:border-indigo-500/40 card-hover cursor-pointer space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <span className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 group-hover:scale-110 transition-transform">
                <Database className="w-4 h-4" />
              </span>
              <SeverityBadge severity="HIGH" size="sm" />
            </div>
            <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">
              Database Connection Pool Exhaustion
            </h4>
            <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
              HikariCP connection timeouts, thread starvations, and HTTP 500 error cascades.
            </p>
          </div>

          <div
            onClick={() => onNavigate('investigation')}
            className="p-4 rounded-xl bg-[#090D17] border border-slate-800/80 hover:border-rose-500/40 card-hover cursor-pointer space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <span className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 group-hover:scale-110 transition-transform">
                <KeyRound className="w-4 h-4" />
              </span>
              <SeverityBadge severity="CRITICAL" size="sm" />
            </div>
            <h4 className="text-xs font-bold text-white group-hover:text-rose-300 transition-colors">
              Authentication Key & JWT Failure
            </h4>
            <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
              Expired secret keys, invalid token signatures, and complete service login degradation.
            </p>
          </div>

          <div
            onClick={() => onNavigate('investigation')}
            className="p-4 rounded-xl bg-[#090D17] border border-slate-800/80 hover:border-amber-500/40 card-hover cursor-pointer space-y-2 group"
          >
            <div className="flex items-center justify-between">
              <span className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 group-hover:scale-110 transition-transform">
                <MemoryStick className="w-4 h-4" />
              </span>
              <SeverityBadge severity="CRITICAL" size="sm" />
            </div>
            <h4 className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors">
              Java Heap Space Out of Memory
            </h4>
            <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
              GC overhead limit exceeded, worker process crash, and node eviction.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Investigations List */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                Recent Incident Investigations
              </h3>
              <p className="text-[10px] text-slate-400">Persisted in SQLite database</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadDashboardData}
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition"
              title="Refresh table"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 transition"
            >
              <span>View All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {recentInvestigations.length === 0 ? (
          <div className="text-center py-10 space-y-2">
            <Clock className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400 font-medium">No recent investigations found.</p>
            <p className="text-[11px] text-slate-500">
              Run your first incident investigation to see historical RCA reports here.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {recentInvestigations.slice(0, 5).map((inv) => (
              <div
                key={inv.investigation_id}
                onClick={() => onSelectInvestigation && onSelectInvestigation(inv.investigation_id)}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-[#080C16] border border-slate-800/80 hover:border-indigo-500/40 card-hover cursor-pointer group"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={inv.severity} size="sm" />
                    <span className="text-[10px] font-mono text-slate-500">
                      ID: {inv.investigation_id.slice(0, 8)}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition-colors">
                    {inv.incident_title || 'Application Incident'}
                  </h4>
                  {inv.affected_services?.length > 0 && (
                    <p className="text-[10px] text-slate-400 font-mono">
                      Services: {inv.affected_services.join(', ')}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto shrink-0">
                  <span className="text-[10px] font-mono text-slate-400">
                    {inv.created_at ? new Date(inv.created_at).toLocaleDateString() : 'Recent'}
                  </span>
                  <div className="p-1.5 rounded-lg bg-slate-800/60 text-slate-400 group-hover:text-indigo-300 group-hover:bg-indigo-600/20 transition">
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
