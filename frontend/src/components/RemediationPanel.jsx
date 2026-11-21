import React from 'react';
import { Wrench, Zap, CheckCircle2, ArrowRight, ShieldCheck, Clock } from 'lucide-react';

export default function RemediationPanel({
  remediationSteps = [],
  immediateActions = [],
  additionalInfoRequired = [],
}) {
  return (
    <div className="glass-panel-elevated rounded-2xl p-6 md:p-7 border border-slate-800/90 shadow-xl my-6 space-y-7">
      {/* Immediate Triage Actions (P0 Urgent) */}
      {immediateActions && immediateActions.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/25">
                <Zap className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                  Immediate Emergency Mitigation (Triage)
                </h3>
                <p className="text-[10px] text-slate-400">Apply these steps immediately to halt service degradation</p>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/25 px-2.5 py-0.5 rounded-full">
              P0 Urgent
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {immediateActions.map((action, i) => (
              <div
                key={i}
                className="flex items-start gap-3 bg-amber-500/5 border border-amber-500/20 rounded-xl p-3.5 text-xs text-amber-200 card-hover"
              >
                <CheckCircle2 className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed font-medium">{action}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Prioritized Engineering Remediation Roadmap */}
      <div>
        <div className="flex items-center justify-between mb-3.5">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">
              <Wrench className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                Prioritized Engineering Remediation Plan
              </h3>
              <p className="text-[10px] text-slate-400">Structured permanent fixes and architecture hardening</p>
            </div>
          </div>
          <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full">
            {remediationSteps.length} Steps
          </span>
        </div>

        {remediationSteps.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-4 text-center">
            No specific remediation steps generated.
          </p>
        ) : (
          <div className="space-y-3">
            {remediationSteps.map((step, i) => (
              <div
                key={i}
                className="bg-[#080C16] border border-slate-800/90 rounded-xl p-4 text-xs space-y-2.5 card-hover relative overflow-hidden group"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <span className="w-6 h-6 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 text-white font-extrabold flex items-center justify-center text-xs shadow-glow-sm shadow-indigo-500/30 shrink-0">
                      {step.priority || i + 1}
                    </span>
                    <h4 className="font-bold text-white text-sm tracking-tight">{step.action}</h4>
                  </div>
                  {step.estimated_impact && (
                    <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded-full self-start sm:self-auto">
                      Impact: {step.estimated_impact}
                    </span>
                  )}
                </div>

                {step.rationale && (
                  <p className="text-slate-400 leading-relaxed text-xs pl-8 font-medium">
                    <strong className="text-slate-300">Rationale:</strong> {step.rationale}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Additional Telemetry Needed */}
      {additionalInfoRequired && additionalInfoRequired.length > 0 && (
        <div className="pt-4 border-t border-slate-800/80">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center gap-2 font-mono">
            <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />
            <span>Additional Observability Telemetry Required</span>
          </h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
            {additionalInfoRequired.map((info, i) => (
              <li
                key={i}
                className="bg-[#080C16] p-3 rounded-xl border border-slate-800/80 text-slate-400 flex items-center gap-2.5"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0 shadow-[0_0_6px_rgba(99,102,241,0.8)]" />
                <span className="truncate font-medium">{info}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
