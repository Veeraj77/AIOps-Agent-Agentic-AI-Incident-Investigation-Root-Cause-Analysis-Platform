import React from 'react';
import SeverityBadge from './SeverityBadge';
import { AlertTriangle, CheckCircle, Flame, Layers, Hash, Activity } from 'lucide-react';

export default function IncidentSummary({ analysis }) {
  if (!analysis) return null;

  return (
    <div className="glass-panel-elevated p-6 my-6 space-y-5 relative overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-glow-sm">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                Deterministic Pattern Scan
              </span>
              <span className="text-[10px] font-mono text-slate-500">Fast Triage (Sub-10ms)</span>
            </div>
            <h3 className="text-base font-semibold text-white tracking-tight mt-1">
              {analysis.summary || 'Incident Pattern Analysis'}
            </h3>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[10px] uppercase font-mono text-slate-500">Severity Score</div>
            <div className="text-xs font-mono font-bold text-slate-300">{analysis.severity_score}/100</div>
          </div>
          <SeverityBadge severity={analysis.overall_severity} size="lg" />
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-[#0B0F19]/60 border border-slate-800/80 rounded-xl p-3.5">
          <span className="text-[11px] text-slate-400 font-medium">Telemetry Lines</span>
          <div className="text-xl font-bold font-mono text-white mt-1">{analysis.total_log_entries}</div>
        </div>
        <div className="bg-[#0B0F19]/60 border border-slate-800/80 rounded-xl p-3.5">
          <span className="text-[11px] text-slate-400 font-medium">Error Frequency</span>
          <div className="text-xl font-bold font-mono text-red-400 mt-1">{analysis.error_rate_percent}%</div>
        </div>
        <div className="bg-[#0B0F19]/60 border border-slate-800/80 rounded-xl p-3.5">
          <span className="text-[11px] text-slate-400 font-medium">Unique Exceptions</span>
          <div className="text-xl font-bold font-mono text-orange-400 mt-1">{analysis.unique_error_count}</div>
        </div>
        <div className="bg-[#0B0F19]/60 border border-slate-800/80 rounded-xl p-3.5">
          <span className="text-[11px] text-slate-400 font-medium">Matched Signatures</span>
          <div className="text-xl font-bold font-mono text-indigo-400 mt-1">{analysis.detected_patterns?.length || 0}</div>
        </div>
      </div>

      {/* Detected Anti-Patterns */}
      {analysis.detected_patterns && analysis.detected_patterns.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
            <Flame className="w-4 h-4 text-orange-400" />
            <span>Recognized Failure Signatures ({analysis.detected_patterns.length})</span>
          </h4>
          <div className="space-y-2.5">
            {analysis.detected_patterns.map((p, idx) => (
              <div
                key={idx}
                className="bg-[#0B0F19]/60 border border-slate-800/80 hover:border-slate-700/80 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{p.name}</span>
                    <SeverityBadge severity={p.severity} size="sm" />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{p.description}</p>
                  <p className="text-[11px] text-indigo-300/90 mt-1">
                    <strong className="text-slate-400 font-medium">Probable Cause:</strong> {p.probable_cause}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-[11px] font-mono text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-1 rounded-lg">
                    {p.match_count} occurrences
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Occurring Errors */}
      {analysis.top_errors && analysis.top_errors.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2.5 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span>Top Recurring Errors</span>
          </h4>
          <div className="bg-[#0B0F19]/80 border border-slate-800/80 rounded-xl divide-y divide-slate-800/60 font-mono text-xs overflow-hidden">
            {analysis.top_errors.map((err, i) => (
              <div key={i} className="p-3 flex items-center justify-between text-slate-300 gap-4 hover:bg-slate-800/30 transition">
                <span className="truncate text-red-300">{err.message}</span>
                <span className="shrink-0 text-slate-500 text-[11px] bg-slate-800/80 px-2 py-0.5 rounded">
                  {err.count}x ({err.percentage}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Affected Services & Endpoints */}
      {(analysis.affected_services?.length > 0 || analysis.affected_endpoints?.length > 0) && (
        <div className="flex flex-wrap gap-4 pt-2 border-t border-slate-800/60">
          {analysis.affected_services?.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-medium">Services:</span>
              <div className="flex flex-wrap gap-1">
                {analysis.affected_services.map((svc, i) => (
                  <span key={i} className="bg-slate-800/80 border border-slate-700/60 text-slate-200 px-2.5 py-0.5 rounded-lg text-[11px]">
                    {svc}
                  </span>
                ))}
              </div>
            </div>
          )}
          {analysis.affected_endpoints?.length > 0 && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-medium">Endpoints:</span>
              <div className="flex flex-wrap gap-1">
                {analysis.affected_endpoints.map((ep, i) => (
                  <span key={i} className="bg-indigo-950/40 border border-indigo-800/40 text-indigo-300 px-2.5 py-0.5 rounded-lg text-[11px] font-mono">
                    {ep}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
