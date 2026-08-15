import React from 'react';
import { SearchX } from 'lucide-react';

export default function EmptyState({ 
  icon: Icon = SearchX, 
  title = 'No Items Found', 
  description = 'No results matched your search query or filter criteria.', 
  actionLabel, 
  onAction 
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-slate-900/40 border border-slate-800/80 rounded-2xl my-6 backdrop-blur-sm">
      <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 mb-4 shadow-glow-blue">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-bold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-md mb-6">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg transition-all duration-150 active:scale-95"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
