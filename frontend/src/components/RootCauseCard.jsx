import React from 'react';
import { Target, HelpCircle, ShieldAlert, Sparkles, Brain, CheckCircle2 } from 'lucide-react';

export default function RootCauseCard({
  probableRootCause,
  alternativeCauses = [],
  confidence = 'MEDIUM',
  confidenceReasoning,
  limitations = [],
}) {
  const confidenceColor = {
    HIGH: {
      badge: 'text-emerald-300 bg-emerald-500/15 border-emerald-500/40 shadow-glow-emerald shadow-emerald-500/10',
      label: 'HIGH CONFIDENCE',
      dot: 'bg-emerald-400',
    },
    MEDIUM: {
      badge: 'text-amber-300 bg-amber-500/15 border-amber-500/40',
      label: 'MEDIUM CONFIDENCE',
      dot: 'bg-amber-400',
    },
    LOW: {
      badge: 'text-rose-300 bg-rose-500/15 border-rose-500/40 shadow-glow-red shadow-rose-500/10',
      label: 'LOW CONFIDENCE',
      dot: 'bg-rose-400',
    },
  }[confidence?.toUpperCase()] || {
    badge: 'text-slate-300 bg-slate-500/15 border-slate-500/40',
    label: 'UNKNOWN',
    dot: 'bg-slate-400',
  };

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 md:p-7 border border-indigo-500/30 shadow-2xl relative overflow-hidden group">
      {/* Ambient Radial Halo */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-indigo-500/15 via-purple-500/5 to-transparent rounded-full blur-3xl pointer-events-none -z-0" />
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-90" />

      {/* Header with AI Hypothesis Badge */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-glow-sm shadow-indigo-500/30">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-extrabold text-indigo-400 uppercase tracking-wider font-mono">
                Root Cause Synthesis
              </span>
              <span className="text-[10px] font-mono font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Brain className="w-3 h-3 text-amber-400" />
                <span>AI Hypothesis</span>
              </span>
            </div>
            <h3 className="text-base font-bold text-white tracking-tight mt-0.5">
              Primary Diagnostic Assessment
            </h3>
          </div>
        </div>

        {/* Confidence Meter Badge */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Confidence Score:</span>
          <span
            className={`text-xs font-bold px-3 py-1 rounded-xl border font-mono tracking-wider flex items-center gap-1.5 backdrop-blur-md ${confidenceColor.badge}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${confidenceColor.dot} animate-pulse`} />
            <span>{confidenceColor.label}</span>
          </span>
        </div>
      </div>

      {/* Main Probable Root Cause Statement */}
      <div className="mt-5 p-5 rounded-xl bg-[#080C16] border border-indigo-900/40 relative shadow-inner">
        <div className="flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
          <div className="space-y-2 flex-1">
            <p className="text-sm md:text-base text-slate-100 font-semibold leading-relaxed">
              {probableRootCause || 'Root cause investigation inconclusive.'}
            </p>
            {confidenceReasoning && (
              <p className="text-xs text-slate-400 leading-relaxed font-sans bg-slate-900/60 p-3 rounded-lg border border-slate-800/80">
                <strong className="text-indigo-300">Diagnostic Justification:</strong>{' '}
                {confidenceReasoning}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Alternative Hypotheses */}
      {alternativeCauses && alternativeCauses.length > 0 && (
        <div className="mt-5">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-1.5 font-mono">
            <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
            <span>Alternative Hypotheses Considered</span>
          </h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
            {alternativeCauses.map((cause, i) => (
              <li
                key={i}
                className="flex items-start gap-2.5 bg-[#090D18] p-3 rounded-xl border border-slate-800/80 font-medium"
              >
                <span className="text-indigo-400 font-bold mt-0.5">•</span>
                <span className="leading-relaxed">{cause}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Limitations / Caveats */}
      {limitations && limitations.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-400">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-slate-300 font-mono text-[11px] uppercase tracking-wider">
              Diagnostic Caveats & Limitations:
            </span>
            {limitations.map((lim, i) => (
              <p key={i} className="text-slate-400 text-xs leading-relaxed">
                {lim}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
