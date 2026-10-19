import React from 'react';
import { 
  Building2, 
  Bug, 
  ListOrdered, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  CheckSquare, 
  Info,
  Layers,
  ArrowRight
} from 'lucide-react';

/**
 * Helper to render inline markdown like `code`, **bold**, *italic* safely into React elements
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
 * Parse structured bug report markdown or fallback to clean sections
 */
export function parseProblemStatement(description = '', title = '', technology = '', category = '') {
  const raw = (description || '').trim();
  const techLow = (technology || '').toLowerCase();
  const cleanTitle = (title || 'Challenge').replace(/^\[.*?\]\s*/, '').replace(/^\d+\.\s*/, '').trim();

  const isFrontend = techLow.includes('react') || techLow.includes('css') || techLow.includes('html') || techLow.includes('frontend') || techLow.includes('web');
  const isSql = techLow.includes('sql') || techLow.includes('database');
  const isBackend = techLow.includes('python') || techLow.includes('django') || techLow.includes('node') || techLow.includes('api');

  // Check if text has markdown headings (### )
  const sections = {};
  const currentSection = { name: 'scenario', lines: [] };
  
  if (raw.includes('###')) {
    const lines = raw.split('\n');
    let currentKey = 'scenario';

    for (const line of lines) {
      const trimmed = line.trim();
      const lower = trimmed.toLowerCase();

      if (lower.startsWith('### company scenario') || lower.startsWith('### scenario')) {
        currentKey = 'scenario';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### bug report') || lower.startsWith('### current issue') || lower.startsWith('### defect')) {
        currentKey = 'bugReport';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### steps to reproduce')) {
        currentKey = 'reproduce';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### expected behavior') || lower.startsWith('### expected')) {
        currentKey = 'expected';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### actual behavior') || lower.startsWith('### actual')) {
        currentKey = 'actual';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### impact')) {
        currentKey = 'impact';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### requirements') || lower.startsWith('### requirement')) {
        currentKey = 'requirements';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else if (lower.startsWith('### example') || lower.startsWith('### test case')) {
        currentKey = 'examples';
        if (!sections[currentKey]) sections[currentKey] = [];
      } else {
        if (!sections[currentKey]) sections[currentKey] = [];
        sections[currentKey].push(line);
      }
    }
  }

  // Helper to join and clean lines
  const getSectionText = (key) => {
    if (!sections[key] || sections[key].length === 0) return '';
    return sections[key].join('\n').trim();
  };

  let scenario = getSectionText('scenario');
  let bugReport = getSectionText('bugReport');
  let reproduceRaw = getSectionText('reproduce');
  let expected = getSectionText('expected');
  let actual = getSectionText('actual');
  let impact = getSectionText('impact');
  let reqsRaw = getSectionText('requirements');
  let examplesRaw = getSectionText('examples');

  // If not parsed by ### headers, attempt legacy split by "Requirements:"
  if (!scenario && !bugReport && !expected && !reqsRaw) {
    if (raw.includes('Requirements:') || raw.includes('Requirements')) {
      const parts = raw.split(/Requirements:?/i);
      scenario = parts[0].trim();
      reqsRaw = parts[1] || '';
    } else {
      scenario = raw;
    }
  }

  // Parse reproduce steps into array
  const reproduceSteps = [];
  if (reproduceRaw) {
    const lines = reproduceRaw.split('\n');
    for (const l of lines) {
      const step = l.trim().replace(/^\d+[\.\)]\s*/, '').replace(/^[-*•]\s*/, '').trim();
      if (step) reproduceSteps.push(step);
    }
  }

  // Parse requirements into array
  const requirements = [];
  if (reqsRaw) {
    const lines = reqsRaw.split('\n');
    for (const l of lines) {
      const req = l.trim().replace(/^[-*•]\s*/, '').trim();
      if (req && !req.toLowerCase().startsWith('goal:')) {
        requirements.push(req);
      }
    }
  }

  // Fallbacks if missing
  if (!scenario) {
    if (isFrontend) {
      scenario = `In a production client application, users interact with the ${cleanTitle} component to view and manage state dynamically.`;
    } else if (isSql) {
      scenario = `A production analytics and reporting pipeline relies on ${cleanTitle} queries to extract accurate records from the database.`;
    } else {
      scenario = `A core production service executes ${cleanTitle} logic to handle critical request payloads and data transactions.`;
    }
  }

  if (!bugReport && !actual) {
    if (isFrontend) {
      bugReport = `The component fails to update or render expected state under specific interaction flows or boundary conditions.`;
    } else if (isSql) {
      bugReport = `The query returns incorrect results due to improper filtering, join conditions, or handling of NULL values.`;
    } else {
      bugReport = `The implementation produces incorrect outputs or throws unexpected exceptions under edge case inputs.`;
    }
  }

  if (requirements.length === 0) {
    if (isFrontend) {
      requirements.push(
        `Ensure ${cleanTitle} renders correctly and updates state dynamically upon user interaction.`,
        `Handle boundary inputs and edge cases without runtime errors.`
      );
    } else if (isSql) {
      requirements.push(
        `Update the SQL query to return the exact columns and rows required.`,
        `Ensure proper filtering, joins, and correct handling of NULL values.`
      );
    } else {
      requirements.push(
        `Identify and fix the defect in ${cleanTitle} logic.`,
        `Ensure all visible and hidden evaluation test assertions pass cleanly.`
      );
    }
  }

  return {
    scenario,
    bugReport,
    reproduceSteps,
    expected,
    actual,
    impact,
    requirements,
    examplesRaw
  };
}

export default function ProblemStatementFormatter({ 
  description = '', 
  title = '', 
  technology = '', 
  category = '' 
}) {
  const parsed = parseProblemStatement(description, title, technology, category);

  return (
    <div className="space-y-5 text-slate-300 text-[13px] leading-relaxed font-sans select-text">
      {/* 1. Company Scenario / Problem Introduction (LeetCode Style prose) */}
      {parsed.scenario && (
        <div className="space-y-1.5 text-slate-200">
          <p className="leading-relaxed">
            {formatInlineText(parsed.scenario)}
          </p>
        </div>
      )}

      {/* 2. Bug Report / Defect Description */}
      {parsed.bugReport && (
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/90 shadow-sm space-y-1.5">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
            <Bug className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Defect Observed</span>
          </div>
          <p className="text-slate-300 text-xs leading-normal">
            {formatInlineText(parsed.bugReport)}
          </p>
        </div>
      )}

      {/* 3. Steps to Reproduce */}
      {parsed.reproduceSteps.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-slate-400 font-semibold text-xs uppercase tracking-wider">
            <ListOrdered className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>Steps to Reproduce</span>
          </div>
          <ol className="space-y-1.5 pl-1">
            {parsed.reproduceSteps.map((step, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-300">
                <span className="flex items-center justify-center w-4 h-4 rounded-full bg-slate-800 text-cyan-400 text-[10px] font-mono font-bold shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <span className="leading-normal">{formatInlineText(step)}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* 4. Expected vs Actual Comparison (LeetCode Contrast Cards) */}
      {(parsed.expected || parsed.actual) && (
        <div className="grid grid-cols-1 gap-2.5 pt-1">
          {parsed.expected && (
            <div className="p-3 rounded-xl bg-emerald-950/15 border border-emerald-500/25 space-y-1">
              <div className="flex items-center gap-1.5 text-emerald-400 font-semibold text-xs">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Expected Behavior</span>
              </div>
              <p className="text-slate-300 text-xs leading-normal pl-5">
                {formatInlineText(parsed.expected)}
              </p>
            </div>
          )}

          {parsed.actual && (
            <div className="p-3 rounded-xl bg-rose-950/15 border border-rose-500/25 space-y-1">
              <div className="flex items-center gap-1.5 text-rose-400 font-semibold text-xs">
                <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                <span>Actual Behavior (Defect)</span>
              </div>
              <p className="text-slate-300 text-xs leading-normal pl-5">
                {formatInlineText(parsed.actual)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* 5. Business / System Impact */}
      {parsed.impact && (
        <div className="p-3 rounded-xl bg-amber-950/15 border border-amber-500/20 text-xs space-y-1">
          <div className="flex items-center gap-1.5 text-amber-400 font-semibold text-[11px] uppercase tracking-wider">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Production Impact</span>
          </div>
          <p className="text-slate-300 leading-normal pl-5">
            {formatInlineText(parsed.impact)}
          </p>
        </div>
      )}

      {/* 6. Requirements */}
      {parsed.requirements.length > 0 && (
        <div className="space-y-2 pt-1 border-t border-slate-800/80">
          <div className="flex items-center gap-1.5 text-slate-300 font-semibold text-xs uppercase tracking-wider">
            <CheckSquare className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>Requirements</span>
          </div>
          <ul className="space-y-1.5 pl-1">
            {parsed.requirements.map((req, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                <span className="leading-normal">{formatInlineText(req)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
