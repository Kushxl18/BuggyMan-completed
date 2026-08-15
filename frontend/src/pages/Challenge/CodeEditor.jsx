import React from 'react';
import Editor from '@monaco-editor/react';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CodeEditor({ file, onChange, theme = 'dark', fontSize = 14 }) {
  if (!file) {
    return (
      <div className="flex-1 flex items-center justify-center bg-slate-950 text-slate-500">
        Select a file to begin coding
      </div>
    );
  }

  // Deduce language type based on extension
  const getLanguage = (filename) => {
    if (filename.endsWith('.jsx')) return 'javascript';
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.css')) return 'css';
    if (filename.endsWith('.json')) return 'json';
    return 'javascript';
  };

  return (
    <div className="flex-1 h-full bg-slate-950 relative">
      <Editor
        height="100%"
        language={getLanguage(file.name)}
        value={file.content}
        onChange={onChange}
        theme={theme === 'dark' ? 'vs-dark' : 'light'}
        loading={<LoadingSpinner className="absolute inset-0 bg-slate-950" />}
        options={{
          fontSize: fontSize,
          minimap: { enabled: false },
          automaticLayout: true,
          fontFamily: 'Fira Code, Courier New, monospace',
          scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            useShadows: false,
            verticalScrollbarSize: 6,
            horizontalScrollbarSize: 6
          },
          lineNumbersMinChars: 3,
          padding: { top: 12, bottom: 12 }
        }}
      />
    </div>
  );
}
