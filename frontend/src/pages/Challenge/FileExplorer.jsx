import React from 'react';
import { FileCode, FolderOpen, FileText } from 'lucide-react';

export default function FileExplorer({ files = [], activeFile, onSelectFile }) {
  return (
    <div className="w-60 bg-slate-900 border-r border-slate-800 flex flex-col h-full select-none">
      <div className="p-4 border-b border-slate-800/80 flex items-center gap-2">
        <FolderOpen className="w-4 h-4 text-brand-indigo" />
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Workspace Files</span>
      </div>

      <div className="flex-1 overflow-y-auto p-2.5 space-y-1">
        {files.map((file) => {
          const isActive = file.name === activeFile?.name;
          const isJsx = file.name.endsWith('.jsx') || file.name.endsWith('.js');
          
          return (
            <button
              key={file.name}
              onClick={() => onSelectFile(file)}
              className={`flex items-center gap-2.5 w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-brand-indigo/10 border-l-2 border-brand-indigo text-slate-100'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              {isJsx ? (
                <FileCode className={`w-4 h-4 ${isActive ? 'text-brand-indigo' : 'text-slate-500'}`} />
              ) : (
                <FileText className="w-4 h-4 text-slate-500" />
              )}
              <span className="truncate">{file.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
