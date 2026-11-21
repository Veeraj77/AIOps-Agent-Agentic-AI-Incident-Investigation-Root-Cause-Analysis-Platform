import React from 'react';
import { ShieldCheck, BookOpen, FileCode, CheckCircle2, FileText, ArrowUpRight } from 'lucide-react';

export default function EvidencePanel({ evidence = [], documentReferences = [] }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 my-6">
      {/* Supporting Log Evidence */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                  Observed Log Evidence
                </h3>
                <p className="text-[10px] text-slate-400">Ground-truth log line telemetry</p>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded-full">
              {evidence.length} citations
            </span>
          </div>

          {evidence.length === 0 ? (
            <div className="py-8 text-center space-y-1">
              <FileCode className="w-6 h-6 text-slate-600 mx-auto" />
              <p className="text-xs text-slate-500 italic">
                No specific log citations recorded.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {evidence.map((ev, i) => (
                <div
                  key={i}
                  className="bg-[#080C16] border border-slate-800/90 rounded-xl p-3.5 text-xs space-y-2 card-hover relative overflow-hidden"
                >
                  <div className="flex items-center justify-between text-slate-400 font-mono text-[10px]">
                    <span className="flex items-center gap-1 font-semibold text-slate-300">
                      <FileText className="w-3 h-3 text-indigo-400" />
                      Source: {ev.source}
                    </span>
                    {ev.line_number && (
                      <span className="bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">
                        Line #{ev.line_number}
                      </span>
                    )}
                  </div>

                  <div className="font-mono text-rose-300 bg-[#0E1320] p-3 rounded-lg border border-rose-950/40 text-[11px] overflow-x-auto leading-relaxed border-l-2 border-l-rose-500">
                    {ev.content}
                  </div>

                  {ev.relevance && (
                    <p className="text-slate-400 text-[11px] leading-relaxed pt-0.5 flex items-start gap-1.5">
                      <strong className="text-indigo-300 font-semibold shrink-0">Relevance:</strong>
                      <span>{ev.relevance}</span>
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Retrieved Knowledge Base References (RAG) */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-md flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <BookOpen className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                  RAG Knowledge Citations
                </h3>
                <p className="text-[10px] text-slate-400">ChromaDB semantic runbook chunks</p>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/25 px-2.5 py-1 rounded-full">
              {documentReferences.length} retrieved
            </span>
          </div>

          {documentReferences.length === 0 ? (
            <div className="py-8 text-center space-y-1">
              <BookOpen className="w-6 h-6 text-slate-600 mx-auto" />
              <p className="text-xs text-slate-500 italic">
                No matching runbook documentation found for this incident query.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {documentReferences.map((doc, i) => (
                <div
                  key={i}
                  className="bg-[#080C16] border border-slate-800/90 rounded-xl p-3.5 text-xs space-y-2 card-hover relative overflow-hidden"
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate text-indigo-300 font-bold text-xs flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                      {doc.document_name}
                    </span>
                    <span className="text-[10px] font-mono font-extrabold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                      {(doc.relevance_score * 100).toFixed(0)}% Match
                    </span>
                  </div>

                  <p className="text-slate-300 text-xs bg-[#0E1320] p-3 rounded-lg border border-slate-800/80 leading-relaxed font-sans line-clamp-3 italic border-l-2 border-l-indigo-500">
                    "{doc.excerpt}"
                  </p>

                  {doc.page_number && (
                    <p className="text-slate-500 text-[10px] font-mono">Page {doc.page_number}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
