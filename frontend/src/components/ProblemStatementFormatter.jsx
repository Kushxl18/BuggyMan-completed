import React from 'react';
import { Target, Info, AlertTriangle, ListChecks, CheckCircle2 } from 'lucide-react';

export function parseProblemStatement(description = '', title = '', technology = '', category = '') {
  let cleanDesc = (description || '').trim();

  let context = '';
  let currentIssue = '';
  let requirements = [];
  let goal = '';

  const techLow = (technology || '').toLowerCase();
  const titleClean = (title || 'Challenge').replace(/^\d+\.\s*/, '').replace(/^\[.*?\]\s*/, '').trim();

  const isFrontend = techLow.includes('react') || techLow.includes('css') || techLow.includes('html') || techLow.includes('web') || techLow.includes('styling') || techLow.includes('controlled');
  const isSql = techLow.includes('sql') || techLow.includes('database');
  const isBackend = techLow.includes('python') || techLow.includes('django') || techLow.includes('node') || techLow.includes('api') || techLow.includes('fastapi');

  // Parse description if it has explicit Requirements / Goal sections
  if (cleanDesc.includes('Requirements:') || cleanDesc.includes('Requirements')) {
    const parts = cleanDesc.split(/Requirements:?/i);
    context = parts[0].trim();
    const reqText = parts[1] || '';

    const lines = reqText.split('\n').map(l => l.trim()).filter(Boolean);
    lines.forEach(line => {
      if (line.toLowerCase().startsWith('goal:')) {
        goal = line.replace(/^goal:?/i, '').trim();
      } else {
        const cleanedLine = line.replace(/^[-*•]\s*/, '').trim();
        if (cleanedLine) requirements.push(cleanedLine);
      }
    });
  } else {
    context = cleanDesc;
  }

  // Ensure Context is structured and clear
  if (!context || context.length < 15) {
    if (isFrontend) {
      context = `The application renders a ${titleClean} component designed to provide real-time user interface interaction and state updates.`;
    } else if (isSql) {
      context = `The database contains records supporting the ${titleClean} reporting workflow to generate structured data output.`;
    } else if (isBackend) {
      context = `The backend service implements ${titleClean} endpoints to process incoming requests and manage data integrity.`;
    } else {
      context = `The system implements ${titleClean} logic to perform required data operations and produce expected results.`;
    }
  }

  // Synthesize Current Issue
  if (isFrontend) {
    currentIssue = `The current implementation has functional issues under specific user interactions or state updates. Identify and fix the defects in the ${titleClean} component while preserving the existing UI styling and architecture.`;
  } else if (isSql) {
    currentIssue = `The current query fails to return expected result sets due to incorrect filtering, missing joins, or improper clause ordering. Identify and fix the query statement to return accurate records.`;
  } else if (isBackend) {
    currentIssue = `The server handler fails to process payloads or returns invalid responses under edge cases. Identify and resolve the bug in the API logic.`;
  } else {
    currentIssue = `The current implementation contains one or more logic bugs causing invalid return values. Identify and fix the defects to satisfy problem assertions.`;
  }

  // Ensure Requirements bullet points are detailed and problem-specific
  if (requirements.length === 0) {
    if (isFrontend) {
      requirements = [
        `Render ${titleClean} UI controls cleanly according to visual design.`,
        `Update component state dynamically in real time upon user interactions.`,
        `Handle empty inputs and boundary conditions without crashing.`,
        `Maintain case-insensitive filtering or responsive layout behavior where applicable.`,
        `Ensure error fallback messages display correctly when zero items match.`
      ];
    } else if (isSql) {
      requirements = [
        `Select exact table columns required for the target query output.`,
        `Apply precise filter constraints to exclude invalid or unwanted records.`,
        `Ensure table join conditions and aggregate groupings execute correctly.`,
        `Sort results in expected ascending or descending order.`,
        `Handle NULL values and missing relational records gracefully.`
      ];
    } else if (isBackend) {
      requirements = [
        `Validate incoming request parameters and body payload structures.`,
        `Process target operations and mutate database records accurately.`,
        `Return standard HTTP response status codes and structured JSON payloads.`,
        `Handle validation errors and invalid inputs with proper error messages.`
      ];
    } else {
      requirements = [
        `Process input parameters and execute target algorithms accurately.`,
        `Return expected data structures and calculation outputs.`,
        `Handle boundary inputs and edge cases without runtime exceptions.`
      ];
    }
  }

  // Synthesize Goal
  if (!goal) {
    if (isFrontend) {
      goal = `Fix the ${titleClean} component functionality so it behaves correctly for normal interactions and relevant edge cases.`;
    } else if (isSql) {
      goal = `Correct the ${titleClean} SQL statement to return the exact expected record set, schema, and row order.`;
    } else if (isBackend) {
      goal = `Resolve the issue in ${titleClean} to ensure proper request processing, data integrity, and error handling.`;
    } else {
      goal = `Fix the logic for ${titleClean} so all input conditions and test assertions pass cleanly.`;
    }
  }

  return {
    title: titleClean,
    context,
    currentIssue,
    requirements,
    goal
  };
}

export default function ProblemStatementFormatter({ description = '', title = '', technology = '', category = '' }) {
  const statement = parseProblemStatement(description, title, technology, category);

  return (
    <div className="space-y-4 text-xs text-slate-300 font-sans leading-relaxed">
      {/* 1. Context Section */}
      <div className="space-y-1.5">
        <h4 className="text-[11px] font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>Context</span>
        </h4>
        <p className="text-slate-300 leading-normal">{statement.context}</p>
      </div>

      {/* 2. Current Issue Section */}
      <div className="space-y-1.5">
        <h4 className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          <span>Current Issue</span>
        </h4>
        <p className="text-slate-300 leading-normal">{statement.currentIssue}</p>
      </div>

      {/* 3. Requirements Section */}
      <div className="space-y-2">
        <h4 className="text-[11px] font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <ListChecks className="w-3.5 h-3.5 text-emerald-400" />
          <span>Requirements</span>
        </h4>
        <ul className="space-y-1.5 pl-1">
          {statement.requirements.map((req, idx) => (
            <li key={idx} className="flex items-start gap-2 text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
              <span className="leading-normal">{req}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 4. Goal Section */}
      <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
        <h4 className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
          <Target className="w-3.5 h-3.5 text-cyan-400" />
          <span>Goal</span>
        </h4>
        <p className="text-slate-300 leading-normal font-medium">{statement.goal}</p>
      </div>
    </div>
  );
}
