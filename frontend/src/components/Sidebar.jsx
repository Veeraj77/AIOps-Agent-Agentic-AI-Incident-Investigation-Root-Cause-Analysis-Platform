import React from 'react';
import {
  LayoutDashboard,
  SearchCheck,
  BookOpen,
  History,
  Activity,
  Terminal,
  Cpu,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export default function Sidebar({ activeTab, onSelectTab, systemStatus }) {
  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard, badge: null },
    { id: 'investigation', label: 'New Investigation', icon: SearchCheck, badge: 'Agent' },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen, badge: null },
    { id: 'history', label: 'Investigation History', icon: History, badge: null },
    { id: 'status', label: 'System Status', icon: Activity, badge: null },
  ];

  return (
    <aside className="w-64 bg-[#0B0F19]/90 backdrop-blur-xl border-r border-slate-800/80 flex flex-col justify-between select-none z-20">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center gap-3.5 px-6 border-b border-slate-800/60 bg-gradient-to-b from-indigo-950/20 to-transparent">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 flex items-center justify-center shadow-glow-sm shadow-indigo-500/30">
              <Terminal className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-[#0B0F19]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-sm font-extrabold text-white tracking-wide">AIOps Agent</h1>
              <span className="text-[9px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-1.5 py-0.2 rounded-full">
                AI
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium">Incident RCA Platform</p>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="px-3 pt-5 pb-2">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectTab(item.id)}
                  className={`group relative w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600/20 via-indigo-500/10 to-transparent text-indigo-300 border border-indigo-500/30 shadow-glow-sm shadow-indigo-500/10'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'
                      }`}
                    />
                    <span>{item.label}</span>
                  </div>

                  {item.badge && (
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {item.badge}
                    </span>
                  )}

                  {isActive && (
                    <div className="absolute left-0 top-2 bottom-2 w-1 bg-indigo-500 rounded-r-full shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Quick Links Section */}
        <div className="px-3 pt-3">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Developer APIs
          </p>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition"
          >
            <div className="flex items-center gap-3">
              <Cpu className="w-4 h-4 text-slate-400" />
              <span>Swagger API Docs</span>
            </div>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>
        </div>
      </div>

      {/* System Status Footnote */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <div className="bg-[#111827]/80 rounded-xl p-3 border border-slate-800 flex items-center justify-between shadow-inner">
          <div className="flex items-center gap-2.5">
            <div className="relative flex items-center justify-center">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  systemStatus?.healthy ? 'bg-emerald-500' : 'bg-red-500'
                }`}
              />
              {systemStatus?.healthy && (
                <span className="absolute w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping opacity-75" />
              )}
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-200 leading-none">
                {systemStatus?.healthy ? 'Engine Online' : 'Engine Offline'}
              </p>
              <p className="text-[10px] text-slate-500 font-mono mt-0.5">Port 8000 • Live</p>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
            v1.0.0
          </span>
        </div>
      </div>
    </aside>
  );
}
