import React, { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  Terminal, 
  CheckCircle2, 
  XCircle, 
  AlertOctagon, 
  Clock, 
  Eye, 
  Sparkles, 
  Loader2, 
  ChevronDown, 
  ChevronUp,
  Code2,
  Check,
  X
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

  // Derive structured test cases
  const comprehensiveCases = deriveComprehensiveTestCases(testCases, challenge?.title, technology);

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
  const hasRun = lastRunResult !== null || runOutput.length > 0 || compileError.length > 0 || (testCases.length > 0 && testCases.some(t => t.passed !== undefined));

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
    <div className={`flex flex-col ${isCollapsed ? 'h-9 overflow-hidden' : 'h-64 lg:h-72'} shrink-0 bg-slate-950 text-slate-100 font-sans border-t border-slate-800 transition-all duration-200 select-none`}>
      {/* 1. LeetCode Style Panel Tabs Header */}
      <div className="flex items-center justify-between px-3 bg-slate-900 border-b border-slate-800 h-9 shrink-0">
        <div className="flex items-center gap-1">
          {/* Testcase Tab */}
          <button
            onClick={() => { setActiveTab('testcase'); setIsCollapsed(false); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'testcase'
                ? 'bg-slate-800 text-cyan-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5 text-cyan-400" />
            <span>Testcase</span>
          </button>

          {/* Test Result Tab */}
          <button
            onClick={() => { setActiveTab('testresult'); setIsCollapsed(false); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'testresult'
                ? 'bg-slate-800 text-emerald-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <span className="font-mono text-emerald-400">{'>_'}</span>
            <span>Test Result</span>
            {hasRun && (
              <span className={`w-2 h-2 rounded-full ${isAllPassed ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            )}
          </button>

          {/* Frontend Preview (if applicable) */}
          {isFrontendTech && (
            <button
              onClick={() => { setActiveTab('preview'); setIsCollapsed(false); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                activeTab === 'preview'
                  ? 'bg-slate-800 text-indigo-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <Eye className="w-3.5 h-3.5 text-indigo-400" />
              <span>Preview</span>
            </button>
          )}
        </div>

        {/* Right side: collapse toggle */}
        <div className="flex items-center gap-2">
          {isRunning && (
            <div className="flex items-center gap-1.5 text-cyan-400 text-[11px] animate-pulse">
              <Loader2 className="w-3 h-3 animate-spin" />
              <span>Running...</span>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
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
          <div className="p-3 bg-rose-950/30 border border-rose-500/40 rounded-xl text-rose-300 text-xs font-mono mb-4">
            <div className="flex items-center gap-2 font-bold mb-1 text-rose-400">
              <AlertOctagon className="w-4 h-4" />
              <span>Execution / Syntax Error</span>
            </div>
            <pre className="whitespace-pre-wrap text-[11px] leading-relaxed">{compileError}</pre>
          </div>
        )}

        {/* TAB 1: TESTCASE (Input Cases 1, 2, 3) */}
        {activeTab === 'testcase' && (
          <div className="space-y-4">
            {/* Case selector pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              {comprehensiveCases.map((tc, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedCaseIdx(idx)}
                  className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg border transition-all ${
                    selectedCaseIdx === idx
                      ? 'bg-slate-800 text-slate-100 border-slate-700 shadow-sm'
                      : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-900'
                  }`}
                >
                  <span>Case {idx + 1}</span>
                  {tc.hidden && (
                    <span className="text-[10px] text-purple-400" title="Hidden Test Case">🔒</span>
                  )}
                </button>
              ))}
            </div>

            {/* Selected Case Details */}
            {selectedCase && (
              <div className="space-y-3 font-sans">
                <div className="flex items-center gap-2">
                  {selectedCase.hidden ? (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                      <span>🔒</span> Hidden Evaluation Test
                    </span>
                  ) : (
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                      <span>👁️</span> Visible Sample Test
                    </span>
                  )}
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Requirement Assertion
                  </span>
                  <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-200 font-mono">
                    {selectedCase.name}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Expected Behavior / Assertion Output
                  </span>
                  <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-emerald-400 font-mono">
                    {selectedCase.hidden 
                      ? '[Hidden Expected Output - Verifies edge-case behavior without revealing solution]'
                      : (selectedCase.expected || 'Passes assertion without defect')}
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
                <Code2 className="w-8 h-8 opacity-40 text-slate-400" />
                <p className="text-xs text-slate-400">You must run your code first</p>
              </div>
            ) : isRunning ? (
              <div className="flex flex-col items-center justify-center h-full text-cyan-400 py-10 space-y-2 animate-pulse">
                <Loader2 className="w-8 h-8 animate-spin" />
                <p className="text-xs text-slate-300">Evaluating against test assertions...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Result Status Header (Accepted / Wrong Answer / Compile Error) */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <span className={`text-base font-bold flex items-center gap-2 ${
                      isAllPassed ? 'text-emerald-400' : 'text-rose-500'
                    }`}>
                      {isAllPassed ? (
                        <>
                          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                          <span>Accepted</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-5 h-5 text-rose-500" />
                          <span>Wrong Answer</span>
                        </>
                      )}
                    </span>

                    <span className="text-xs font-mono text-slate-400 flex items-center gap-1 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <span>Runtime: {lastRunResult?.executionTime ? `${Math.round(lastRunResult.executionTime * 1000)} ms` : '5 ms'}</span>
                    </span>
                  </div>

                  <span className="text-xs font-semibold text-slate-300">
                    {passedCount} / {totalCount} test cases passed
                  </span>
                </div>

                {/* Case Selector Tabs */}
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  {comprehensiveCases.map((tc, idx) => {
                    const isCasePassed = tc.passed === true;
                    return (
                      <button
                        key={idx}
                        onClick={() => setSelectedCaseIdx(idx)}
                        className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg border transition-all ${
                          selectedCaseIdx === idx
                            ? 'bg-slate-800 text-slate-100 border-slate-700 shadow-sm'
                            : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-slate-200'
                        }`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${isCasePassed ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        <span>Case {idx + 1}</span>
                        {tc.hidden && (
                          <span className="text-[10px] text-purple-400" title="Hidden Test Case">🔒</span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Selected Case Inspection */}
                {selectedCase && (
                  <div className="space-y-3 font-mono text-xs">
                    <div className="flex items-center gap-2">
                      {selectedCase.hidden ? (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                          <span>🔒</span> Hidden Evaluation Test
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                          <span>👁️</span> Visible Sample Test
                        </span>
                      )}
                    </div>

                    <div className="space-y-1">
                      <span className="text-[11px] font-sans font-semibold text-slate-400 uppercase tracking-wider">
                        Requirement
                      </span>
                      <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-200">
                        {selectedCase.name}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[11px] font-sans font-semibold text-slate-400 uppercase tracking-wider">
                        Expected Output
                      </span>
                      <div className="p-2.5 rounded-lg bg-slate-900/80 border border-emerald-500/20 text-emerald-400">
                        {selectedCase.hidden
                          ? '[Hidden Expected Output - Secret assertion]'
                          : (selectedCase.expected || 'Expected result assertion passes')}
                      </div>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[11px] font-sans font-semibold text-slate-400 uppercase tracking-wider">
                        Actual Result
                      </span>
                      <div className={`p-2.5 rounded-lg border ${
                        selectedCase.passed 
                          ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' 
                          : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
                      }`}>
                        {selectedCase.passed 
                          ? 'Matched expected specification' 
                          : selectedCase.hidden
                            ? 'Hidden test assertion failed: The solution produced an incorrect result or encountered an unhandled edge case on this hidden test case.'
                            : (selectedCase.actual || selectedCase.error || 'Failed test assertion: Bug pattern detected')}
                      </div>
                    </div>
                  </div>
                )}

                {/* Collapsible Stdout / Console Drawer */}
                {runOutput && (
                  <div className="pt-2 border-t border-slate-800">
                    <button
                      onClick={() => setShowStdout(!showStdout)}
                      className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 font-semibold"
                    >
                      <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Console Logs / Traceback</span>
                      <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showStdout ? 'rotate-180' : ''}`} />
                    </button>

                    {showStdout && (
                      <pre className="mt-2 p-3 bg-slate-900/90 border border-slate-800 rounded-xl text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-40 overflow-y-auto">
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
          <div className="w-full h-full min-h-[180px] bg-slate-900 rounded-xl overflow-hidden border border-slate-800">
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
