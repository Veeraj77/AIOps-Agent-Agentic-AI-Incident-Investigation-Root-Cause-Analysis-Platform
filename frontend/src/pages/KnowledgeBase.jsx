import React, { useState, useEffect } from 'react';
import DocumentUploader from '../components/DocumentUploader';
import { api } from '../services/api';
import {
  BookOpen,
  Database,
  RefreshCw,
  FileText,
  CheckCircle2,
  Layers,
  Sparkles,
  Cpu,
  Search,
} from 'lucide-react';

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [docsData, statsData] = await Promise.all([
        api.getDocuments(),
        api.getDocumentStats(),
      ]);
      setDocuments(docsData || []);
      setStats(statsData || null);
    } catch (err) {
      setError(err.message || 'Failed to fetch knowledge base data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUploadSuccess = async (file) => {
    await api.uploadDocument(file);
    await fetchData(); // refresh list and stats
  };

  return (
    <div className="space-y-6">
      {/* ChromaDB Telemetry Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel rounded-2xl p-5 border border-slate-800/80 card-hover bg-gradient-to-b from-indigo-950/20 to-transparent">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              ChromaDB Collection
            </span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-bold text-white truncate font-mono tracking-tight mt-1">
            {stats?.collection_name || 'aiops_knowledge_base'}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            Cosine distance metric (hnsw:space: cosine)
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-slate-800/80 card-hover bg-gradient-to-b from-emerald-950/20 to-transparent">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              Embedded Chunks
            </span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight mt-1">
            {stats?.document_count || 0}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            Vectorized with all-MiniLM-L6-v2 (384-dim)
          </p>
        </div>

        <div className="glass-panel rounded-2xl p-5 border border-slate-800/80 card-hover bg-gradient-to-b from-purple-950/20 to-transparent">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
              Ingested Documents
            </span>
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white tracking-tight mt-1">
            {documents.length}
          </div>
          <p className="text-[11px] text-slate-500 mt-1 font-medium">
            PDF, Markdown & TXT runbooks active
          </p>
        </div>
      </div>

      {/* Upload Box Component */}
      <DocumentUploader onUploadSuccess={handleUploadSuccess} />

      {/* Ingested Documents List */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                Ingested Technical Runbooks & Architecture Docs
              </h3>
              <p className="text-xs text-slate-400">
                Indexed in ChromaDB for dynamic semantic context injection
              </p>
            </div>
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700/60 transition"
            title="Refresh list"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs mb-4">
            {error}
          </div>
        )}

        {documents.length === 0 ? (
          <div className="text-center py-12 space-y-2">
            <FileText className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-300 font-semibold">No runbooks uploaded yet.</p>
            <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
              Upload PDF or Markdown runbooks above to ground the AI agent with domain knowledge.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="bg-[#080C16] border border-slate-800/90 rounded-xl p-4 card-hover flex flex-col justify-between space-y-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5 overflow-hidden">
                    <span className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shrink-0">
                      <FileText className="w-4 h-4" />
                    </span>
                    <div className="truncate">
                      <h4 className="text-xs font-bold text-white truncate">{doc.filename}</h4>
                      <p className="text-[10px] text-slate-500 font-mono">
                        {(doc.file_size_bytes / 1024).toFixed(1)} KB • {doc.file_type?.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Embedded
                  </span>
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-2 border-t border-slate-800/80">
                  <span>Chunks: {doc.chunk_count}</span>
                  <span>{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Active'}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
