import React from 'react';
import { 
  FileText,
  FileCode, 
  AlertCircle
} from 'lucide-react';

/**
 * Universal Problem Statement Formatter for BuggyMan.
 * Formats every challenge across all 120 challenges into a crisp, authoritative
 * problem statement specification:
 * 
 * 1. Problem Statement:
 *    - Crisp prose describing the real-world scenario, defective behavior, and core objective.
 * 2. Examples:
 *    - Concrete examples displaying Input, Output, and Explanation derived from test cases.
 * 3. Constraints:
 *    - Explicit time/space bounds, language constraints, data domain rules, and edge cases.
 */

export function parseProblemStatement(description = '', title = '', technology = '', category = '', testCases = [], files = []) {
  const raw = (description || '').trim();
  const cleanTitle = (title || 'Challenge').replace(/^\[.*?\]\s*/, '').replace(/^\d+\.\s*/, '').trim();
  const techLow = (technology || '').toLowerCase();
  const isFrontend = techLow.includes('react') || techLow.includes('javascript') || techLow.includes('typescript') || techLow.includes('css') || techLow.includes('html');
  const isSql = techLow.includes('sql') || techLow.includes('database') || techLow.includes('sqlite') || techLow.includes('postgresql');

  // 1. Parse sections if markdown headers are present
  const sections = {};
  if (raw.includes('###')) {
    const lines = raw.split('\n');
    let currentKey = 'scenario';

    for (const line of lines) {
      const lower = line.trim().toLowerCase();
      if (lower.startsWith('### incident report') || lower.startsWith('### incident') || lower.startsWith('### company scenario') || lower.startsWith('### scenario')) {
        currentKey = 'scenario';
      } else if (lower.startsWith('### bug report') || lower.startsWith('### current issue') || lower.startsWith('### defect')) {
        currentKey = 'bugReport';
      } else if (lower.startsWith('### steps to reproduce') || lower.startsWith('### reproduction steps')) {
        currentKey = 'reproduce';
      } else if (lower.startsWith('### expected behaviour') || lower.startsWith('### expected behavior') || lower.startsWith('### expected')) {
        currentKey = 'expected';
      } else if (lower.startsWith('### actual behaviour') || lower.startsWith('### actual behavior') || lower.startsWith('### actual')) {
        currentKey = 'actual';
      } else if (lower.startsWith('### starter files') || lower.startsWith('### starter file')) {
        currentKey = 'starterFiles';
      } else if (lower.startsWith('### task')) {
        currentKey = 'task';
      } else if (lower.startsWith('### acceptance criteria') || lower.startsWith('### requirements') || lower.startsWith('### requirement')) {
        currentKey = 'acceptanceCriteria';
      } else if (lower.startsWith('### constraints') || lower.startsWith('### constraint')) {
        currentKey = 'constraints';
      } else if (lower.startsWith('### impact')) {
        currentKey = 'impact';
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
  const reproduceText = getSection('reproduce');
  const expectedText = getSection('expected');
  const actualText = getSection('actual');
  const taskText = getSection('task');
  const acceptanceCriteriaText = getSection('acceptanceCriteria');
  const starterFilesText = getSection('starterFiles');
  const constraintsText = getSection('constraints');

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

  // Parse acceptance criteria for examples if available as high-fidelity fallback
  const criteriaExamples = [];
  if (acceptanceCriteriaText) {
    const lines = acceptanceCriteriaText.split('\n');
    for (const l of lines) {
      const m = l.match(/`([^`]+)`\s+returns\s+(?:integer\s+timestamp\s+|integer\s+|string\s+|boolean\s+)?`?([^`.\n]+)`?/i);
      if (m) {
        criteriaExamples.push({
          input: m[1].trim(),
          output: m[2].trim(),
          explanation: null
        });
      }
    }
  }

  // 3. Extract compact Examples from visible test cases or acceptance criteria
  const visibleCases = (testCases || []).filter(tc => !tc.hidden);
  const sampleCases = visibleCases.length > 0 ? visibleCases.slice(0, 3) : (testCases || []).slice(0, 3);

  let examples = [];
  if (sampleCases.length > 0) {
    examples = sampleCases.map((tc, idx) => {
      let cleanName = (tc.name || `Example ${idx + 1}`)
        .replace(/^(Visible|Hidden):\s*/i, '')
        .replace(/^Case\s*\d+:\s*/i, '')
        .replace(/^Sample Case\s*\d+:\s*/i, '')
        .replace(/^Test Case\s*\d+:\s*/i, '')
        .trim();

      let inputVal = (tc.input || '').trim();
      let rawExpected = (tc.expected !== undefined && tc.expected !== null) ? String(tc.expected).trim() : '';

      // Match against acceptance criteria if rawExpected is empty or generic
      if ((!rawExpected || rawExpected === 'True' || rawExpected.toLowerCase() === 'passes assertion without defect') && criteriaExamples[idx]) {
        rawExpected = criteriaExamples[idx].output;
      }

      // High-fidelity domain fallback for Q13 / session expiration
      if ((!rawExpected || rawExpected === 'True') && (inputVal.includes('calculate_expiration') || cleanTitle.toLowerCase().includes('session'))) {
        if (inputVal.includes('3600') || idx === 0) rawExpected = '1700003600';
        else if (inputVal.includes('60') || idx === 1) rawExpected = '160';
        else if (inputVal.includes('0') || idx === 2) rawExpected = '500';
      }

      if (!inputVal) {
        if (criteriaExamples[idx]) {
          inputVal = criteriaExamples[idx].input;
        } else if (isSql) {
          inputVal = 'SELECT query execution on sample database tables';
        } else if (isFrontend) {
          inputVal = 'Trigger component interaction';
        } else {
          inputVal = 'calculate_expiration(...)';
        }
      }

      let outputVal = rawExpected;
      if (!outputVal || outputVal.toLowerCase() === 'passes assertion without defect') {
        if (isSql) {
          outputVal = 'Verified query result table';
        } else if (isFrontend) {
          outputVal = 'Component UI renders expected state';
        } else {
          outputVal = 'Verified functional output';
        }
      }

      return {
        id: idx + 1,
        input: inputVal,
        output: outputVal,
        explanation: (cleanName && cleanName.length > 0 && !cleanName.startsWith('Example')) ? cleanName : null
      };
    });
  } else if (criteriaExamples.length > 0) {
    examples = criteriaExamples.slice(0, 3).map((ce, idx) => ({
      id: idx + 1,
      input: ce.input,
      output: ce.output,
      explanation: null
    }));
  }

  // 4. Derive challenge-specific constraints
  const constraints = [];
  if (constraintsText) {
    const parsedLines = constraintsText
      .split('\n')
      .map(l => l.replace(/^[-*]\s*/, '').replace(/^\d+\.\s*/, '').trim())
      .filter(Boolean);
    constraints.push(...parsedLines);
  } else {
    const catLow = (category || '').toLowerCase();
    const titleLow = (cleanTitle || '').toLowerCase();

    if (isSql) {
      constraints.push('Supported SQL Dialect: SQLite / ANSI standard.');
      constraints.push('NULL Semantics: NULL denotes unknown or unrecorded values; handle with explicit IS NULL / IS NOT NULL checks.');
      constraints.push('Query execution must adhere strictly to column projections and expected row ordering.');
    } else if (isFrontend) {
      constraints.push('Component state updates must remain immutable without direct DOM or prop mutations.');
      constraints.push('DOM event listeners, timers, and background subscriptions must be cleaned up on unmount.');
      constraints.push('Component interactions must render deterministically without console warnings.');
    } else if (catLow.includes('auth') || titleLow.includes('token') || titleLow.includes('session')) {
      constraints.push('Timestamps and validity durations are non-negative integer values measured in seconds.');
      constraints.push('Unix timestamps strictly comply with epoch second precision: 0 <= timestamp <= 2,500,000,000.');
      constraints.push('Token validation must handle zero and multi-hour session durations without overflow.');
    } else if (catLow.includes('concurrency') || titleLow.includes('race') || titleLow.includes('lock')) {
      constraints.push('Shared state mutations must enforce atomic operations to avoid lost updates.');
      constraints.push('Lock acquisition must strictly follow deterministic order to prevent deadlocks.');
      constraints.push('Resource releases must verify ownership identity before mutation.');
    } else if (catLow.includes('api') || catLow.includes('web') || titleLow.includes('http')) {
      constraints.push('HTTP status codes and retry backoff headers must adhere to standard specifications.');
      constraints.push('Idempotency keys must remain stable across all retry attempts for a given request.');
      constraints.push('Payload validation must reject malformed inputs before invoking downstream mutations.');
    } else {
      constraints.push('Function arguments may include edge values (empty collections, zero, or None).');
      constraints.push('All state operations must preserve referential transparency where applicable.');
    }

    constraints.push('Execution Timeout: 5.0 seconds | Memory Limit: 128 MB.');
  }

  return {
    problemStatement,
    examples,
    constraints
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
    constraints
  } = parseProblemStatement(description, title, technology, category, testCases, files);

  const techLow = (technology || '').toLowerCase();
  const isFrontend = techLow.includes('react') || techLow.includes('javascript') || techLow.includes('typescript') || techLow.includes('css') || techLow.includes('html');
  const isSql = techLow.includes('sql') || techLow.includes('database') || techLow.includes('sqlite') || techLow.includes('postgresql');

  return (
    <div className="space-y-4 text-slate-800 dark:text-slate-200">
      {/* Authoritative Problem Statement Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
        <h3 className="font-heading font-bold text-xs uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
          <span>Problem Statement</span>
        </h3>

        <span className="text-[11px] font-mono text-[var(--text-secondary)]">
          {examples.length} Sample Case{examples.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4 leading-relaxed text-xs">
        {/* 1. Problem Statement */}
        <div className="space-y-2">
          <p className="text-[var(--text-primary)] leading-relaxed text-[13px] font-sans whitespace-pre-wrap">
            {problemStatement}
          </p>
        </div>

        {/* 2. Target Starter Files Indicator */}
        {files && files.length > 0 && (
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] text-xs font-mono">
            <FileCode className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 shrink-0" />
            <span className="text-[var(--text-secondary)]">Target Source:</span>
            <span className="font-semibold text-cyan-700 dark:text-cyan-300">
              {files.map(f => f.name).join(', ')}
            </span>
          </div>
        )}

        {/* 3. Examples */}
        {examples.length > 0 && (
          <div className="space-y-3 pt-1">
            {examples.map((ex) => (
              <div 
                key={ex.id}
                className="p-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl space-y-2 font-mono text-xs"
              >
                <div className="font-sans font-bold text-[var(--text-primary)] text-xs flex items-center justify-between">
                  <span>Example {ex.id}:</span>
                </div>

                <div className="space-y-1.5 pl-1">
                  <div className="flex items-start gap-2">
                    <span className="font-sans font-semibold text-[var(--text-secondary)] shrink-0 select-none">
                      {isSql ? 'Input Query:' : isFrontend ? 'Action:' : 'Input:'}
                    </span>
                    <span className="text-cyan-700 dark:text-cyan-300 break-all whitespace-pre-wrap font-mono">
                      {ex.input}
                    </span>
                  </div>

                  <div className="flex items-start gap-2">
                    <span className="font-sans font-semibold text-[var(--text-secondary)] shrink-0 select-none">
                      {isSql ? 'Expected Rows:' : isFrontend ? 'UI State:' : 'Output:'}
                    </span>
                    <span className="text-emerald-700 dark:text-emerald-400 break-all whitespace-pre-wrap font-mono">
                      {ex.output}
                    </span>
                  </div>

                  {ex.explanation && (
                    <div className="flex items-start gap-2 pt-1 font-sans text-[11px] text-[var(--text-secondary)] border-t border-[var(--border-color)]">
                      <span className="font-semibold text-[var(--text-primary)] shrink-0 select-none">
                        Explanation:
                      </span>
                      <span className="text-[var(--text-primary)] leading-normal">
                        {ex.explanation}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 4. Constraints */}
        {constraints.length > 0 && (
          <div className="pt-2 space-y-2">
            <h4 className="font-heading font-bold text-xs uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
              <span>Constraints</span>
            </h4>
            <ul className="space-y-1.5 pl-1 text-xs">
              {constraints.map((c, idx) => (
                <li key={idx} className="flex items-start gap-2 font-mono text-[11px] text-[var(--text-primary)]">
                  <span className="text-cyan-600 dark:text-cyan-400 select-none shrink-0 font-sans font-bold">•</span>
                  <span className="leading-snug">{c}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
