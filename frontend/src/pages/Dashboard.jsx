import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Bug, 
  Code2, 
  Database, 
  Palette, 
  Sparkles, 
  ArrowRight, 
  Search, 
  CheckCircle2, 
  TrendingUp, 
  User, 
  Briefcase, 
  Zap, 
  HelpCircle,
  Play,
  Layers,
  ShoppingBag,
  Gift
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
  const isNewUser = solvedCount === 0;

  return (
    <div className="max-w-6xl mx-auto space-y-12 py-4 animate-fade-in relative">
      <OnboardingModal 
        isOpen={showOnboardingModal} 
        onClose={() => setShowOnboardingModal(false)} 
      />

      {/* 1. Hero Section */}
      <div className="glass-panel p-8 md:p-12 rounded-3xl border border-cyan-500/30 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-slate-100 relative overflow-hidden space-y-6">
        <div className="flex items-center gap-2.5">
          <span className="badge badge-cyan flex items-center gap-1.5 px-3 py-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI DEBUGGER LAB</span>
          </span>
          <span className="text-xs text-slate-400 font-medium">Hands-on Engineering Practice</span>
        </div>

        <div className="space-y-3 max-w-3xl">
          <h1 className="font-heading font-black text-3xl md:text-5xl text-slate-100 tracking-tight leading-tight">
            Welcome to <span className="text-cyan-400">BuggyMan</span>
          </h1>
          <p className="text-base md:text-lg text-slate-300 font-medium leading-relaxed">
            Find bugs. Fix real-world software problems. Build practical engineering skills.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <Link
            to="/challenges"
            className="button-primary px-6 py-3 text-sm font-bold flex items-center gap-2"
          >
            <span>Start Debugging</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <button
            onClick={scrollToExplore}
            className="button-secondary px-6 py-3 text-sm font-semibold flex items-center gap-2"
          >
            <span>Explore BuggyMan</span>
          </button>
        </div>
      </div>

      {/* 2. Explore BuggyMan (Three Feature Cards) */}
      <div id="explore-section" className="space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-500 font-heading block">Explore BuggyMan</span>
          <h2 className="font-heading font-bold text-xl text-slate-800 dark:text-[#F0F2F4] mt-1">Three Specialized Debugging Arenas</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Code Challenges */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-[#292E33] hover:border-cyan-500/40 transition-all duration-200 flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 w-fit">
                <Code2 className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h3 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-500 transition-colors">
                  Code Challenges
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Debug real-world software, backend logic, Python APIs, and Node.js backend issues.
                </p>
              </div>
            </div>
            <Link
              to="/challenges"
              className="text-xs font-bold text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5 hover:gap-2.5 transition-all"
            >
              <span>Explore Code Challenges</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Card 2: SQL Lab */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-[#292E33] hover:border-cyan-500/40 transition-all duration-200 flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 w-fit">
                <Database className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h3 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-500 transition-colors">
                  SQL Lab
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Find and fix real-world database queries, JOIN conditions, GROUP BY aggregations, and CTE performance bugs.
                </p>
              </div>
            </div>
            <Link
              to="/sql-challenges"
              className="text-xs font-bold text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5 hover:gap-2.5 transition-all"
            >
              <span>Explore SQL Lab</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Card 3: Frontend Studio */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-[#292E33] hover:border-cyan-500/40 transition-all duration-200 flex flex-col justify-between space-y-6 group">
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 w-fit">
                <Palette className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h3 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-500 transition-colors">
                  Frontend Studio
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Debug UI responsiveness, Flexbox/Grid layouts, glassmorphism CSS, state mutations, and component styling.
                </p>
              </div>
            </div>
            <Link
              to="/design-challenges"
              className="text-xs font-bold text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5 hover:gap-2.5 transition-all"
            >
              <span>Explore Frontend Studio</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* 3. How BuggyMan Works */}
      <div className="space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-500 font-heading block">Workflow</span>
          <h2 className="font-heading font-bold text-xl text-slate-800 dark:text-[#F0F2F4] mt-1">How BuggyMan Works</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              step: '01',
              title: 'Find the Bug',
              desc: 'Understand the real-world scenario and read suspected component files.'
            },
            {
              step: '02',
              title: 'Investigate',
              desc: 'Trace the issue, analyze error output, and isolate what is failing.'
            },
            {
              step: '03',
              title: 'Fix It',
              desc: 'Implement the correct solution directly in Monaco IDE and run backend test suites.'
            },
            {
              step: '04',
              title: 'Build Your Skills',
              desc: 'BuggyMan analyzes your performance and adapts future challenge recommendations.'
            }
          ].map((item) => (
            <div key={item.step} className="glass-panel p-5 rounded-2xl border border-slate-200 dark:border-[#292E33] space-y-3">
              <span className="text-xs font-extrabold text-cyan-500 font-mono tracking-widest block">{item.step}</span>
              <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">{item.title}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Personalized Learning Section */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-200 dark:border-[#292E33] space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-500 font-heading block">Personalized Engine</span>
            <h2 className="font-heading font-bold text-xl text-slate-800 dark:text-[#F0F2F4]">Challenges That Adapt to You</h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              BuggyMan learns from your strengths, weaknesses, and problem-solving performance to personalize the challenges you receive across all three arenas.
            </p>
          </div>
          <Link
            to="/profile"
            className="button-primary text-xs px-5 py-2.5 flex items-center justify-center gap-2 whitespace-nowrap self-start md:self-auto"
          >
            <User className="w-4 h-4" />
            <span>View My Profile</span>
          </Link>
        </div>

        {/* Visual Flow Diagram */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-center pt-2">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-xs font-semibold text-slate-700 dark:text-slate-300">
            Strengths & Weaknesses
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-xs font-semibold text-slate-700 dark:text-slate-300">
            Problems You Solve
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-xs font-semibold text-slate-700 dark:text-slate-300">
            Performance Analysis
          </div>
          <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-xs font-bold text-cyan-600 dark:text-cyan-400">
            Personalized Challenges
          </div>
        </div>
      </div>

      {/* 5. Career Direction Section */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-200 dark:border-[#292E33] space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-500 font-heading block">Career Insights</span>
            <h2 className="font-heading font-bold text-xl text-slate-800 dark:text-[#F0F2F4]">Turn Your Skills into Career Direction</h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Discover software engineering roles that align with your demonstrated skill matrix and identify high-impact areas to improve.
            </p>
          </div>
          <Link
            to="/career-insights"
            className="button-primary text-xs px-5 py-2.5 flex items-center justify-center gap-2 whitespace-nowrap self-start md:self-auto"
          >
            <Briefcase className="w-4 h-4" />
            <span>Explore Career Insights</span>
          </Link>
        </div>
      </div>

      {/* 6. BugBytes Store & Money-Back Rewards Widget */}
      <div className="glass-panel p-6 md:p-8 rounded-3xl border border-amber-500/30 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 text-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="badge badge-amber text-[10px] font-bold uppercase tracking-wider">
              AI HINT CREDITS & REWARDS
            </span>
            <span className="text-[11px] text-amber-400 font-bold flex items-center gap-1">
              <Bug className="w-3.5 h-3.5" />
              <span>{profile?.bugbytes_balance ?? profile?.bugbytesBalance ?? 0} BugBytes Available</span>
            </span>
          </div>
          <h2 className="font-heading font-bold text-xl text-slate-100">
            BugBytes Store + Challenge-Based Money-Back Rewards
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Need AI hints for tricky debugging sessions? Purchase mock BugBytes packages and recover 100% of your simulated purchase through coding missions.
          </p>
        </div>
        <Link
          to="/store"
          className="button-primary bg-amber-600 hover:bg-amber-500 text-xs px-5 py-2.5 flex items-center justify-center gap-2 whitespace-nowrap self-start md:self-auto font-bold shadow-lg"
        >
          <ShoppingBag className="w-4 h-4" />
          <span>Open BugBytes Store</span>
        </Link>
      </div>

      {/* 6. Getting Started / Continuation CTA */}
      <div className="glass-panel p-8 rounded-3xl border border-cyan-500/30 bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 text-center space-y-4">
        <h3 className="font-heading font-bold text-xl text-slate-100">
          {isNewUser ? 'Ready to start debugging?' : 'Continue your learning journey'}
        </h3>
        <p className="text-xs text-slate-300 max-w-lg mx-auto leading-relaxed">
          {isNewUser 
            ? 'Dive into your first interactive code challenge and start building real-world software troubleshooting skills.'
            : 'Pick up right where you left off or explore customized challenges tailored to your latest performance.'}
        </p>
        <div className="pt-2">
          <Link
            to="/challenges"
            className="button-primary px-6 py-3 text-xs font-bold inline-flex items-center gap-2"
          >
            <span>{isNewUser ? 'Start Your First Challenge' : 'Continue Debugging'}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
