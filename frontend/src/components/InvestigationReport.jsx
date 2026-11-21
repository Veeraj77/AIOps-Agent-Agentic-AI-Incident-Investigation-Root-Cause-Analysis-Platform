import React, { useState } from 'react';
import SeverityBadge from './SeverityBadge';
import RootCauseCard from './RootCauseCard';
import EvidencePanel from './EvidencePanel';
import RemediationPanel from './RemediationPanel';
import {
  Calendar,
  Activity,
  ArrowLeft,
  Share2,
  Download,
  Check,
  Hash,
  Server,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function InvestigationReport({ report, onBack }) {
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner with Navigation & Metadata */}
      <div className="glass-panel-elevated rounded-2xl p-6 border border-slate-800/90 shadow-2xl relative overflow-hidden">
        {/* Subtle Accent Glow */}
        <div className="absolute top-0 right-0 w-80 h-32 bg-indigo-500/10 blur-[80px] pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="flex items-start sm:items-center gap-4">
            {onBack && (
              <button
                onClick={onBack}
                className="p-2.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/80 transition shadow-sm active:scale-95 shrink-0"
                title="Back to input console"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}

            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="text-[11px] font-mono text-slate-400 bg-slate-900/90 border border-slate-800 px-2 py-0.5 rounded-md flex items-center gap-1 font-semibold">
                  <Hash className="w-3 h-3 text-indigo-400" />
                  {report.investigation_id ? report.investigation_id.slice(0, 8) : 'AUTO-RCA'}
                </span>
                <span className="text-slate-600">•</span>
                <span className="text-[11px] font-mono text-slate-400 flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-500" />
                  {report.created_at ? new Date(report.created_at).toLocaleString() : 'Just now'}
                </span>
                <span className="text-slate-600">•</span>
                <span className="text-[11px] font-mono text-indigo-400 font-semibold flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  LangGraph Synthesized
                </span>
              </div>

              <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
                {report.incident_title || 'Application Incident Root Cause Investigation'}
              </h2>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 self-start lg:self-auto">
            <SeverityBadge severity={report.severity} size="lg" />

            <button
              onClick={handleCopyJson}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-300 border border-slate-700/80 text-xs font-semibold transition active:scale-95 shadow-sm"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Share2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>Export JSON</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Affected Services Bar */}
        {(report.affected_services?.length > 0 || report.detected_patterns?.length > 0) && (
          <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mr-1">
              Impacted Topology:
            </span>
            {report.affected_services?.map((svc, i) => (
              <span
                key={i}
                className="text-[11px] font-mono font-medium px-2.5 py-0.5 rounded-lg bg-indigo-500/10 text-indigo-300 border border-indigo-500/25 flex items-center gap-1"
              >
                <Server className="w-3 h-3 text-indigo-400" />
                <span>{svc}</span>
              </span>
            ))}
            {report.detected_patterns?.map((pat, i) => (
              <span
                key={i}
                className="text-[11px] font-mono font-medium px-2.5 py-0.5 rounded-lg bg-violet-500/10 text-violet-300 border border-violet-500/25 flex items-center gap-1"
              >
                <Layers className="w-3 h-3 text-violet-400" />
                <span>{pat}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Primary Root Cause Diagnosis Card */}
      <RootCauseCard
        probableRootCause={report.probable_root_cause}
        alternativeCauses={report.alternative_causes}
        confidence={report.confidence}
        confidenceReasoning={report.confidence_reasoning}
        limitations={report.limitations}
      />

      {/* Dual Summaries: Executive & Technical */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Executive Summary */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 card-hover relative overflow-hidden space-y-2.5">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-indigo-500 opacity-80" />
          <span className="text-[10px] font-mono uppercase text-indigo-400 font-extrabold tracking-wider bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 inline-block">
            Executive Summary • Leadership & Stakeholders
          </span>
          <p className="text-xs text-slate-200 leading-relaxed font-sans font-medium">
            {report.executive_summary || 'No executive summary generated.'}
          </p>
        </div>

        {/* Technical Summary */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 card-hover relative overflow-hidden space-y-2.5">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-purple-500 opacity-80" />
          <span className="text-[10px] font-mono uppercase text-purple-400 font-extrabold tracking-wider bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20 inline-block">
            Technical Summary • SRE & DevOps Engineers
          </span>
          <p className="text-xs text-slate-200 leading-relaxed font-sans font-medium">
            {report.technical_summary || 'No technical summary generated.'}
          </p>
        </div>
      </div>

      {/* Observable Symptoms (Observed Facts) */}
      {report.symptoms && report.symptoms.length > 0 && (
        <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3.5 flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" />
            <span>Observed Operational Symptoms ({report.symptoms.length})</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {report.symptoms.map((symptom, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 bg-[#090D17] p-3 rounded-xl border border-slate-800/80 text-xs text-slate-200 font-medium"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0 mt-1.5 shadow-[0_0_6px_rgba(129,140,248,0.8)]" />
                <span className="leading-relaxed">{symptom}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Supporting Evidence & RAG Document References */}
      <EvidencePanel
        evidence={report.supporting_evidence}
        documentReferences={report.document_references}
      />

      {/* Prioritized Engineering Remediation Roadmap */}
      <RemediationPanel
        remediationSteps={report.recommended_remediation}
        immediateActions={report.immediate_actions}
        additionalInfoRequired={report.additional_info_required}
      />
    </div>
  );
}
