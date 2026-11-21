import React from 'react';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

export default function SeverityBadge({ severity = 'INFO', size = 'md' }) {
  const norm = (severity || 'INFO').toUpperCase();

  const config = {
    CRITICAL: {
      bg: 'bg-rose-500/15 border-rose-500/40 text-rose-300 shadow-glow-red shadow-rose-500/20',
      dot: 'bg-rose-500',
      ping: true,
      icon: AlertOctagon,
      label: 'CRITICAL',
    },
    HIGH: {
      bg: 'bg-orange-500/15 border-orange-500/40 text-orange-300',
      dot: 'bg-orange-500',
      ping: true,
      icon: AlertTriangle,
      label: 'HIGH',
    },
    MEDIUM: {
      bg: 'bg-amber-500/15 border-amber-500/40 text-amber-300',
      dot: 'bg-amber-500',
      ping: false,
      icon: AlertTriangle,
      label: 'MEDIUM',
    },
    LOW: {
      bg: 'bg-blue-500/15 border-blue-500/40 text-blue-300',
      dot: 'bg-blue-500',
      ping: false,
      icon: Info,
      label: 'LOW',
    },
    INFO: {
      bg: 'bg-slate-500/15 border-slate-500/40 text-slate-300',
      dot: 'bg-slate-400',
      ping: false,
      icon: CheckCircle2,
      label: 'INFO',
    },
  };

  const current = config[norm] || config.INFO;
  const Icon = current.icon;

  const sizeClasses = {
    sm: 'text-[10px] font-bold px-2 py-0.5 gap-1.5',
    md: 'text-xs font-bold px-3 py-1 gap-1.5',
    lg: 'text-xs font-extrabold px-3.5 py-1.5 gap-2',
  }[size] || 'text-xs font-bold px-3 py-1 gap-1.5';

  return (
    <span
      className={`inline-flex items-center rounded-lg border tracking-wider font-mono uppercase backdrop-blur-md ${current.bg} ${sizeClasses}`}
    >
      <span className="relative flex items-center justify-center">
        <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`} />
        {current.ping && (
          <span className={`absolute w-1.5 h-1.5 rounded-full ${current.dot} animate-ping opacity-75`} />
        )}
      </span>
      <Icon className="w-3.5 h-3.5" />
      <span>{current.label}</span>
    </span>
  );
}
