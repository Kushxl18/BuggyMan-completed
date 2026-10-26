import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

export default function ConfirmationDialog({ 
  isOpen, 
  title, 
  message, 
  onConfirm, 
  onCancel, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  type = 'danger' 
}) {
  if (!isOpen) return null;

  const btnColors = {
    danger: 'bg-brand-rose hover:bg-rose-600 shadow-glow-rose',
    primary: 'bg-brand-indigo hover:bg-indigo-600 shadow-glow-indigo',
    success: 'bg-brand-emerald hover:bg-emerald-600 shadow-glow-emerald'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm"
        onClick={onCancel}
      />
      
      {/* Dialog container */}
      <div className="relative w-full max-w-md glass-panel rounded-2xl p-6 overflow-hidden animate-slide-up shadow-2xl border border-slate-200 dark:border-slate-800 z-10">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-xl bg-slate-100 dark:bg-slate-950/80 border ${type === 'danger' ? 'border-brand-rose/30 text-brand-rose' : 'border-brand-indigo/30 text-brand-indigo'}`}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-heading font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
          </div>
          <button 
            onClick={onCancel}
            className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-slate-700 dark:text-slate-300 text-sm mb-6 leading-relaxed">
          {message}
        </p>

        <div className="flex justify-end gap-3">
          <button 
            onClick={onCancel}
            className="button-secondary px-4 py-2 text-sm"
          >
            {cancelText}
          </button>
          <button 
            onClick={onConfirm}
            className={`${btnColors[type]} text-white text-sm font-medium px-4 py-2 rounded-xl active:scale-95 transition-all duration-150`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
