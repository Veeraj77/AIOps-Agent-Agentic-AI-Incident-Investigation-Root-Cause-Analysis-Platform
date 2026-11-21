import React from 'react';

export default function StatCard({
  title,
  value,
  icon: Icon,
  change,
  trend = 'neutral',
  subtitle,
  color = 'indigo',
}) {
  const colorMap = {
    indigo: {
      badge: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30 shadow-glow-sm shadow-indigo-500/20',
      gradient: 'from-indigo-950/20 to-transparent',
      border: 'hover:border-indigo-500/40',
    },
    red: {
      badge: 'text-rose-400 bg-rose-500/10 border-rose-500/30 shadow-glow-red shadow-rose-500/20',
      gradient: 'from-rose-950/20 to-transparent',
      border: 'hover:border-rose-500/40',
    },
    orange: {
      badge: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
      gradient: 'from-orange-950/20 to-transparent',
      border: 'hover:border-orange-500/40',
    },
    amber: {
      badge: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      gradient: 'from-amber-950/20 to-transparent',
      border: 'hover:border-amber-500/40',
    },
    emerald: {
      badge: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 shadow-glow-emerald shadow-emerald-500/20',
      gradient: 'from-emerald-950/20 to-transparent',
      border: 'hover:border-emerald-500/40',
    },
    blue: {
      badge: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
      gradient: 'from-blue-950/20 to-transparent',
      border: 'hover:border-blue-500/40',
    },
  };

  const style = colorMap[color] || colorMap.indigo;

  return (
    <div
      className={`glass-panel rounded-2xl p-5 card-hover bg-gradient-to-b ${style.gradient} border border-slate-800/80 ${style.border} relative overflow-hidden group`}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border transition-transform duration-300 group-hover:scale-110 ${style.badge}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-4 flex items-baseline gap-2.5">
        <div className="text-3xl font-extrabold text-white tracking-tight font-sans">
          {value}
        </div>
        {change && (
          <span
            className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
              trend === 'up'
                ? 'text-rose-400 bg-rose-500/10 border border-rose-500/20'
                : trend === 'down'
                ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
                : 'text-slate-400 bg-slate-800'
            }`}
          >
            {change}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-slate-400 font-medium leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}
