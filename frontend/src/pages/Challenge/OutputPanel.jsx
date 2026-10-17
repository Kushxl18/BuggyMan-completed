import React, { useState } from 'react';
import { Terminal, CheckCircle2, XCircle, AlertOctagon, PlayCircle, Eye, Monitor, Sparkles, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { challengeService } from '../../services/challengeService';
import TestCasesSection from '../../components/TestCasesSection';

export default function OutputPanel({ challenge, userCode = '', testCases = [], runOutput = '', isRunning = false, compileError = '', files = [], technology = '' }) {
  const isFrontendTech = ['react', 'css', 'html', 'styling', 'frontend design', 'web', 'javascript'].includes((technology || '').toLowerCase());
  const [activeTab, setActiveTab] = useState(isFrontendTech ? 'preview' : 'console');
  const [feedback, setFeedback] = useState(null);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const passedTestsCount = testCases.filter(t => t.passed).length;

  const handleFetchFeedback = async () => {
    if (!challenge) return;
    try {
      setLoadingFeedback(true);
      const res = await challengeService.getFeedback(challenge.id, {
        code: userCode,
        files: files,
        testResults: testCases,
        stdout: runOutput,
        stderr: compileError,
        error: compileError
      });
      if (res) {
        setFeedback(res);
      }
    } catch (err) {
      console.error('Failed to fetch AI feedback:', err);
    } finally {
      setLoadingFeedback(false);
    }
  };

  const buildPreviewHtml = () => {
    try {
      const htmlFile = (files || []).find(f => (f?.name || '').endsWith('.html'));
      const cssFiles = (files || []).filter(f => (f?.name || '').endsWith('.css'));
      const jsFiles = (files || []).filter(f => (f?.name || '').endsWith('.js') || (f?.name || '').endsWith('.jsx'));

      const cssContent = cssFiles.map(f => f?.content || '').join('\n');
      let bodyContent = htmlFile ? (htmlFile.content || '') : '<div id="root"></div>';

      let scriptContent = '';
      jsFiles.forEach(f => {
        let cleanCode = (f?.content || '')
          .replace(/import\s+.*?from\s+['"].*?['"];?/g, '')
          .replace(/export\s+default\s+/g, '')
          .replace(/export\s+/g, '')
          .replace(/<\/script>/gi, '<\\/script>');
        scriptContent += cleanCode + '\n';
      });

      return `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
              body { font-family: system-ui, -apple-system, sans-serif; padding: 16px; background: #0f172a; color: #f8fafc; margin: 0; }
              ${cssContent}
            </style>
            <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
            <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
            <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
          </head>
          <body>
            ${bodyContent.includes('id="root"') ? bodyContent : '<div id="root"></div>' + bodyContent}
            <script type="text/babel">
              try {
                ${scriptContent}
                const rootEl = document.getElementById('root');
                if (rootEl && typeof React !== 'undefined' && typeof ReactDOM !== 'undefined') {
                  const compCandidate = typeof Counter !== 'undefined' ? Counter :
                                        typeof SignupForm !== 'undefined' ? SignupForm :
                                        typeof Navbar !== 'undefined' ? Navbar :
                                        typeof ActionButton !== 'undefined' ? ActionButton :
                                        typeof Avatar !== 'undefined' ? Avatar :
                                        typeof SearchInput !== 'undefined' ? SearchInput :
                                        typeof ThemeToggle !== 'undefined' ? ThemeToggle :
                                        typeof Modal !== 'undefined' ? Modal :
                                        typeof DataList !== 'undefined' ? DataList :
                                        typeof CardGrid !== 'undefined' ? CardGrid : null;
                  if (compCandidate) {
                    const root = ReactDOM.createRoot(rootEl);
                    root.render(React.createElement(compCandidate));
                  }
                }
              } catch (err) {
                console.error(err);
                document.body.innerHTML += '<div style="color: #f43f5e; padding: 12px; background: #881337; border-radius: 8px; font-family: monospace; font-size: 12px;">Preview Error: ' + err.message + '</div>';
              }
            </script>
          </body>
        </html>
      `;
    } catch (e) {
      return `<div style="color: #f43f5e; padding: 12px;">Preview render failed.</div>`;
    }
  };

  return (
    <div className={`flex flex-col ${isCollapsed ? 'h-9 overflow-hidden' : 'h-64'} shrink-0 bg-slate-950 text-slate-100 font-mono text-xs border-t border-slate-800 transition-all duration-200`}>
      <div className="flex items-center justify-between px-4 bg-slate-900 border-b border-slate-800 select-none h-9 shrink-0">
        <div className="flex items-center gap-1 overflow-x-auto">
          {isFrontendTech && (
            <button
              onClick={() => { setActiveTab('preview'); setIsCollapsed(false); }}
              className={`px-3 py-1.5 border-b-2 flex items-center gap-1.5 transition-all text-xs ${
                activeTab === 'preview' ? 'border-brand-violet text-brand-violet font-bold' : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Live Preview</span>
            </button>
          )}

          <button
            onClick={() => { setActiveTab('console'); setIsCollapsed(false); }}
            className={`px-3 py-1.5 border-b-2 flex items-center gap-1.5 transition-all text-xs ${
              activeTab === 'console' ? 'border-brand-cyan text-brand-cyan font-bold' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Terminal Console</span>
          </button>

          <button
            onClick={() => { setActiveTab('tests'); setIsCollapsed(false); }}
            className={`px-3 py-1.5 border-b-2 flex items-center gap-1.5 transition-all text-xs ${
              activeTab === 'tests' ? 'border-brand-indigo text-brand-indigo font-bold' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Test Results ({passedTestsCount}/{testCases.length})</span>
          </button>

          <button
            onClick={() => { setActiveTab('errors'); setIsCollapsed(false); }}
            className={`px-3 py-1.5 border-b-2 flex items-center gap-1.5 transition-all text-xs ${
              activeTab === 'errors' ? 'border-brand-rose text-brand-rose font-bold' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <AlertOctagon className="w-3.5 h-3.5" />
            <span>Errors {compileError && '(1)'}</span>
          </button>

          <button
            onClick={() => { setActiveTab('ai_feedback'); setIsCollapsed(false); if (!feedback) handleFetchFeedback(); }}
            className={`px-3 py-1.5 border-b-2 flex items-center gap-1.5 transition-all text-xs ${
              activeTab === 'ai_feedback' ? 'border-amber-400 text-amber-300 font-bold' : 'border-transparent text-slate-400 hover:text-amber-300'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>AI Feedback</span>
          </button>
        </div>

        <div className="flex items-center gap-3">
          {isRunning && (
            <div className="flex items-center gap-2 text-brand-cyan animate-pulse text-[10px]">
              <PlayCircle className="w-3.5 h-3.5" />
              <span>Evaluating...</span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1 text-[11px]"
            title={isCollapsed ? "Expand Terminal Panel" : "Collapse Terminal Panel"}
          >
            {isCollapsed ? <ChevronUp className="w-4 h-4 text-cyan-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            <span className="text-[10px] hidden sm:inline text-slate-400">{isCollapsed ? "Expand" : "Collapse"}</span>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden relative">
        {activeTab === 'preview' && (
          <div className="w-full h-full bg-slate-900 relative">
            <iframe
              title="Frontend Live Preview"
              srcDoc={buildPreviewHtml()}
              sandbox="allow-scripts allow-modals"
              className="w-full h-full border-0"
            />
          </div>
        )}

        {activeTab === 'console' && (
          <div className="p-4 overflow-y-auto h-full space-y-2">
            {runOutput ? (
              <pre className="whitespace-pre-wrap leading-relaxed text-slate-300 font-mono text-[11px]">
                {runOutput}
              </pre>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 py-8">
                <Terminal className="w-8 h-8 mb-2 opacity-50" />
                <p>Run your code to see terminal execution logs.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'tests' && (
          <div className="p-4 overflow-y-auto h-full">
            <TestCasesSection 
              testCases={testCases} 
              challengeTitle={challenge?.title} 
              technology={technology || challenge?.technology} 
              showHeader={false} 
            />
          </div>
        )}

        {activeTab === 'errors' && (
          <div className="p-4 overflow-y-auto h-full">
            {compileError ? (
              <div className="p-4 bg-rose-950/25 border border-brand-rose/20 rounded-xl text-brand-rose leading-relaxed">
                <h4 className="font-bold mb-1.5 uppercase text-[10px] tracking-wider font-sans">Compilation Traceback:</h4>
                <pre className="whitespace-pre-wrap font-mono">{compileError}</pre>
              </div>
            ) : (
              <p className="text-slate-500 italic font-sans">No compilation errors detected. Clean build.</p>
            )}
          </div>
        )}

        {activeTab === 'ai_feedback' && (
          <div className="p-4 overflow-y-auto h-full space-y-4">
            <div className="flex justify-between items-center bg-slate-900 p-3 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-300" />
                <span className="font-bold text-slate-200">AI Code Review & Debugging Feedback</span>
              </div>
              <button
                onClick={handleFetchFeedback}
                disabled={loadingFeedback}
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-[11px] flex items-center gap-1.5 transition-all disabled:opacity-50"
              >
                {loadingFeedback ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Analyze Code'}
              </button>
            </div>

            {feedback ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400 font-sans">What Appears Wrong</span>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{feedback.whatIsWrong}</p>
                </div>

                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 font-sans">Why It Is Wrong</span>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{feedback.whyItIsWrong}</p>
                </div>

                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 font-sans">Concept To Understand</span>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{feedback.conceptToUnderstand}</p>
                </div>

                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 font-sans">Suggested Direction</span>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{feedback.suggestedDirection}</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500">
                <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50 text-amber-300" />
                <p className="text-xs text-slate-400">Click "Analyze Code" to generate structured AI feedback on your solution.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
