import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

export default function ErrorState({ 
  title = 'Something Went Wrong', 
  message = 'Failed to load data. Please check your network connection and try again.', 
  onRetry 
}) {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center bg-rose-950/20 border border-rose-800/40 rounded-2xl my-6 backdrop-blur-sm">
      <div className="p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 mb-3 shadow-glow-rose">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h3 className="text-base font-bold text-rose-200 mb-1">{title}</h3>
      <p className="text-xs text-rose-300/80 max-w-md mb-5">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-md transition-all active:scale-95"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
}
