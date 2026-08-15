import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Trophy, 
  Flame, 
  CheckCircle2, 
  TrendingUp, 
  Zap, 
  Play,
  ArrowRight,
  Shield,
  Clock,
  Sparkles,
  Code2,
  Target,
  Award,
  XCircle,
  FileCheck,
  Activity,
  Layers,
  HelpCircle
} from 'lucide-react';
import ProgressBar from '../components/ProgressBar';
import LoadingSpinner from '../components/LoadingSpinner';
import OnboardingModal from '../components/OnboardingModal';
import { authService } from '../services/authService';
import { challengeService } from '../services/challengeService';

export default function Dashboard({ user, addToast }) {
  const [profile, setProfile] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [mlRecommendations, setMlRecommendations] = useState([]);
  const [showOnboardingModal, setShowOnboardingModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [profData, chalData, leaderData, analyticsData, subData, recData] = await Promise.all([
          authService.getCurrentUser(),
          challengeService.getChallenges(),
          challengeService.getLeaderboard(),
          challengeService.getAnalytics(),
          challengeService.getUserSubmissions().catch(() => []),
          challengeService.getRecommendations(3).catch(() => [])
        ]);

        setProfile(profData);
        setChallenges(chalData || []);
        setLeaderboard((leaderData || []).slice(0, 3));
        setAnalytics(analyticsData);
        setRecentSubmissions((subData || []).slice(0, 5));
        setMlRecommendations(recData || []);
      } catch (err) {
        if (typeof addToast === 'function') {
          addToast('Error loading dashboard metrics.', 'error');
        }
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, [addToast]);

  useEffect(() => {
    const onboardingDone = localStorage.getItem('buggyman_onboarding_completed');
    if (!onboardingDone) {
      setShowOnboardingModal(true);
    }
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Active challenge resumption logic
  const lastSub = recentSubmissions[0];
  const activeChallengeId = lastSub ? String(lastSub.challengeId) : (challenges[0] ? String(challenges[0].id) : '1');
  const activeChallenge = challenges.find(c => String(c.id) === activeChallengeId) || challenges[0];
  const recommendedChallenges = (mlRecommendations && mlRecommendations.length > 0)
    ? mlRecommendations.slice(0, 2)
    : challenges.filter(c => String(c.id) !== activeChallengeId).slice(0, 2);

  return (
    <div className="space-y-8 animate-fade-in relative">
      <OnboardingModal 
        isOpen={showOnboardingModal} 
        onClose={() => setShowOnboardingModal(false)} 
      />

      {/* Hero Welcome Banner */}
      <div className="relative rounded-2xl p-8 overflow-hidden bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] shadow-sm">
        <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />
        <div className="absolute inset-0 bg-radial-gradient opacity-60 pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span className="badge badge-cyan">
                <Sparkles className="w-3 h-3 text-cyan-500" />
                <span>AI Debugger Engine Active</span>
              </span>
              <span className="badge badge-amber">
                <Flame className="w-3 h-3 text-amber-500 fill-amber-500" />
                <span>{profile?.streak || 0}-Day Streak</span>
              </span>
            </div>
            <h1 className="font-heading font-extrabold text-3xl md:text-4xl text-slate-800 dark:text-[#F0F2F4] leading-tight">
              Welcome back, <span className="text-cyan-600 dark:text-cyan-400">{profile?.name}</span>
            </h1>
            <p className="text-slate-600 dark:text-slate-400 text-sm max-w-xl leading-relaxed">
              Identify bugs, repair broken logic, and elevate your full-stack engineering proficiency.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <button
              onClick={() => setShowOnboardingModal(true)}
              className="button-secondary font-semibold text-xs px-4 py-3 flex items-center gap-2"
            >
              <HelpCircle className="w-4 h-4 text-cyan-500" />
              <span>Platform Tour</span>
            </button>
            <Link to="/challenges" className="button-primary font-semibold text-sm px-6 py-3 whitespace-nowrap group">
              <Zap className="w-4 h-4 fill-white group-hover:scale-110 transition-transform" />
              <span>Start New Challenge</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Grid Dashboard Analytics Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Profile Card, Unlocked Badges & Analytics */}
        <div className="lg:col-span-1 space-y-6">
          {/* User profile card */}
          <div className="glass-card p-6 rounded-xl relative overflow-hidden">
            <div className="flex items-center gap-4 mb-5">
              <img 
                src={profile?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'} 
                alt={profile?.name} 
                className="w-14 h-14 rounded-xl object-cover ring-2 ring-cyan-500/40"
              />
              <div className="min-w-0 flex-1">
                <h3 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4] truncate">{profile?.name}</h3>
                <p className="text-xs text-slate-500 truncate">@{profile?.username}</p>
                <p className="text-[10px] text-cyan-500 font-bold mt-1 uppercase tracking-wider truncate">{profile?.college}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-200 dark:border-[#292E33] text-center">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Total XP</span>
                <p className="text-lg font-heading font-extrabold text-cyan-600 dark:text-cyan-400">{profile?.totalScore || 0}</p>
              </div>
              <div className="space-y-1 border-x border-slate-200 dark:border-[#292E33]">
                <div className="flex items-center justify-center gap-1 text-amber-500">
                  <Flame className="w-4 h-4 fill-amber-500 shrink-0" />
                  <p className="text-lg font-heading font-extrabold text-slate-800 dark:text-[#F0F2F4]">{profile?.streak || 0}</p>
                </div>
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Streak</span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Solved</span>
                <p className="text-lg font-heading font-extrabold text-emerald-600 dark:text-emerald-400">{profile?.challengesSolved || 0}</p>
              </div>
            </div>
          </div>

          {/* Progress Analytics Card */}
          <div className="glass-card p-6 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Progress Statistics</h3>
              <TrendingUp className="w-4 h-4 text-emerald-500" />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-1">
              <div className="p-3 bg-slate-50 dark:bg-[#1B1F23] rounded-lg border border-slate-200 dark:border-[#292E33] text-center">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Accuracy Rate</span>
                <span className="text-lg font-heading font-extrabold text-emerald-600 dark:text-emerald-400">{analytics?.accuracy || 100}%</span>
              </div>

              <div className="p-3 bg-slate-50 dark:bg-[#1B1F23] rounded-lg border border-slate-200 dark:border-[#292E33] text-center">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total Attempts</span>
                <span className="text-lg font-heading font-extrabold text-cyan-600 dark:text-cyan-400">{analytics?.totalAttempts || recentSubmissions.length || 1}</span>
              </div>
            </div>

            {/* Difficulty Breakdown */}
            <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-[#292E33]">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Difficulty Progression</span>
              <div className="space-y-2">
                {analytics?.difficultyProgression?.map((item) => (
                  <div key={item.name} className="flex justify-between items-center text-xs">
                    <span className="text-slate-600 dark:text-slate-400 font-medium">{item.name}</span>
                    <span className="text-slate-800 dark:text-[#F0F2F4] font-bold">{item.completed} Solved</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Unlocked Badges Carousel */}
          <div className="glass-card p-6 rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Unlocked Badges</h3>
              <Shield className="w-4 h-4 text-amber-500" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              {profile?.badges && profile.badges.length > 0 ? (
                profile.badges.map((badge, idx) => (
                  <div key={badge.name || idx} className="p-3 rounded-lg bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] flex items-center gap-2.5">
                    <span className="text-xl">{badge.icon || '🏅'}</span>
                    <div className="min-w-0 flex-1">
                      <h5 className="text-xs font-bold text-slate-800 dark:text-[#F0F2F4] truncate">{badge.name}</h5>
                      <span className="text-[9px] text-slate-500 block truncate">{badge.date || 'Unlocked'}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic col-span-2 text-center py-2">Solve your first challenge to unlock badges!</p>
              )}
            </div>
          </div>
        </div>

        {/* Center Column: Resume Workspace & Recent Submissions */}
        <div className="lg:col-span-1 space-y-6">
          {/* Active Workspace / Resume Challenge Banner */}
          {activeChallenge && (
            <div className="relative rounded-xl border border-cyan-500/30 bg-white dark:bg-[#15181B] p-6 overflow-hidden shadow-sm">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                <Clock className="w-20 h-20 text-cyan-500" />
              </div>
              <div className="space-y-3 relative z-10">
                <span className="badge badge-cyan">CONTINUE SESSION</span>
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">{activeChallenge.title}</h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed line-clamp-2">
                  {activeChallenge.description}
                </p>
                <div className="flex justify-between items-center pt-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">{activeChallenge.technology} • {activeChallenge.timeEstimate}</span>
                  <Link 
                    to={`/challenge/${activeChallenge.id}`} 
                    className="flex items-center gap-1.5 text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline transition-colors group"
                  >
                    <span>Resume Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* Recent Submissions Panel */}
          <div className="glass-card p-6 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4.5 h-4.5 text-cyan-500" />
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Recent Submissions</h3>
              </div>
              <span className="text-[10px] text-slate-500 font-bold uppercase">{recentSubmissions.length} Recorded</span>
            </div>

            <div className="space-y-3">
              {recentSubmissions.length > 0 ? (
                recentSubmissions.map((sub) => (
                  <div 
                    key={sub.id} 
                    className="p-3.5 rounded-lg bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] flex items-center justify-between text-xs transition-colors"
                  >
                    <div className="space-y-1 min-w-0 pr-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-800 dark:text-[#F0F2F4] truncate">{sub.challengeTitle || `Challenge #${sub.challengeId}`}</span>
                        {sub.attemptNumber && (
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono">#{sub.attemptNumber}</span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500 block">
                        {sub.createdAt ? new Date(sub.createdAt).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      {sub.success ? (
                        <span className="badge badge-emerald">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>PASSED</span>
                        </span>
                      ) : (
                        <span className="badge badge-rose">
                          <XCircle className="w-3 h-3" />
                          <span>FAILED</span>
                        </span>
                      )}
                      <Link 
                        to={`/challenge/${sub.challengeId}`}
                        className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 p-1"
                        title="View Challenge"
                      >
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic text-center py-4">No submissions recorded yet. Start a challenge to submit code!</p>
              )}
            </div>
          </div>

          {/* Recommended challenges list */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Recommended Debugging</h3>
              <Code2 className="w-4 h-4 text-slate-400" />
            </div>
            <div className="space-y-4">
              {recommendedChallenges.map((chal) => (
                <div key={chal.id} className="glass-card p-5 rounded-xl flex flex-col justify-between gap-3 transition-colors">
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <span className={`badge ${
                        chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                      }`}>
                        {chal.difficulty}
                      </span>
                      <span className="text-[10px] text-slate-500 font-bold uppercase">{chal.technology}</span>
                    </div>
                    <h4 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">{chal.title}</h4>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">{chal.description}</p>
                  </div>
                  <div className="flex items-center justify-between border-t border-slate-200 dark:border-[#292E33] pt-3 mt-1">
                    <span className="text-[10px] font-bold text-slate-500 uppercase">Est. Time: {chal.timeEstimate}</span>
                    <Link 
                      to={`/challenge/${chal.id}`}
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline transition-colors"
                    >
                      <span>Start Debugging</span>
                      <Play className="w-3 h-3 fill-current" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Leaderboard preview & Recent Activity */}
        <div className="lg:col-span-1 space-y-6">
          {/* Leaderboard Preview */}
          <div className="glass-card p-6 rounded-xl">
            <div className="flex justify-between items-center mb-5">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-amber-500" />
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Top Debuggers</h3>
              </div>
              <Link to="/leaderboard" className="text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:underline">
                View All
              </Link>
            </div>
            
            <div className="space-y-3">
              {leaderboard.map((item, idx) => (
                <div 
                  key={item.username || idx} 
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] transition-all"
                >
                  <div className="flex items-center gap-3">
                    <span className={`w-6 h-6 rounded-md flex items-center justify-center font-bold text-xs ${
                      idx === 0 
                        ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30' 
                        : idx === 1 
                        ? 'bg-slate-300/40 text-slate-700 dark:text-slate-300 border border-slate-400/30' 
                        : 'bg-amber-700/20 text-amber-700 dark:text-amber-500 border border-amber-700/30'
                    }`}>
                      {idx + 1}
                    </span>
                    <div>
                      <h4 className="text-xs font-bold text-slate-800 dark:text-[#F0F2F4]">{item.name}</h4>
                      <p className="text-[9px] text-slate-500 uppercase font-bold">{item.college}</p>
                    </div>
                  </div>
                  <span className="text-xs font-extrabold text-slate-800 dark:text-[#F0F2F4]">{item.score} XP</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity Timeline */}
          <div className="glass-card p-6 rounded-xl">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-500" />
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Recent Activity</h3>
              </div>
            </div>
            
            <div className="space-y-4">
              {profile?.activities && profile.activities.length > 0 ? (
                profile.activities.map((act, idx) => (
                  <div key={act.id || idx} className="flex gap-3 text-xs leading-relaxed">
                    <div className="w-2 h-2 rounded-full bg-cyan-500 mt-1.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-slate-700 dark:text-slate-300 font-medium">{act.text}</p>
                      <span className="text-[10px] text-slate-500 block mt-0.5">{act.time || 'Just now'}</span>
                    </div>
                    {act.xp && (
                      <span className="badge badge-emerald">
                        +{act.xp} XP
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic text-center py-4">No recent activity. Solve a bug to earn activity logs!</p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
