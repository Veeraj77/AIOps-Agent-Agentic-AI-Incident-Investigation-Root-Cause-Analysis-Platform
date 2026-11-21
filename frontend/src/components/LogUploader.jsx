import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Sparkles,
  X,
  Terminal,
  Database,
  KeyRound,
  MemoryStick,
  Search,
  ArrowRight,
  HelpCircle,
} from 'lucide-react';

export default function LogUploader({
  logs,
  onLogsChange,
  onAnalyze,
  onRunInvestigation,
  isSubmitting,
}) {
  const [question, setQuestion] = useState('Why is the application failing?');
  const [uploadedFileName, setUploadedFileName] = useState('');

  const sampleDbIncident = `2026-11-17 14:30:15 WARNING DatabaseService - Connection pool usage at 85% (17/20 connections)
2026-11-17 14:30:28 ERROR DatabaseService - Connection pool exhausted. No available connections.
2026-11-17 14:30:30 ERROR OrderService - Failed to process order #98214: Database connection timeout after 30000ms
2026-11-17 14:30:31 WARNING APIGateway - API response time exceeded 5000ms for /api/orders
2026-11-17 14:30:32 ERROR HTTP 500 - /api/orders - Internal Server Error
2026-11-17 14:30:35 CRITICAL DatabaseService - HikariCP pool blocked: 24 threads waiting for connection`;

  const sampleAuthIncident = `2026-11-17 09:15:00 WARNING AuthService - JWT token validation latency elevated: 420ms avg
2026-11-17 09:16:00 ERROR AuthService - JWT secret key verification failed: token signature is invalid or expired
2026-11-17 09:16:01 ERROR HTTP 401 - /api/auth/login - Unauthorized: Invalid token signature
2026-11-17 09:16:02 ERROR HTTP 403 - /api/admin/users - Access denied for user admin@company.com
2026-11-17 09:16:05 ERROR AuthService - Public key rotation failed: keystore endpoint unreachable
2026-11-17 09:16:10 CRITICAL AuthService - Authentication service degraded: all login validations failing`;

  const sampleOomIncident = `2026-11-17 16:20:00 WARNING WorkerNode - JVM heap memory utilization above 90%
2026-11-17 16:20:45 WARNING WorkerNode - Full GC pause duration exceeded 4200ms
2026-11-17 16:21:00 ERROR WorkerNode - java.lang.OutOfMemoryError: Java heap space
2026-11-17 16:21:02 CRITICAL WorkerNode - Garbage collection overhead limit exceeded
2026-11-17 16:21:05 ERROR WorkerNode - Worker process 1421 crashed due to memory exhaustion`;

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content === 'string') {
        onLogsChange(content);
      }
    };
    reader.readAsText(file);
  };

  const handleClear = () => {
    onLogsChange('');
    setUploadedFileName('');
  };

  return (
    <div className="glass-panel-elevated rounded-2xl p-6 md:p-7 border border-slate-800/90 shadow-2xl relative overflow-hidden">
      {/* Decorative Top Accent Glow */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-80" />

      {/* Header with Title and Quick Sample Pills */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Terminal className="w-4 h-4" />
            </span>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Incident Telemetry & Log Ingestion
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Feed raw error streams for autonomous LangGraph multi-node RCA reasoning
          </p>
        </div>

        {/* Quick Sample Selector Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-medium text-slate-400 mr-1">Load Incident:</span>
          <button
            type="button"
            onClick={() => onLogsChange(sampleDbIncident)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900/90 hover:bg-slate-800 text-indigo-300 border border-indigo-500/30 hover:border-indigo-400/50 shadow-sm transition-all duration-150"
          >
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span>DB Pool Crash</span>
          </button>
          <button
            type="button"
            onClick={() => onLogsChange(sampleAuthIncident)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900/90 hover:bg-slate-800 text-amber-300 border border-amber-500/30 hover:border-amber-400/50 shadow-sm transition-all duration-150"
          >
            <KeyRound className="w-3.5 h-3.5 text-amber-400" />
            <span>JWT Auth Outage</span>
          </button>
          <button
            type="button"
            onClick={() => onLogsChange(sampleOomIncident)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900/90 hover:bg-slate-800 text-rose-300 border border-rose-500/30 hover:border-rose-400/50 shadow-sm transition-all duration-150"
          >
            <MemoryStick className="w-3.5 h-3.5 text-rose-400" />
            <span>Heap OOM Crash</span>
          </button>
        </div>
      </div>

      {/* Terminal Editor Frame */}
      <div className="rounded-xl border border-slate-800/90 bg-[#060910] overflow-hidden shadow-inner">
        {/* Terminal Title Bar */}
        <div className="h-9 bg-slate-900/70 border-b border-slate-800/80 px-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-[11px] font-mono text-slate-400 ml-2 font-medium">
              telemetry-stream.log
            </span>
          </div>

          <div className="flex items-center gap-3">
            {logs && (
              <span className="text-[10px] font-mono text-slate-500">
                {logs.split('\n').filter(Boolean).length} lines • {logs.length} chars
              </span>
            )}
            {logs && (
              <button
                onClick={handleClear}
                className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-rose-300 transition"
                title="Clear input"
              >
                <X className="w-3 h-3" />
                <span>Clear</span>
              </button>
            )}
          </div>
        </div>

        {/* Textarea */}
        <textarea
          value={logs}
          onChange={(e) => onLogsChange(e.target.value)}
          placeholder="Paste log output here (e.g. 2026-11-17 14:30:28 ERROR Database connection pool exhausted...)"
          rows={9}
          className="w-full bg-transparent p-4 font-mono text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none leading-relaxed resize-y selection:bg-indigo-500/30"
          spellCheck={false}
        />
      </div>

      {/* Auxiliary Inputs: Investigation Question & File Upload */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Question Prompt Input */}
        <div>
          <label className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-1.5">
            <span>Investigation Directive / Question</span>
            <span className="text-[10px] font-mono text-slate-500">Prompt Guidance</span>
          </label>
          <div className="relative">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Why is the application failing?"
              className="w-full bg-[#0A0F1D] border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30 transition shadow-inner font-medium"
            />
          </div>
        </div>

        {/* File Drag-and-Drop Box */}
        <div>
          <label className="flex items-center justify-between text-xs font-semibold text-slate-300 mb-1.5">
            <span>Upload Log File</span>
            <span className="text-[10px] font-mono text-slate-500">.log, .txt (up to 50MB)</span>
          </label>
          <label className="flex items-center justify-between px-4 py-2 rounded-xl bg-[#0A0F1D] border border-dashed border-slate-700/80 hover:border-indigo-500/60 hover:bg-slate-900/60 transition cursor-pointer group shadow-inner">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <UploadCloud className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
              <span className="text-xs text-slate-400 truncate">
                {uploadedFileName || 'Drop .log or .txt file here'}
              </span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 shrink-0">
              Browse
            </span>
            <input
              type="file"
              accept=".log,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {/* Action Buttons Bar */}
      <div className="mt-6 pt-5 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
          <span>Need quick triage? Use rule scan for instant 6ms telemetry.</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Quick Deterministic Scan */}
          <button
            type="button"
            onClick={() => onAnalyze(logs)}
            disabled={!logs.trim() || isSubmitting}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700/80 transition disabled:opacity-40 disabled:cursor-not-allowed shadow-sm active:scale-95"
          >
            <Search className="w-4 h-4 text-slate-400" />
            <span>Fast Rule Scan</span>
          </button>

          {/* Full Autonomous AI Agent Investigation Button */}
          <button
            type="button"
            onClick={() => onRunInvestigation(logs, question)}
            disabled={!logs.trim() || isSubmitting}
            className="flex items-center gap-2.5 px-6 py-2.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:via-indigo-400 hover:to-violet-500 shadow-glow-md shadow-indigo-500/25 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none active:scale-95"
          >
            <Sparkles className="w-4 h-4 text-indigo-100 animate-pulse" />
            <span>Run AI RCA Investigation</span>
            <ArrowRight className="w-3.5 h-3.5 text-indigo-200" />
          </button>
        </div>
      </div>
    </div>
  );
}
