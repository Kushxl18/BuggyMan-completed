import React, { useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function Toast({ message, type = 'success', onClose, duration = 4000 }) {
  useEffect(() => {
    if (duration) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const config = {
    success: {
      icon: <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />,
      border: 'border-emerald-500/30 dark:border-emerald-500/40',
      bg: 'bg-white dark:bg-slate-900',
      accent: 'bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400'
    },
    error: {
      icon: <AlertCircle className="w-5 h-5 text-rose-500 shrink-0" />,
      border: 'border-rose-500/30 dark:border-rose-500/40',
      bg: 'bg-white dark:bg-slate-900',
      accent: 'bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400'
    },
    warning: {
      icon: <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />,
      border: 'border-amber-500/30 dark:border-amber-500/40',
      bg: 'bg-white dark:bg-slate-900',
      accent: 'bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400'
    },
    info: {
      icon: <Info className="w-5 h-5 text-cyan-500 shrink-0" />,
      border: 'border-cyan-500/30 dark:border-cyan-500/40',
      bg: 'bg-white dark:bg-slate-900',
      accent: 'bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400'
    }
  };

  const current = config[type] || config.info;

  return (
    <div className={`flex items-center gap-3 px-4 py-3.5 rounded-2xl border ${current.border} ${current.bg} shadow-xl dark:shadow-2xl shadow-slate-900/10 dark:shadow-black/40 animate-slide-up max-w-sm pointer-events-auto backdrop-blur-md`}>
      <div className={`p-1 rounded-lg ${current.accent}`}>
        {current.icon}
      </div>
      <div className="flex-1 min-w-0 pr-1">
        <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 leading-snug break-words">
          {message}
        </p>
      </div>
      <button 
        onClick={onClose}
        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors shrink-0"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
