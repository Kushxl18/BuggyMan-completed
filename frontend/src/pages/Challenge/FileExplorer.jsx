import React from 'react';
import { FileCode, FolderOpen, FileText } from 'lucide-react';

export default function FileExplorer({ files = [], activeFile, onSelectFile }) {
  return (
    <div className="w-60 bg-[var(--bg-card)] border-r border-[var(--border-color)] flex flex-col h-full select-none">
      <div className="p-4 border-b border-[var(--border-color)] flex items-center gap-2">
        <FolderOpen className="w-4 h-4 text-brand-indigo" />
        <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">Workspace Files</span>
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
                  ? 'bg-[var(--brand-cyan-bg)] border-l-2 border-[var(--brand-cyan)] text-[var(--text-primary)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
              }`}
            >
              {isJsx ? (
                <FileCode className={`w-4 h-4 ${isActive ? 'text-[var(--brand-cyan)]' : 'text-[var(--text-muted)]'}`} />
              ) : (
                <FileText className="w-4 h-4 text-[var(--text-muted)]" />
              )}
              <span className="truncate">{file.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
