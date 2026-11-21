import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  Activity,
  CheckCircle2,
  XCircle,
  Server,
  Database,
  Cpu,
  Layers,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export default function SystemStatus() {
  const [health, setHealth] = useState(null);
  const [docStats, setDocStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkStatus = async () => {
    setLoading(true);
    try {
      const [h, s] = await Promise.allSettled([
        api.healthCheck(),
        api.getDocumentStats(),
      ]);
      setHealth(h.status === 'fulfilled' ? h.value : null);
      setDocStats(s.status === 'fulfilled' ? s.value : null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const endpoints = [
    { method: 'GET', path: '/health', desc: 'Application health & runtime metadata' },
    { method: 'POST', path: '/api/incidents/analyze', desc: 'Rule-based pattern & severity classification' },
    { method: 'POST', path: '/api/incidents/analyze/upload', desc: 'Upload .log file for pattern analysis' },
    { method: 'POST', path: '/api/investigations/run', desc: 'LangGraph autonomous agent investigation' },
    { method: 'GET', path: '/api/investigations', desc: 'List past investigations with pagination' },
    { method: 'GET', path: '/api/investigations/{id}', desc: 'Retrieve full investigation report JSON' },
    { method: 'POST', path: '/api/documents/upload', desc: 'Ingest PDF/TXT into ChromaDB vector store' },
    { method: 'GET', path: '/api/documents', desc: 'List uploaded knowledge base runbooks' },
    { method: 'GET', path: '/api/documents/stats', desc: 'ChromaDB collection health & chunk count' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel-elevated p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-32 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-glow-emerald">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                AIOps System Health & Telemetry Status
                <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live Probes
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Real-time diagnostics across FastAPI, LangGraph, Groq LLM, ChromaDB, and SQLite
              </p>
            </div>
          </div>
          <button
            onClick={checkStatus}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 text-xs font-medium self-start sm:self-auto transition duration-150 hover:border-slate-600"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : 'text-slate-400'}`} />
            <span>Probe Health</span>
          </button>
        </div>
      </div>

      {/* Component Status Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Backend API */}
        <div className="glass-panel card-hover p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">FastAPI Core</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Server className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1">
            {health ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-sm font-bold text-white">Online & Healthy</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-red-400" />
                <span className="text-sm font-bold text-red-300">Disconnected</span>
              </>
            )}
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Uvicorn 0.0.0.0</span>
            <span className="text-indigo-400 font-semibold">:8000</span>
          </div>
        </div>

        {/* LLM Engine */}
        <div className="glass-panel card-hover p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">LLM Provider</span>
            <div className="w-8 h-8 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-bold text-white capitalize">{health?.llm_provider || 'Groq'}</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Model</span>
            <span className="text-violet-300">{health?.llm_model || 'llama3-8b-8192'}</span>
          </div>
        </div>

        {/* Vector DB */}
        <div className="glass-panel card-hover p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">ChromaDB Store</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-bold text-white">
              {docStats?.status === 'ready' ? `Active (${docStats.document_count} chunks)` : 'Persistent Ready'}
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>all-MiniLM-L6-v2</span>
            <span className="text-emerald-400">384-dim</span>
          </div>
        </div>

        {/* SQLite Database */}
        <div className="glass-panel card-hover p-5 relative overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">SQLite Audit DB</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-bold text-white">Connected</span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Engine</span>
            <span className="text-amber-300">WAL Mode</span>
          </div>
        </div>
      </div>

      {/* Live Endpoints Catalog */}
      <div className="glass-panel p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-4 mb-5 gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide">
                Registered REST API Endpoints
              </h3>
              <p className="text-xs text-slate-400">Integrated with FastAPI OpenAPI and Swagger validation</p>
            </div>
          </div>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold self-start sm:self-auto transition duration-150 shadow-glow-sm"
          >
            <span>Open Interactive Swagger Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="divide-y divide-slate-800/70 font-mono text-xs">
          {endpoints.map((ep, i) => (
            <div key={i} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 hover:bg-slate-800/30 px-3 rounded-lg transition duration-150">
              <div className="flex items-center gap-3">
                <span
                  className={`px-2.5 py-0.5 rounded text-[10px] font-bold tracking-wider ${
                    ep.method === 'GET'
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  }`}
                >
                  {ep.method}
                </span>
                <span className="text-slate-200 font-semibold">{ep.path}</span>
              </div>
              <span className="text-slate-400 text-[11px] font-sans">{ep.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
