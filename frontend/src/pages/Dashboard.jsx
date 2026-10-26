import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Code2, 
  Database, 
  Palette, 
  ArrowRight, 
  User, 
  Briefcase, 
  ChevronRight,
  Layers,
  Sparkles
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import OnboardingModal from '../components/OnboardingModal';
import { authService } from '../services/authService';

export default function Dashboard({ user, addToast }) {
  const [profile, setProfile] = useState(user || null);
  const [showOnboardingModal, setShowOnboardingModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHomeData() {
      try {
        setLoading(true);
        const u = await authService.getCurrentUser().catch(() => user);
        if (u) setProfile(u);
      } catch (err) {
        // Fallback to prop user
      } finally {
        setLoading(false);
      }
    }
    loadHomeData();
  }, [user]);

  useEffect(() => {
    const onboardingDone = localStorage.getItem('buggyman_onboarding_completed');
    if (!onboardingDone) {
      setShowOnboardingModal(true);
    }
  }, []);

  const scrollToExplore = () => {
    const el = document.getElementById('explore-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const solvedCount = profile?.challengesSolved ?? profile?.challenges_solved ?? 0;

  return (
    <div className="max-w-6xl mx-auto space-y-5 py-1 animate-fade-in">
      <OnboardingModal 
        isOpen={showOnboardingModal} 
        onClose={() => setShowOnboardingModal(false)} 
      />

      {/* 1. Workspace Header - Modern Linear/Vercel Studio Style */}
      <div className="relative overflow-hidden border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 md:p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_24px_rgba(0,0,0,0.1)]">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-80 h-80 bg-blue-600/5 dark:bg-blue-500/[0.05] rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-2xl">
            <h1 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Welcome to BuggyMan
            </h1>
            <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Interactive software debugging and diagnosis practice. Select an arena below to reproduce defects, examine test failures, and fix production issues.
            </p>
          </div>

          <div className="relative z-10 flex items-center gap-2.5 self-start md:self-center shrink-0">
            <Link
              to="/challenges"
              className="button-primary text-xs"
            >
              <span>Start Debugging</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <button
              onClick={scrollToExplore}
              className="button-secondary text-xs"
            >
              <span>Explore Arenas</span>
            </button>
          </div>
        </div>

        {/* 4 Developer Metrics - Modernized Metric Cards */}
        <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5 pt-5 border-t border-slate-200/70 dark:border-white/[0.06]">
          <div className="p-3 rounded-lg bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/70 dark:border-white/[0.06] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.03)] hover:border-slate-300 dark:hover:border-white/[0.12] transition-colors">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">Challenges Solved</span>
            <span className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100 tabular-nums">{solvedCount}</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/70 dark:border-white/[0.06] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.03)] hover:border-slate-300 dark:hover:border-white/[0.12] transition-colors">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">Current Streak</span>
            <span className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100 tabular-nums">{profile?.streak || 0} days</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/70 dark:border-white/[0.06] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.03)] hover:border-slate-300 dark:hover:border-white/[0.12] transition-colors">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">Score</span>
            <span className="text-xl font-bold font-mono text-blue-600 dark:text-blue-400 tabular-nums">{profile?.totalScore || 0} XP</span>
          </div>
          <div className="p-3 rounded-lg bg-slate-50/80 dark:bg-white/[0.02] border border-slate-200/70 dark:border-white/[0.06] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.03)] hover:border-slate-300 dark:hover:border-white/[0.12] transition-colors">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">BugBytes Balance</span>
            <span className="text-xl font-bold font-mono text-slate-900 dark:text-slate-100 tabular-nums">{profile?.bugbytes_balance ?? profile?.bugbytesBalance ?? 50} BB</span>
          </div>
        </div>
      </div>

      {/* Feature Implementation Arena Highlight Banner (Unlinked for now - preserved to re-link later)
      <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)] hover:border-slate-300 dark:hover:border-white/[0.14] transition-all">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900/60">
              New Coding Arena
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">Multi-File Codebases</span>
          </div>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Feature Implementation Arena
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            Work with realistic multi-file repositories, receive full feature specifications, and ship production-grade implementations evaluated against 5-tier test suites.
          </p>
        </div>
        <Link
          to="/feature-challenges"
          className="button-primary text-xs shrink-0 self-start md:self-center"
        >
          <span>Browse Feature Challenges</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
      */}

      {/* 2. Specialized Arenas - 3 Columns with Aligned Heights & Linear-Style Cards */}
      <div id="explore-section" className="space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-slate-100">
            Three Specialized Debugging Arenas
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Targeted sandboxes designed for distinct software layers and real-world failure modes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Code Challenges */}
          <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 h-full group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
            <div className="space-y-3.5">
              <div className="flex items-center justify-between">
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-white/[0.06] text-slate-800 dark:text-slate-200 flex items-center justify-center shrink-0 border border-slate-200/70 dark:border-white/[0.08] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)] group-hover:text-blue-500 transition-colors">
                  <Code2 className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 border border-blue-200/70 dark:border-blue-900/60">
                  Python / Node
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  Code Challenges
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed min-h-[48px]">
                  Debug backend application logic, API boundaries, async handlers, and data parsing defects in isolated sandboxes.
                </p>
              </div>
            </div>
            <div className="pt-3 mt-3 border-t border-slate-100 dark:border-white/[0.06]">
              <Link
                to="/challenges"
                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center justify-between group/link py-0.5"
              >
                <span>Explore Code Challenges</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Card 2: SQL Lab */}
          <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 h-full group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
            <div className="space-y-3.5">
              <div className="flex items-center justify-between">
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-white/[0.06] text-slate-800 dark:text-slate-200 flex items-center justify-center shrink-0 border border-slate-200/70 dark:border-white/[0.08] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)] group-hover:text-blue-500 transition-colors">
                  <Database className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-white/[0.06] border border-slate-200/70 dark:border-white/[0.08]">
                  SQLite / Relational
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  SQL Lab
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed min-h-[48px]">
                  Isolate and correct database query bugs: invalid JOIN relationships, GROUP BY aggregation traps, NULL edge cases, and CTEs.
                </p>
              </div>
            </div>
            <div className="pt-3 mt-3 border-t border-slate-100 dark:border-white/[0.06]">
              <Link
                to="/sql-challenges"
                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center justify-between group/link py-0.5"
              >
                <span>Explore SQL Lab</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Card 3: Frontend Studio */}
          <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 h-full group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
            <div className="space-y-3.5">
              <div className="flex items-center justify-between">
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-white/[0.06] text-slate-800 dark:text-slate-200 flex items-center justify-center shrink-0 border border-slate-200/70 dark:border-white/[0.08] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1)] group-hover:text-blue-500 transition-colors">
                  <Palette className="w-4 h-4" />
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-white/[0.06] border border-slate-200/70 dark:border-white/[0.08]">
                  React / CSS
                </span>
              </div>
              <div>
                <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  Frontend Studio
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5 leading-relaxed min-h-[48px]">
                  Resolve component layout breakage, responsive viewport collapses, Flexbox/Grid alignment errors, and state synchronization bugs.
                </p>
              </div>
            </div>
            <div className="pt-3 mt-3 border-t border-slate-100 dark:border-white/[0.06]">
              <Link
                to="/design-challenges"
                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center justify-between group/link py-0.5"
              >
                <span>Explore Frontend Studio</span>
                <ChevronRight className="w-3.5 h-3.5 group-hover/link:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Engineering Workflow Guide - Standard Procedure */}
      <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
        <div className="mb-3.5">
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400 block mb-0.5">Standard Procedure</span>
          <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
            Debugging Workflow
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            {
              step: '01',
              title: 'Reproduce Defect',
              desc: 'Review the bug report scenario, examine failing test assertions, and inspect suspected files.'
            },
            {
              step: '02',
              title: 'Isolate Root Cause',
              desc: 'Trace logic branch conditions, evaluate edge cases, and run diagnostic test suites.'
            },
            {
              step: '03',
              title: 'Implement Fix',
              desc: 'Refactor broken functions in the Monaco IDE and re-run unit tests until 100% pass.'
            },
            {
              step: '04',
              title: 'Verify & Benchmark',
              desc: 'Submit solution for backend evaluation, earn verified XP, and update skill matrix rankings.'
            }
          ].map((item) => (
            <div key={item.step} className="p-3.5 rounded-lg border border-slate-200/70 dark:border-white/[0.06] bg-slate-50/60 dark:bg-white/[0.02] space-y-1.5 hover:border-slate-300 dark:hover:border-white/[0.12] transition-colors">
              <span className="text-xs font-mono font-medium text-blue-600 dark:text-blue-400 block">{item.step}</span>
              <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100">{item.title}</h3>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Adaptive Learning & Career Direction Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Adaptive System */}
        <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col justify-between space-y-3.5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
          <div className="space-y-1.5">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 block mb-0.5">Skill Profile</span>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Personalized Recommendation Engine
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              BuggyMan indexes your declared strengths, areas for improvement, and submission history to recommend challenges targeting your skill gaps.
            </p>
          </div>
          <Link
            to="/profile"
            className="button-secondary text-xs self-start"
          >
            <User className="w-3.5 h-3.5" />
            <span>View Skill Matrix</span>
          </Link>
        </div>

        {/* Career Insights */}
        <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 flex flex-col justify-between space-y-3.5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
          <div className="space-y-1.5">
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 block mb-0.5">Market Alignment</span>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              Career Role Suitability
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Match your verified problem-solving capabilities against industry hiring benchmarks for Backend, Full Stack, Data, and Frontend engineering roles.
            </p>
          </div>
          <Link
            to="/career-insights"
            className="button-secondary text-xs self-start"
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Open Career Insights</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
