import React from 'react';
import { ChevronRight, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Breadcrumbs({ paths = [] }) {
  return (
    <nav className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400 py-2">
      <Link 
        to="/" 
        className="flex items-center gap-1 text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors"
      >
        <Home className="w-3.5 h-3.5" />
      </Link>
      {paths.map((p, index) => {
        const isLast = index === paths.length - 1;
        return (
          <React.Fragment key={index}>
            <ChevronRight className="w-3 h-3 text-slate-400 dark:text-slate-600" />
            {isLast ? (
              <span className="text-slate-900 dark:text-slate-200 font-semibold truncate max-w-[200px]">{p.name}</span>
            ) : (
              <Link 
                to={p.url || '#'} 
                className="text-slate-600 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors truncate max-w-[200px]"
              >
                {p.name}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
