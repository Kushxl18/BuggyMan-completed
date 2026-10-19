import React from 'react';
import { CheckCircle2, Check, X } from 'lucide-react';

export const deriveComprehensiveTestCases = (rawCases = [], challengeTitle = '', technology = '') => {
  return (rawCases || []).map((tc, idx) => {
    const isHidden = Boolean(
      tc.hidden || 
      (tc.name && String(tc.name).toLowerCase().includes('hidden'))
    );
    return {
      id: tc.id || idx + 1,
      name: `Test Case ${idx + 1}`,
      passed: tc.passed,
      input: isHidden ? '' : (tc.input || ''),
      error: tc.error || tc.hint,
      hint: tc.hint || tc.error,
      hidden: isHidden
    };
  });
};

export default function TestCasesSection({ testCases = [], challengeTitle = '', technology = '', showHeader = true }) {
  const cases = deriveComprehensiveTestCases(testCases, challengeTitle, technology);

  return (
    <div className="space-y-2.5">
      {showHeader && (
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Test Cases ({cases.length})</span>
        </h3>
      )}

      <div className="space-y-2">
        {cases.map((tc, idx) => {
          const isPassed = tc.passed === true;
          const isFailed = tc.passed === false;

          return (
            <div
              key={tc.id || idx}
              className={`p-3 rounded-xl border text-xs space-y-1.5 transition-all ${
                isPassed
                  ? 'bg-emerald-950/20 border-emerald-500/30'
                  : isFailed
                  ? 'bg-rose-950/20 border-rose-500/30'
                  : 'bg-slate-950/50 border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between font-semibold text-slate-200">
                <div className="flex items-center gap-2 flex-wrap">
                  {isPassed ? (
                    <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : isFailed ? (
                    <X className="w-4 h-4 text-rose-400 shrink-0" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
                  )}
                  <span>Test Case {idx + 1}</span>
                  {tc.hidden && (
                    <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">
                      Hidden Test
                    </span>
                  )}
                </div>
                {tc.passed !== undefined && (
                  <span
                    className={`text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                      isPassed
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    }`}
                  >
                    {isPassed ? 'PASSED' : 'FAILED'}
                  </span>
                )}
              </div>

              {isFailed && (tc.hint || tc.error) && (
                <div className="text-[11px] text-rose-300 leading-normal pl-6 bg-rose-950/30 p-2 rounded-lg border border-rose-500/20">
                  <span className="font-semibold text-rose-400">Feedback: </span>
                  {tc.hint || tc.error}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
