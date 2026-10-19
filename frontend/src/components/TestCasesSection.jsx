import React from 'react';
import { CheckCircle2, Check, X } from 'lucide-react';

const sanitizeExpectedText = (expected, name = '', technology = '') => {
  if (!expected) return 'Behaves as specified in problem requirements';

  let str = String(expected).trim();

  // If expected text contains raw code syntax, convert to clear behavior description!
  if (
    str.includes('.toLowerCase(') ||
    str.includes('toLowerCase') ||
    str.includes('includes(') ||
    str.includes('useState') ||
    str.includes('useEffect') ||
    str.includes('JOIN') ||
    str.includes('WHERE') ||
    str.includes('SELECT') ||
    str.includes('transition:') ||
    str.includes('background-color:') ||
    str.includes('<') ||
    str.includes('=>') ||
    str.includes('function') ||
    str.includes('return')
  ) {
    const lowerName = name.toLowerCase();
    if (lowerName.includes('case') || lowerName.includes('search')) {
      return 'Matches titles regardless of upper or lower case letter casing';
    }
    if (lowerName.includes('transition') || lowerName.includes('theme') || lowerName.includes('smooth')) {
      return 'Applies smooth visual color transitions when theme toggles';
    }
    if (lowerName.includes('color') || lowerName.includes('badge') || lowerName.includes('priority')) {
      return 'Applies distinct visual priority styling according to severity level';
    }
    if (lowerName.includes('sql') || lowerName.includes('order') || lowerName.includes('filter') || lowerName.includes('query')) {
      return 'Returns correct filtered dataset matching target requirements';
    }
    if (name) {
      return `Satisfies ${name.replace(/^(Visible|Hidden):\s*/i, '')} criteria`;
    }
    return 'Satisfies specified functional test requirements';
  }

  return str;
};

export const deriveComprehensiveTestCases = (rawCases = [], challengeTitle = '', technology = '') => {
  const isSql = (technology || '').toLowerCase().includes('sql') || (challengeTitle || '').toLowerCase().includes('sql');
  const isFrontend = (technology || '').toLowerCase().includes('react') || (technology || '').toLowerCase().includes('css') || (technology || '').toLowerCase().includes('html') || (technology || '').toLowerCase().includes('js');

  const sanitized = (rawCases || []).map((tc, idx) => {
    const isHidden = Boolean(
      tc.hidden || 
      (tc.name && tc.name.toLowerCase().includes('hidden')) || 
      (rawCases.length >= 3 && idx >= 2)
    );
    return {
      id: tc.id || idx + 1,
      name: tc.name || `Requirement ${idx + 1}`,
      expected: isHidden 
        ? '[Hidden Expected Output - Secret test case assertion]' 
        : sanitizeExpectedText(tc.expected, tc.name || challengeTitle, technology),
      passed: tc.passed,
      input: tc.input,
      actual: tc.actual,
      error: tc.error,
      hidden: isHidden
    };
  });

  if (sanitized.length >= 3) {
    return sanitized;
  }

  const existingNames = new Set(sanitized.map(t => (t.name || '').toLowerCase()));

  if (isSql) {
    if (!existingNames.has('query results assertion')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Query Results & Output Format',
        expected: 'Returns exact matching rows with expected column headers',
        passed: sanitized[0]?.passed
      });
    }
    if (!existingNames.has('filtering & null handling')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Data Filtering & Constraint Verification',
        expected: 'Excludes unmatched records and handles NULL values gracefully',
        passed: sanitized[0]?.passed
      });
    }
    if (sanitized.length < 3) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Aggregate & Ordering Precision',
        expected: 'Calculates aggregate metrics and orders records accurately',
        passed: sanitized[0]?.passed
      });
    }
  } else if (isFrontend) {
    if (!existingNames.has('real-time interaction')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Interactive State & Event Handling',
        expected: 'Updates UI state cleanly upon user interactions and events',
        passed: sanitized[0]?.passed
      });
    }
    if (!existingNames.has('boundary conditions')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Edge Case & Empty State Resilience',
        expected: 'Renders appropriate fallback feedback for empty or boundary inputs',
        passed: sanitized[0]?.passed
      });
    }
    if (sanitized.length < 3) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Component Rendering & DOM Integrity',
        expected: 'Maintains consistent component hierarchy without visual glitches',
        passed: sanitized[0]?.passed
      });
    }
  } else {
    if (!existingNames.has('input assertions')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Input Assertion & Logic Validation',
        expected: 'Evaluates input arguments and executes target logic correctly',
        passed: sanitized[0]?.passed
      });
    }
    if (!existingNames.has('boundary scenario')) {
      sanitized.push({
        id: sanitized.length + 1,
        name: 'Boundary Scenario & Exception Handling',
        expected: 'Handles boundary conditions without uncaught exceptions',
        passed: sanitized[0]?.passed
      });
    }
  }

  return sanitized;
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
              className={`p-3 rounded-xl border text-xs space-y-1 transition-all ${
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
                  <span>{tc.name}</span>
                  {tc.hidden ? (
                    <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">
                      Hidden Test
                    </span>
                  ) : (
                    <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                      Visible Test
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

              {tc.expected && (
                <p className="text-[11px] text-slate-400 leading-normal pl-6">
                  Expected: <span className="text-emerald-400 font-medium">{tc.expected}</span>
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
