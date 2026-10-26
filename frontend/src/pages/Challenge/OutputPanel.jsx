import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  Terminal, 
  CheckCircle2, 
  XCircle, 
  AlertOctagon, 
  Clock, 
  Eye, 
  Loader2, 
  ChevronDown, 
  ChevronUp,
  Code2,
  Lock
} from 'lucide-react';
import { deriveComprehensiveTestCases } from '../../components/TestCasesSection';

export default function OutputPanel({ 
  challenge, 
  userCode = '', 
  testCases = [], 
  runOutput = '', 
  isRunning = false, 
  compileError = '', 
  files = [], 
  technology = '',
  lastRunResult = null
}) {
  const isFrontendTech = ['react', 'css', 'html', 'styling', 'frontend design', 'web', 'javascript'].includes((technology || '').toLowerCase());
  
  // Default tab: 'testcase' if not run, or 'testresult' if run finished
  const [activeTab, setActiveTab] = useState('testcase');
  const [selectedCaseIdx, setSelectedCaseIdx] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showStdout, setShowStdout] = useState(false);

  // Active cases: prioritize evaluated results from lastRunResult if available
  const activeCasesSource = (lastRunResult?.testCases || lastRunResult?.test_results || testCases || []);
  const comprehensiveCases = deriveComprehensiveTestCases(activeCasesSource, challenge?.title, technology);

  // When run completes, automatically switch to Test Result tab
  useEffect(() => {
    if (lastRunResult || runOutput || compileError) {
      setActiveTab('testresult');
      setIsCollapsed(false);
    }
  }, [lastRunResult, runOutput, compileError]);

  const passedCount = comprehensiveCases.filter(t => t.passed === true).length;
  const totalCount = comprehensiveCases.length;
  const isAllPassed = totalCount > 0 && passedCount === totalCount;
  const hasRun = lastRunResult !== null || runOutput.length > 0 || compileError.length > 0 || (comprehensiveCases.length > 0 && comprehensiveCases.some(t => t.passed !== undefined));

  const selectedCase = comprehensiveCases[selectedCaseIdx] || comprehensiveCases[0] || null;

  // Build iframe for live frontend preview
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
              body { font-family: system-ui, -apple-system, sans-serif; padding: 16px; background: #0D1117; color: #E6EDF3; margin: 0; }
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
                document.body.innerHTML += '<div style="color: #f85149; padding: 12px; background: rgba(248,81,73,0.1); border: 1px solid #f85149; border-radius: 4px; font-family: monospace; font-size: 12px;">Preview Error: ' + err.message + '</div>';
              }
            </script>
          </body>
        </html>
      `;
    } catch (e) {
      return `<div style="color: #f85149; padding: 12px;">Preview render failed.</div>`;
    }
  };

  return (
    <div className={`flex flex-col ${isCollapsed ? 'h-9 overflow-hidden' : 'h-64 lg:h-72'} shrink-0 bg-white dark:bg-[#0D1117] text-slate-800 dark:text-[#E6EDF3] font-sans border-t border-slate-200 dark:border-[#30363D] transition-all duration-150 select-none`}>
      {/* 1. Panel Tabs Header */}
      <div className="flex items-center justify-between px-3 bg-slate-50 dark:bg-[#161B22] border-b border-slate-200 dark:border-[#30363D] h-9 shrink-0">
        <div className="flex items-center gap-1">
          {/* Testcase Tab */}
          <button
            onClick={() => { setActiveTab('testcase'); setIsCollapsed(false); }}
            className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded transition-colors ${
              activeTab === 'testcase'
                ? 'bg-white dark:bg-[#21262D] text-cyan-600 dark:text-cyan-400 border border-slate-200 dark:border-transparent shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3]'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5" />
            <span>Testcases</span>
          </button>

          {/* Test Result Tab */}
          <button
            onClick={() => { setActiveTab('testresult'); setIsCollapsed(false); }}
            className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded transition-colors ${
              activeTab === 'testresult'
                ? 'bg-white dark:bg-[#21262D] text-emerald-600 dark:text-emerald-400 border border-slate-200 dark:border-transparent shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3]'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Test Results</span>
            {hasRun && (
              <span className={`w-1.5 h-1.5 rounded-full ${isAllPassed ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            )}
          </button>

          {/* Frontend Preview */}
          {isFrontendTech && (
            <button
              onClick={() => { setActiveTab('preview'); setIsCollapsed(false); }}
              className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded transition-colors ${
                activeTab === 'preview'
                  ? 'bg-white dark:bg-[#21262D] text-indigo-600 dark:text-indigo-400 border border-slate-200 dark:border-transparent shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3]'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
          )}
        </div>

        {/* Right side: collapse toggle */}
        <div className="flex items-center gap-2">
          {isRunning && (
            <div className="flex items-center gap-1.5 text-cyan-400 text-[11px] font-mono">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Evaluating...</span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 hover:bg-slate-200 dark:hover:bg-[#21262D] rounded text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3] transition-colors"
            title={isCollapsed ? 'Expand panel' : 'Collapse panel'}
          >
            {isCollapsed ? <ChevronUp className="w-4 h-4 text-cyan-400" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* 2. Main Panel Content */}
      <div className="flex-1 overflow-y-auto p-4 select-text">
        {/* Compile / Execution Error Banner */}
        {compileError && (
          <div className="p-3 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-500/30 rounded text-rose-800 dark:text-rose-300 text-xs font-mono mb-4">
            <div className="flex items-center gap-2 font-bold mb-1 text-rose-700 dark:text-rose-400">
              <AlertOctagon className="w-4 h-4" />
              <span>Execution / Syntax Error</span>
            </div>
            <pre className="whitespace-pre-wrap text-[11px] leading-relaxed">{compileError}</pre>
          </div>
        )}

        {/* TAB 1: TESTCASE */}
        {activeTab === 'testcase' && (
          <div className="space-y-4">
            {/* Case selector pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
              {comprehensiveCases.map((tc, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedCaseIdx(idx)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono rounded transition-colors ${
                    selectedCaseIdx === idx
                      ? 'bg-white dark:bg-[#21262D] text-slate-900 dark:text-[#E6EDF3] border border-slate-300 dark:border-[#30363D] shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3] hover:bg-slate-100 dark:hover:bg-[#161B22]'
                  }`}
                >
                  <span>Case {idx + 1}</span>
                  {tc.hidden && (
                    <Lock className="w-3 h-3 text-slate-400" />
                  )}
                </button>
              ))}
            </div>

            {/* Selected Case Details */}
            {selectedCase && (
              <div className="space-y-3 font-sans">
                <div className="flex items-center gap-2">
                  {selectedCase.hidden ? (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1">
                      <Lock className="w-3 h-3" />
                      <span>Hidden Evaluation Test</span>
                    </span>
                  ) : (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      <span>Visible Sample Test</span>
                    </span>
                  )}
                </div>

                {selectedCase.input && (
                  <div className="space-y-1">
                    <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">
                      Input
                    </span>
                    <div className="p-2.5 rounded bg-slate-50 dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] text-xs text-cyan-700 dark:text-cyan-300 font-mono whitespace-pre-wrap">
                      {selectedCase.input}
                    </div>
                  </div>
                )}

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">
                    Scope
                  </span>
                  <div className="p-2.5 rounded bg-slate-50 dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] text-xs text-slate-700 dark:text-slate-300 font-sans">
                    {selectedCase.hidden
                      ? 'Hidden evaluation test. Validates boundary conditions and edge cases during execution.'
                      : 'Sample case verification. Validates core functional requirements against sample input data.'}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: TEST RESULT */}
        {activeTab === 'testresult' && (
          <div className="h-full">
            {!hasRun && !isRunning ? (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 py-10 space-y-2">
                <Code2 className="w-7 h-7 opacity-40 text-slate-400" />
                <p className="text-xs text-slate-400 font-mono">Run your code to execute assertions</p>
              </div>
            ) : isRunning ? (
              <div className="flex flex-col items-center justify-center h-full text-cyan-400 py-10 space-y-2">
                <Loader2 className="w-6 h-6 animate-spin" />
                <p className="text-xs text-slate-300 font-mono">Evaluating against test assertions...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Result Status Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-[#30363D]">
                  <div className="flex items-center gap-3">
                    <span className={`text-sm font-bold flex items-center gap-2 ${
                      isAllPassed ? 'text-emerald-400' : 'text-rose-700 dark:text-rose-400'
                    }`}>
                      {isAllPassed ? (
                        <>
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                          <span>Accepted</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-4 h-4 text-rose-700 dark:text-rose-400" />
                          <span>Wrong Answer</span>
                        </>
                      )}
                    </span>

                    <span className="text-xs font-mono text-slate-600 dark:text-slate-400 flex items-center gap-1 bg-slate-100 dark:bg-[#161B22] px-2 py-0.5 rounded border border-slate-200 dark:border-[#30363D]">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span>Runtime: {lastRunResult?.executionTime ? `${Math.round(lastRunResult.executionTime * 1000)} ms` : '5 ms'}</span>
                    </span>
                  </div>

                  <span className="text-xs font-mono text-slate-700 dark:text-slate-300">
                    {passedCount} / {totalCount} test cases passed
                  </span>
                </div>

                {/* Scannable Case Selector */}
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                  {comprehensiveCases.map((tc, idx) => {
                    const isCasePassed = tc.passed === true;
                    const isCaseFailed = tc.passed === false;
                    return (
                      <button
                        key={idx}
                        onClick={() => setSelectedCaseIdx(idx)}
                        className={`flex items-center gap-2 px-2.5 py-1 text-xs font-mono rounded border transition-colors shrink-0 ${
                          selectedCaseIdx === idx
                            ? 'bg-white dark:bg-[#21262D] text-slate-900 dark:text-[#E6EDF3] border-slate-300 dark:border-[#30363D] shadow-sm'
                            : 'bg-transparent text-slate-600 dark:text-slate-400 border-transparent hover:bg-slate-100 dark:hover:bg-[#161B22]'
                        }`}
                      >
                        <span className={`w-2 h-2 rounded-full shrink-0 ${
                          isCasePassed ? 'bg-emerald-400' : isCaseFailed ? 'bg-rose-400' : 'bg-slate-500'
                        }`} />
                        <span>Case {idx + 1} — {isCasePassed ? 'Passed' : isCaseFailed ? 'Failed' : 'Pending'}</span>
                        {tc.hidden && (
                          <Lock className="w-2.5 h-2.5 text-slate-400 ml-0.5" />
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Selected Case Inspection */}
                {selectedCase && (
                  <div className="space-y-3 font-sans text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900 dark:text-slate-200 text-sm font-mono">
                        Test Case {selectedCaseIdx + 1}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider ${
                        selectedCase.passed === true
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : selectedCase.passed === false
                          ? 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/30'
                          : 'bg-slate-100 dark:bg-[#21262D] text-slate-600 dark:text-slate-400'
                      }`}>
                        {selectedCase.passed === true ? 'PASSED' : selectedCase.passed === false ? 'FAILED' : 'PENDING'}
                      </span>
                    </div>

                    {selectedCase.passed === true && (
                      <div className="p-3 rounded bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-300 font-mono text-xs">
                        All assertions for Test Case {selectedCaseIdx + 1} matched expected output.
                      </div>
                    )}

                    {selectedCase.passed === false && (
                      <div className="p-3 rounded bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-300 space-y-1.5 font-mono text-xs">
                        <div className="font-semibold text-rose-700 dark:text-rose-400">
                          Evaluator Output:
                        </div>
                        <div className="text-slate-800 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                          {selectedCase.hint || selectedCase.error || "The result does not match the required behavior."}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Collapsible Stdout / Console Drawer */}
                {runOutput && (
                  <div className="pt-2 border-t border-slate-200 dark:border-[#30363D]">
                    <button
                      onClick={() => setShowStdout(!showStdout)}
                      className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 font-mono"
                    >
                      <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Console Logs / Traceback</span>
                      <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showStdout ? 'rotate-180' : ''}`} />
                    </button>

                    {showStdout && (
                      <pre className="mt-2 p-3 bg-slate-50 dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] rounded text-[11px] font-mono text-slate-800 dark:text-slate-300 whitespace-pre-wrap leading-relaxed max-h-40 overflow-y-auto">
                        {runOutput}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: LIVE PREVIEW (Frontend) */}
        {activeTab === 'preview' && isFrontendTech && (
          <div className="w-full h-full min-h-[180px] bg-white dark:bg-[#161B22] rounded overflow-hidden border border-slate-200 dark:border-[#30363D]">
            <iframe
              title="Live Preview"
              srcDoc={buildPreviewHtml()}
              sandbox="allow-scripts allow-modals"
              className="w-full h-full border-0"
            />
          </div>
        )}
      </div>
    </div>
  );
}
