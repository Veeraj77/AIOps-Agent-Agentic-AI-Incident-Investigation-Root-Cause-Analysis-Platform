import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';

export default function DocumentUploader({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState(null); // { type: 'success' | 'error', message: '' }
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    // Validate extension
    const ext = selected.name.split('.').pop()?.toLowerCase();
    if (!['pdf', 'txt', 'md'].includes(ext)) {
      setStatus({
        type: 'error',
        message: 'Unsupported file type. Please upload a PDF, TXT, or MD document.',
      });
      setFile(null);
      return;
    }

    // Validate size (50MB)
    if (selected.size > 50 * 1024 * 1024) {
      setStatus({
        type: 'error',
        message: 'File size exceeds 50MB limit.',
      });
      setFile(null);
      return;
    }

    setFile(selected);
    setStatus(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) {
      const ext = dropped.name.split('.').pop()?.toLowerCase();
      if (!['pdf', 'txt', 'md'].includes(ext)) {
        setStatus({
          type: 'error',
          message: 'Unsupported file type. Please upload a PDF, TXT, or MD document.',
        });
        return;
      }
      setFile(dropped);
      setStatus(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setStatus(null);

    try {
      if (onUploadSuccess) {
        await onUploadSuccess(file);
      }
      setStatus({
        type: 'success',
        message: `Successfully embedded and indexed "${file.name}" in ChromaDB vector store!`,
      });
      setFile(null);
    } catch (err) {
      setStatus({
        type: 'error',
        message: err.message || 'Failed to upload and ingest document',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-panel-elevated p-6 relative overflow-hidden">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-glow-sm">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wide">
              Upload Knowledge Base Documentation
            </h3>
            <p className="text-xs text-slate-400">
              Ingest infrastructure runbooks, architecture specs, and triage guides into ChromaDB
            </p>
          </div>
        </div>
        <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-[11px] font-mono text-slate-400">
          <Sparkles className="w-3 h-3 text-indigo-400" />
          SentenceTransformers 384-d
        </span>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer ${
          isDragOver
            ? 'border-indigo-500 bg-indigo-500/10 shadow-glow-md'
            : file
            ? 'border-emerald-500/40 bg-emerald-500/5'
            : 'border-slate-700/80 hover:border-indigo-500/50 bg-[#0B0F19]/40 hover:bg-[#0B0F19]/70'
        }`}
      >
        <label className="cursor-pointer block">
          <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-3 text-indigo-400">
            <UploadCloud className="w-7 h-7" />
          </div>
          <span className="text-sm font-semibold text-slate-200 block mb-1">
            {file ? file.name : 'Click to select or drag & drop runbook file'}
          </span>
          <span className="text-xs text-slate-500 block">
            {file ? `${(file.size / 1024).toFixed(1)} KB — Ready to embed` : 'Supported formats: .pdf, .txt, .md (Max 50MB)'}
          </span>
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
      </div>

      {status && (
        <div
          className={`mt-4 p-3.5 rounded-xl text-xs flex items-center gap-2.5 backdrop-blur-md ${
            status.type === 'success'
              ? 'bg-emerald-950/30 text-emerald-300 border border-emerald-500/30 shadow-glow-emerald'
              : 'bg-red-950/30 text-red-300 border border-red-500/30'
          }`}
        >
          {status.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          )}
          <span>{status.message}</span>
        </div>
      )}

      <div className="mt-5 flex justify-end">
        <button
          type="button"
          disabled={!file || isUploading}
          onClick={handleUpload}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white shadow-glow-sm disabled:opacity-40 disabled:cursor-not-allowed transition duration-200"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Embedding Chunks into ChromaDB...</span>
            </>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              <span>Ingest & Vectorize Document</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
