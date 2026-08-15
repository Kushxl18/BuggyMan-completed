import React from 'react';

export default function ProgressBar({ value = 0, max = 100, color = 'blue', showText = false, size = 'md' }) {
  const percentage = Math.min(100, Math.max(0, Math.round((value / max) * 100)));

  const colorVariants = {
    blue: 'from-blue-600 to-cyan-500 shadow-glow-blue',
    cyan: 'from-cyan-500 to-sky-400 shadow-glow-cyan',
    indigo: 'from-blue-600 to-cyan-500 shadow-glow-blue',
    violet: 'from-sky-500 to-blue-600 shadow-glow-blue',
    emerald: 'from-emerald-500 to-teal-400 shadow-glow-emerald',
    rose: 'from-rose-500 to-pink-500 shadow-glow-rose',
    amber: 'from-amber-500 to-yellow-400 shadow-glow-amber',
  };

  const sizeVariants = {
    sm: 'h-1',
    md: 'h-2.5',
    lg: 'h-4',
  };

  return (
    <div className="w-full">
      {showText && (
        <div className="flex justify-between items-center text-xs font-semibold text-slate-400 mb-1.5">
          <span>Progress</span>
          <span className="text-slate-200">{percentage}%</span>
        </div>
      )}
      <div className={`w-full bg-slate-800/80 rounded-full overflow-hidden ${sizeVariants[size]}`}>
        <div
          className={`h-full bg-gradient-to-r ${colorVariants[color] || colorVariants.blue} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
