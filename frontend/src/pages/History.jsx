import React, { useState, useEffect } from 'react';
import SeverityBadge from '../components/SeverityBadge';
import { api } from '../services/api';
import { History as HistoryIcon, Search, Calendar, ChevronRight, RefreshCw, FileText, Layers, AlertTriangle } from 'lucide-react';

export default function History({ onSelectInvestigation }) {
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigations(100);
      setInvestigations(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load investigation history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filtered = investigations.filter((inv) => {
    const matchesSearch =
      inv.incident_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inv.affected_services?.some((s) => s.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesSeverity = severityFilter === 'ALL' || inv.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="glass-panel-elevated p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-32 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-glow-sm">
              <HistoryIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                Incident Audit Trail
                <span className="text-[10px] font-mono font-normal text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-full border border-slate-700/60">
                  SQLite Persistent
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Search, filter, and inspect previous autonomous root cause investigations
              </p>
            </div>
          </div>
          <button
            onClick={fetchHistory}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 text-xs font-medium self-start sm:self-auto transition duration-150 hover:border-slate-600"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-400' : 'text-slate-400'}`} />
            <span>Refresh Audit Log</span>
          </button>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-col sm:flex-row gap-3 pt-5 mt-5 border-t border-slate-800/70">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by incident title, service name, or error keywords..."
              className="glass-input w-full pl-10 pr-4 py-2.5 text-xs text-slate-200 placeholder:text-slate-500 rounded-lg"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition duration-150 ${
                  severityFilter === sev
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-glow-sm font-semibold'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-800'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-xs text-red-300 bg-red-950/30 border border-red-500/30 p-4 rounded-xl flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Investigations Table / List */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/70">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Recorded Investigations
            </span>
          </div>
          <span className="text-xs font-mono text-slate-500">
            Showing {filtered.length} of {investigations.length}
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin text-indigo-400 mx-auto" />
            <p className="text-xs text-slate-400">Querying SQLite investigation database...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-16 text-center text-slate-400 space-y-3">
            <div className="w-12 h-12 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center mx-auto text-slate-500">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-300">No matching investigation records found</p>
              <p className="text-[11px] text-slate-500 mt-1">Try adjusting your search query or severity filter</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((inv) => (
              <div
                key={inv.investigation_id}
                onClick={() => onSelectInvestigation(inv.investigation_id)}
                className="card-hover p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl cursor-pointer bg-[#0D1322]/60 border border-slate-800/80 hover:border-indigo-500/40 group"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-xs font-semibold text-white group-hover:text-indigo-300 transition duration-150 truncate">
                      {inv.incident_title}
                    </span>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400 font-mono">
                    <span className="flex items-center gap-1 text-slate-400">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      {new Date(inv.created_at).toLocaleString()}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-red-400 font-semibold">{inv.error_count} errors logged</span>
                    {inv.affected_services?.length > 0 && (
                      <>
                        <span className="text-slate-600">•</span>
                        <div className="flex items-center gap-1 font-sans">
                          {inv.affected_services.map((svc, sIdx) => (
                            <span
                              key={sIdx}
                              className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[10px]"
                            >
                              {svc}
                            </span>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-auto shrink-0">
                  <SeverityBadge severity={inv.severity} size="sm" />
                  <div className="w-7 h-7 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 group-hover:text-indigo-400 group-hover:border-indigo-500/40 transition duration-150">
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
