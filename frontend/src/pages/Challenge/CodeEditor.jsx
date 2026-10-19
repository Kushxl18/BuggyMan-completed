import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function CodeEditor({ file, onChange, theme = 'dark', fontSize = 14 }) {
  const editorRef = useRef(null);
  const containerRef = useRef(null);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
    setTimeout(() => {
      try {
        editor.layout();
      } catch (e) {}
    }, 50);
  };

  // ResizeObserver forces Monaco to layout when container flex size shifts
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(() => {
      if (editorRef.current) {
        try {
          editorRef.current.layout();
        } catch (e) {}
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  // Force layout when file or theme changes
  useEffect(() => {
    if (editorRef.current) {
      try {
        editorRef.current.layout();
      } catch (e) {}
    }
  }, [file?.name, file?.content, theme]);

  if (!file) {
    return (
      <div className="w-full h-full flex-1 flex flex-col bg-[var(--bg-main)] relative min-h-[300px] items-center justify-center text-[var(--text-muted)]">
        Select a file to begin coding
      </div>
    );
  }

  // Deduce language type based on extension
  const getLanguage = (filename = '') => {
    if (!filename) return 'javascript';
    const lower = filename.toLowerCase();
    if (lower.endsWith('.jsx') || lower.endsWith('.js') || lower.endsWith('.tsx') || lower.endsWith('.ts')) return 'javascript';
    if (lower.endsWith('.py')) return 'python';
    if (lower.endsWith('.css')) return 'css';
    if (lower.endsWith('.sql')) return 'sql';
    if (lower.endsWith('.html') || lower.endsWith('.htm')) return 'html';
    if (lower.endsWith('.json')) return 'json';
    return 'javascript';
  };

  return (
    <div ref={containerRef} className="w-full h-full flex-1 flex flex-col bg-[var(--bg-main)] relative min-h-[300px]">
      <Editor
        height="100%"
        width="100%"
        language={getLanguage(file?.name)}
        value={file?.content || ''}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme={theme === 'dark' ? 'vs-dark' : 'light'}
        loading={<LoadingSpinner className="absolute inset-0 bg-[var(--bg-main)]" />}
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
