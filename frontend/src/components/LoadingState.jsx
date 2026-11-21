import React from 'react';
import { Loader2, Bot, Search, FileText, CheckCircle2, Cpu, Sparkles } from 'lucide-react';

export default function LoadingState({
  message = 'Autonomous AI agent investigating incident telemetry...',
  currentStep = 1,
}) {
  const steps = [
    { id: 1, label: 'Parsing & normalizing error streams', icon: FileText },
    { id: 2, label: 'Detecting failure anti-patterns & calculating severity', icon: Search },
    { id: 3, label: 'Semantic RAG retrieval from ChromaDB vector store', icon: Bot },
    { id: 4, label: 'Synthesizing root cause hypothesis & generating remediation', icon: CheckCircle2 },
  ];

  return (
    <div className="glass-panel-elevated rounded-2xl p-8 md:p-10 flex flex-col items-center justify-center text-center my-6 border border-indigo-500/30 relative overflow-hidden">
      {/* Background Animated Glow */}
      <div className="absolute w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl animate-pulse -z-0" />

      {/* Cybernetic Agent Spinner */}
      <div className="relative mb-6 z-10">
        <div className="w-20 h-20 rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin flex items-center justify-center shadow-glow-md shadow-indigo-500/30">
          <Bot className="w-8 h-8 text-indigo-400" />
        </div>
        <div className="absolute -inset-1 rounded-full border border-indigo-400/30 animate-ping opacity-30" />
      </div>

      <div className="relative z-10 max-w-lg space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[10px] font-mono font-bold uppercase tracking-wider">
          <Sparkles className="w-3 h-3 text-indigo-400" />
          <span>LangGraph Multi-Node Workflow Active</span>
        </div>
        <h3 className="text-lg font-extrabold text-white tracking-tight">{message}</h3>
        <p className="text-xs text-slate-400 font-medium leading-relaxed">
          The agent is evaluating log telemetry, executing vector similarity queries, and synthesizing evidence-grounded hypotheses.
        </p>
      </div>

      {/* Progress Steps List */}
      <div className="w-full max-w-md space-y-2.5 text-left mt-8 relative z-10">
        {steps.map((s) => {
          const Icon = s.icon;
          const isDone = currentStep > s.id;
          const isCurrent = currentStep === s.id;
          return (
            <div
              key={s.id}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all duration-300 ${
                isCurrent
                  ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-200 border border-indigo-500/40 shadow-glow-sm shadow-indigo-500/15'
                  : isDone
                  ? 'bg-slate-900/60 text-slate-400 border border-slate-800 opacity-60'
                  : 'bg-[#080C16] text-slate-500 border border-slate-800/60'
              }`}
            >
              <div
                className={`p-1.5 rounded-lg border ${
                  isCurrent
                    ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                    : isDone
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                    : 'bg-slate-800 border-slate-700 text-slate-500'
                }`}
              >
                <Icon className="w-3.5 h-3.5 shrink-0" />
              </div>
              <span className="flex-1 font-mono text-[11px]">{s.label}</span>
              {isDone && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
              {isCurrent && (
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400 shrink-0" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
