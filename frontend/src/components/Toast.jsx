import React, { useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function Toast({ message, type = 'success', onClose, duration = 4000 }) {
  useEffect(() => {
    if (duration) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-brand-emerald" />,
    error: <AlertCircle className="w-5 h-5 text-brand-rose" />,
    warning: <AlertTriangle className="w-5 h-5 text-brand-amber" />,
    info: <Info className="w-5 h-5 text-brand-indigo" />
  };

  const borderColors = {
    success: 'border-brand-emerald/35 bg-emerald-950/20',
    error: 'border-brand-rose/35 bg-rose-950/20',
    warning: 'border-brand-amber/35 bg-amber-950/20',
    info: 'border-brand-indigo/35 bg-indigo-950/20'
  };

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl border glass-panel ${borderColors[type]} animate-slide-up shadow-lg max-w-sm pointer-events-auto`}>
      {icons[type]}
      <div className="flex-1">
        <p className="text-sm font-medium text-slate-100">{message}</p>
      </div>
      <button 
        onClick={onClose}
        className="p-1 hover:bg-slate-800/60 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
