import React from 'react';
import { 
  CheckCircle2, 
  Terminal, 
  Database, 
  Layout, 
  SlidersHorizontal,
  FileCode2,
  AlertCircle
} from 'lucide-react';

/**
 * Format inline text: backticks to <code>, **bold** to <strong>
 */
export function formatInlineText(text = '') {
  if (!text) return null;

  // Split text by code backticks first: `code`
  const parts = text.split(/(`[^`]+`)/g);

  return parts.map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`')) {
      const code = part.slice(1, -1);
      return (
        <code 
          key={index} 
          className="px-1.5 py-0.5 mx-0.5 rounded text-[12px] font-mono bg-slate-800 text-cyan-300 border border-slate-700/60"
        >
          {code}
        </code>
      );
    }

    // Split bold: **bold**
    const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((bPart, bIndex) => {
      if (bPart.startsWith('**') && bPart.endsWith('**')) {
        return (
          <strong key={`${index}-${bIndex}`} className="font-semibold text-slate-100">
            {bPart.slice(2, -2)}
          </strong>
        );
      }
      return bPart;
    });
  });
}

/**
 * Parse raw description and test cases into LeetCode-style problem structure
 */
export function parseProblemStatement(description = '', title = '', technology = '', category = '', testCases = [], files = []) {
  const raw = (description || '').trim();
  const techLow = (technology || '').toLowerCase();
  const cleanTitle = (title || 'Challenge').replace(/^\[.*?\]\s*/, '').replace(/^\d+\.\s*/, '').trim();

  const isFrontend = techLow.includes('react') || techLow.includes('css') || techLow.includes('html') || techLow.includes('frontend') || techLow.includes('web');
  const isSql = techLow.includes('sql') || techLow.includes('database') || techLow.includes('sqlite') || techLow.includes('postgresql');

  // 1. Parse sections if markdown headers are present
  const sections = {};
  if (raw.includes('###')) {
    const lines = raw.split('\n');
    let currentKey = 'scenario';

    for (const line of lines) {
      const lower = line.trim().toLowerCase();
      if (lower.startsWith('### company scenario') || lower.startsWith('### scenario')) {
        currentKey = 'scenario';
      } else if (lower.startsWith('### bug report') || lower.startsWith('### current issue') || lower.startsWith('### defect')) {
        currentKey = 'bugReport';
      } else if (lower.startsWith('### steps to reproduce')) {
        currentKey = 'reproduce';
      } else if (lower.startsWith('### expected behavior') || lower.startsWith('### expected')) {
        currentKey = 'expected';
      } else if (lower.startsWith('### actual behavior') || lower.startsWith('### actual')) {
        currentKey = 'actual';
      } else if (lower.startsWith('### impact')) {
        currentKey = 'impact';
      } else if (lower.startsWith('### requirements') || lower.startsWith('### requirement')) {
        currentKey = 'requirements';
      } else if (lower.startsWith('### example') || lower.startsWith('### test case')) {
        currentKey = 'examples';
      } else {
        if (!sections[currentKey]) sections[currentKey] = [];
        sections[currentKey].push(line);
      }
    }
  }

  const getSection = (key) => (sections[key] ? sections[key].join('\n').trim() : '');

  const scenarioText = getSection('scenario');
  const bugReportText = getSection('bugReport');
  const expectedText = getSection('expected');

  // 2. Synthesize concise 2-4 sentence problem statement
  let problemStatement = '';

  if (scenarioText || bugReportText) {
    const scenarioSentences = scenarioText
      .split(/(?<=[.!?])\s+/)
      .filter(s => s.trim().length > 0 && !s.includes('###'));
    const firstScenario = scenarioSentences.slice(0, 2).join(' ').trim();

    const bugSentences = bugReportText
      .split(/(?<=[.!?])\s+/)
      .filter(s => s.trim().length > 0 && !s.includes('###'));
    const bugSummary = bugSentences.slice(0, 2).join(' ').trim();

    const parts = [];
    if (firstScenario) parts.push(firstScenario);
    if (bugSummary && !firstScenario.includes(bugSummary)) parts.push(bugSummary);

    // Target goal
    const targetFile = (files && files[0] && files[0].name) ? files[0].name : 'the starter implementation';
    parts.push(`Investigate and repair the defect in \`${targetFile}\` so that all expected behavior and boundary assertions are restored.`);

    problemStatement = parts.join(' ');
  } else {
    // Already concise prose
    problemStatement = raw;
  }

  // 3. Extract compact LeetCode-style Examples from visible test cases
  const visibleCases = (testCases || []).filter(tc => !tc.hidden);
  const sampleCases = visibleCases.length > 0 ? visibleCases.slice(0, 2) : (testCases || []).slice(0, 2);

  const examples = sampleCases.map((tc, idx) => {
    let cleanName = (tc.name || `Case ${idx + 1}`)
      .replace(/^(Visible|Hidden):\s*/i, '')
      .replace(/^Case\s*\d+:\s*/i, '')
      .trim();

    let inputVal = tc.input || '';
    let outputVal = tc.expected || '';

    // If input is empty, provide sensible context
    if (!inputVal) {
      if (isSql) {
        inputVal = 'SELECT query execution on sample database tables';
      } else if (isFrontend) {
        inputVal = 'Render component and trigger interaction';
      } else {
        inputVal = 'Default function arguments';
      }
    }

    return {
      id: idx + 1,
      input: inputVal,
      output: outputVal || 'Passes assertion without defect',
      explanation: cleanName !== `Case ${idx + 1}` ? cleanName : null
    };
  });

  // 4. Derive relevant constraints
  const constraints = [];
  if (isSql) {
    constraints.push('Supported SQL Dialect: SQLite / ANSI SQL standard.');
    constraints.push('NULL Semantics: NULL denotes missing/unrecorded status; explicit IS NULL / IS NOT NULL handling is required.');
    constraints.push('Result ordering, aggregate precision, and column names must strictly match requirements.');
  } else if (isFrontend) {
    constraints.push('State updates must be immutable without mutating input props or DOM elements directly.');
    constraints.push('Event listeners, timers, or background subscriptions must be cleaned up on unmount.');
    constraints.push('Component must render consistently without visual glitches or runtime React errors.');
  } else {
    constraints.push('Inputs may include empty collections, zero values, or boundary indices; handle defensively.');
    constraints.push('Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.');
    constraints.push('Return types and error boundaries must conform to the expected module contract.');
  }

  // 5. Derive concise Expected Behavior summary
  let cleanExpected = '';
  if (expectedText) {
    cleanExpected = expectedText
      .split('\n')[0]
      .replace(/`.*=.*`/g, '')
      .trim();
  }
  if (!cleanExpected) {
    cleanExpected = isSql
      ? 'The query must return the exact matching rows and columns according to relational criteria and NULL constraints.'
      : isFrontend
      ? 'The component must render expected UI states dynamically and handle user interactions predictably.'
      : 'The function must compute and return expected values across all standard and boundary test scenarios.';
  }

  return {
    problemStatement,
    examples,
    constraints,
    isSql,
    isFrontend
  };
}

export default function ProblemStatementFormatter({ 
  description = '', 
  title = '', 
  technology = '', 
  category = '',
  testCases = [],
  files = []
}) {
  const {
    problemStatement,
    examples,
    constraints,
    isSql,
    isFrontend
  } = parseProblemStatement(description, title, technology, category, testCases, files);

  return (
    <div className="space-y-5 text-slate-300 text-[13px] leading-relaxed font-sans select-text">
      {/* A. Problem Statement (LeetCode Style Prose) */}
      <div className="space-y-2 text-slate-200">
        <p className="leading-relaxed text-[13px]">
          {formatInlineText(problemStatement)}
        </p>
      </div>

      {/* B. Examples (Compact LeetCode Cards) */}
      {examples.length > 0 && (
        <div className="space-y-3 pt-1">
          {examples.map((ex) => (
            <div 
              key={ex.id}
              className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2 font-mono text-xs"
            >
              <div className="font-sans font-bold text-slate-200 text-xs flex items-center justify-between">
                <span>Example {ex.id}:</span>
              </div>

              <div className="space-y-1.5 pl-1">
                <div className="flex items-start gap-2">
                  <span className="font-sans font-semibold text-slate-400 shrink-0 select-none">
                    {isSql ? 'Input Query:' : isFrontend ? 'Action:' : 'Input:'}
                  </span>
                  <span className="text-cyan-300 break-all whitespace-pre-wrap">
                    {ex.input}
                  </span>
                </div>

                <div className="flex items-start gap-2">
                  <span className="font-sans font-semibold text-slate-400 shrink-0 select-none">
                    {isSql ? 'Expected Rows:' : isFrontend ? 'UI State:' : 'Output:'}
                  </span>
                  <span className="text-emerald-400 break-all whitespace-pre-wrap">
                    {ex.output}
                  </span>
                </div>

                {ex.explanation && (
                  <div className="flex items-start gap-2 pt-1 font-sans text-[11px] text-slate-400 border-t border-slate-800/60">
                    <span className="font-semibold text-slate-300 shrink-0 select-none">
                      Explanation:
                    </span>
                    <span className="text-slate-300 leading-normal">
                      {ex.explanation}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* C. Constraints */}
      {constraints.length > 0 && (
        <div className="space-y-2 pt-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
            <span>Constraints</span>
          </h4>
          <ul className="space-y-1.5 pl-1">
            {constraints.map((c, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                <span className="leading-normal font-sans">
                  {formatInlineText(c)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
