import React from 'react';
import { Server, Cpu, CheckCircle2, AlertCircle, FileCode } from 'lucide-react';

export default function Header({ title, subtitle, health }) {
  const isHealthy = health?.healthy;

  return (
    <header className="h-16 bg-[#0B0F19]/80 backdrop-blur-xl border-b border-slate-800/80 px-8 flex items-center justify-between z-10 sticky top-0">
      <div>
        <h2 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
          <span>{title}</span>
        </h2>
        {subtitle && (
          <p className="text-xs text-slate-400 font-medium tracking-normal mt-0.5 line-clamp-1">
            {subtitle}
          </p>
        )}
      </div>

      <div className="flex items-center gap-3 text-xs">
        {/* Engine Status Chip */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full border backdrop-blur-md transition ${
            isHealthy
              ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
              : 'bg-rose-500/10 border-rose-500/25 text-rose-400'
          }`}
        >
          {isHealthy ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
          )}
          <span className="font-semibold text-[11px]">
            {isHealthy ? 'FastAPI Operational' : 'Connecting to Engine...'}
          </span>
        </div>

        {/* LLM Model Chip */}
        <div className="hidden md:flex items-center gap-2 bg-slate-900/90 border border-slate-800/90 px-3.5 py-1.5 rounded-full text-slate-400 shadow-sm">
          <Cpu className="w-3.5 h-3.5 text-indigo-400" />
          <span>
            Model: <strong className="text-slate-200 font-semibold">{health?.llm_model || 'llama3-8b-8192'}</strong>
          </span>
        </div>

        {/* Provider Chip */}
        <div className="hidden sm:flex items-center gap-2 bg-slate-900/90 border border-slate-800/90 px-3.5 py-1.5 rounded-full text-slate-400 shadow-sm">
          <Server className="w-3.5 h-3.5 text-violet-400" />
          <span>
            Provider: <strong className="text-slate-200 font-semibold capitalize">{health?.llm_provider || 'groq'}</strong>
          </span>
        </div>

        {/* API Docs Button */}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-300 border border-indigo-500/25 transition font-medium text-[11px]"
        >
          <FileCode className="w-3.5 h-3.5 text-indigo-400" />
          <span>REST API</span>
        </a>
      </div>
    </header>
  );
}
