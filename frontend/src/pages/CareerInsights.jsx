import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Briefcase, 
  Sparkles, 
  CheckCircle2, 
  Target, 
  TrendingUp, 
  ArrowRight, 
  Award,
  Info,
  Clock,
  Layers,
  HelpCircle,
  Code2,
  GraduationCap,
  Edit3,
  User as UserIcon,
  Flame,
  Zap,
  Compass
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ProgressBar from '../components/ProgressBar';
import { challengeService } from '../services/challengeService';

export default function CareerInsights({ user, addToast }) {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState(null);
  const [selectedRole, setSelectedRole] = useState(null);

  useEffect(() => {
    async function loadCareerInsights() {
      try {
        setLoading(true);
        const data = await challengeService.getCareerInsights();
        setInsights(data);
        if (data && data.topMatch) {
          setSelectedRole(data.topMatch);
        }
      } catch (err) {
        if (addToast) addToast('Failed to load career suitability insights.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadCareerInsights();
  }, [addToast]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const currentUser = insights?.userProfile || user;
  const topMatch = insights?.topMatch;
  const roles = insights?.roles || [];
  const isInsufficientData = insights?.isInsufficientData || false;
  const currentRole = selectedRole || topMatch;

  return (
    <div className="max-w-6xl mx-auto py-6 space-y-8 animate-fade-in px-4">
      {/* Page Title & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#292E33] pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-cyan text-[10px] uppercase font-bold">CAREER ENGINE</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Demonstrated Skills & Market Insights</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Briefcase className="w-7 h-7 text-cyan-500" />
            <span>Career Role Suitability & Skill Gaps</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Personalized role alignment based on your profile strengths, career interests, and verified debugging benchmarks.
          </p>
        </div>

        <Link
          to="/profile"
          className="button-secondary text-xs px-4 py-2 flex items-center gap-2 self-start md:self-auto"
        >
          <Award className="w-4 h-4 text-cyan-400" />
          <span>View My Skill Matrix</span>
        </Link>
      </div>

      {/* Personalized User Profile Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-200 dark:border-[#292E33] bg-white/70 dark:bg-slate-900/60 backdrop-blur-md space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <img
              src={currentUser?.avatar || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'}
              alt={currentUser?.name || 'Developer'}
              className="w-14 h-14 rounded-2xl object-cover border-2 border-cyan-500/40 shadow-sm shrink-0"
            />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-slate-800 dark:text-[#F0F2F4]">
                  {currentUser?.name || currentUser?.username || 'Your Personalized Profile'}
                </h2>
                <span className="badge badge-cyan text-[10px] font-bold">Tailored For You</span>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mt-1">
                <span className="flex items-center gap-1">
                  <GraduationCap className="w-3.5 h-3.5 text-cyan-500 shrink-0" />
                  <span>{currentUser?.college || 'Student Developer'}</span>
                </span>
                <span className="text-slate-300 dark:text-slate-600">•</span>
                <span className="flex items-center gap-1 text-amber-500 font-semibold">
                  <Zap className="w-3.5 h-3.5 shrink-0" />
                  <span>{currentUser?.totalScore || 0} XP</span>
                </span>
                <span className="text-slate-300 dark:text-slate-600">•</span>
                <span className="text-slate-600 dark:text-slate-300 font-medium">
                  {currentUser?.challengesSolved || 0} Solved
                </span>
              </div>
            </div>
          </div>

          <Link
            to="/profile"
            className="button-secondary text-xs font-semibold px-3.5 py-1.5 flex items-center gap-1.5 self-start sm:self-auto rounded-xl hover:border-cyan-500/40 transition-all"
          >
            <Edit3 className="w-3.5 h-3.5 text-cyan-500" />
            <span>Edit Profile & Preferences</span>
          </Link>
        </div>

        {/* Personalized Pillars: Strengths, Interests, Areas to Improve */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3 border-t border-slate-100 dark:border-slate-800/80">
          {/* Declared Strengths */}
          <div className="p-3.5 rounded-2xl bg-emerald-50/70 dark:bg-emerald-500/5 border border-emerald-500/20 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Your Profile Strengths</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {currentUser?.strengths && currentUser.strengths.length > 0 ? (
                currentUser.strengths.map((str) => (
                  <span key={str} className="px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[10px] font-semibold border border-emerald-500/30">
                    {str}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No strengths selected yet</span>
              )}
            </div>
          </div>

          {/* Declared Career Interests */}
          <div className="p-3.5 rounded-2xl bg-cyan-50/70 dark:bg-cyan-500/5 border border-cyan-500/20 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">
              <Compass className="w-3.5 h-3.5" />
              <span>Target Career Interests</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {currentUser?.interests && currentUser.interests.length > 0 ? (
                currentUser.interests.map((int) => (
                  <span key={int} className="px-2 py-0.5 rounded-lg bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-[10px] font-semibold border border-cyan-500/30">
                    {int}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No target interests selected yet</span>
              )}
            </div>
          </div>

          {/* Declared Weaknesses / Areas to Improve */}
          <div className="p-3.5 rounded-2xl bg-amber-50/70 dark:bg-amber-500/5 border border-amber-500/20 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Areas to Improve</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {currentUser?.weaknesses && currentUser.weaknesses.length > 0 ? (
                currentUser.weaknesses.map((wk) => (
                  <span key={wk} className="px-2 py-0.5 rounded-lg bg-amber-500/10 text-amber-700 dark:text-amber-300 text-[10px] font-semibold border border-amber-500/30">
                    {wk}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No growth areas specified</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Insufficient Data Banner for Cold-Start Users */}
      {isInsufficientData && (
        <div className="glass-panel p-6 rounded-2xl border border-amber-500/30 bg-amber-500/5 space-y-3">
          <div className="flex items-center gap-2.5 text-amber-500 font-bold text-sm">
            <Info className="w-5 h-5 shrink-0" />
            <span>Initial Profile-Based Recommendations</span>
          </div>
          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed max-w-3xl">
            {insights?.dataMessage || 'Your career recommendations are calculated using your declared strengths, interests, and profile preferences. Solve challenges to build real performance metrics!'}
          </p>
          <div className="pt-1">
            <Link to="/challenges" className="button-primary text-xs font-bold px-4 py-2 inline-flex items-center gap-2">
              <span>Start Debugging Challenges</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}

      {/* Top Role Match Hero Card */}
      {topMatch && (
        <div className="glass-panel p-8 rounded-3xl border border-slate-200 dark:border-cyan-500/30 bg-gradient-to-br from-white via-cyan-50/40 to-slate-50 dark:from-slate-900 dark:via-slate-950 dark:to-slate-900 space-y-6 relative overflow-hidden shadow-sm dark:shadow-xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-1/4 -mb-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3 max-w-2xl">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="badge badge-emerald text-[10px] font-extrabold uppercase px-2.5 py-1">
                  🥇 TOP ROLE MATCH
                </span>
                {topMatch.isInterestMatch && (
                  <span className="badge badge-cyan text-[10px] font-extrabold uppercase px-2.5 py-1">
                    🎯 YOUR TARGET CAREER GOAL
                  </span>
                )}
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{topMatch.matchLabel}</span>
              </div>
              <h2 className="font-heading font-extrabold text-2xl md:text-3xl text-slate-900 dark:text-slate-100">
                {topMatch.title}
              </h2>
              <p className="text-xs md:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                {topMatch.explanation}
              </p>
            </div>

            {/* Score Ring / Metrics */}
            <div className="flex items-center gap-4 shrink-0 self-start md:self-auto">
              <div className="text-center p-4 rounded-2xl bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm min-w-[110px]">
                <span className="text-3xl font-black text-cyan-600 dark:text-cyan-400 font-heading block">{topMatch.matchScore}%</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">Skill Match</span>
              </div>
              <div className="text-center p-4 rounded-2xl bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm min-w-[110px]">
                <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400 font-heading block">{topMatch.marketDemand}</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider">Market Demand</span>
              </div>
            </div>
          </div>

          {/* Market Metadata Source & Date */}
          <div className="relative z-10 flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800/80 pt-4">
            <div className="flex items-center gap-4">
              <span>Market Trend: <strong className="text-slate-800 dark:text-slate-200">{topMatch.marketTrend}</strong></span>
              <span>Source: <strong className="text-slate-800 dark:text-slate-200">{topMatch.source}</strong></span>
            </div>
            <span>Data updated: <strong className="text-slate-700 dark:text-slate-300">{topMatch.lastUpdated}</strong></span>
          </div>
        </div>
      )}

      {/* Main Grid: Selected Role Deep Dive */}
      {currentRole && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-500" />
                <span>Role Breakdown: {currentRole.title}</span>
              </h3>
              <p className="text-xs text-slate-500 font-medium">Detailed skill breakdown and gap practice for this role</p>
            </div>
            {currentRole.isInterestMatch && (
              <span className="badge badge-cyan text-[11px] font-bold self-start sm:self-auto">
                🎯 Aligned with your stated career interest
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Demonstrated Relevant Strengths */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-[#292E33] space-y-4">
              <h4 className="font-heading font-bold text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2 border-b border-slate-200 dark:border-[#292E33] pb-3">
                <CheckCircle2 className="w-4.5 h-4.5" />
                <span>Relevant Strengths</span>
              </h4>
              <div className="space-y-2.5">
                {currentRole.demonstratedStrengths && currentRole.demonstratedStrengths.length > 0 ? (
                  currentRole.demonstratedStrengths.map((str) => (
                    <div key={str} className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33]">
                      <span className="text-xs font-semibold text-slate-700 dark:text-slate-200">{str}</span>
                      <span className="badge badge-emerald text-[10px]">VERIFIED</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 italic">No specific strengths recorded yet.</p>
                )}
              </div>
            </div>

            {/* Skill Gaps & Practice CTA */}
            <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-200 dark:border-[#292E33] space-y-5">
              <h4 className="font-heading font-bold text-sm text-rose-600 dark:text-rose-400 flex items-center gap-2 border-b border-slate-200 dark:border-[#292E33] pb-3">
                <Target className="w-4.5 h-4.5" />
                <span>Skill Gaps & Recommended Challenge Practice</span>
              </h4>

              <div className="space-y-4">
                {currentRole.skillGaps?.map((gap) => (
                  <div key={gap.skill} className="space-y-1.5 p-3 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33]">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-700 dark:text-slate-300 flex items-center gap-2">
                        <span>Focus Area: {gap.skill}</span>
                        {gap.isDeclaredWeakness && (
                          <span className="text-[10px] text-amber-500 font-normal">
                            (Marked in your profile as an area to improve)
                          </span>
                        )}
                      </span>
                      <span className="text-slate-500 font-mono">{gap.proficiency}% Proficiency</span>
                    </div>
                    <ProgressBar value={gap.proficiency} max={100} color={gap.proficiency >= 50 ? 'indigo' : 'rose'} />
                  </div>
                ))}
              </div>

              {/* Recommended Unsolved Challenges for this Role's Gap */}
              {currentRole.recommendedChallenges && currentRole.recommendedChallenges.length > 0 && (
                <div className="space-y-3 pt-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 block">Recommended Practice Challenges to Boost Match:</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {currentRole.recommendedChallenges.map((chal) => (
                      <Link
                        key={chal.id}
                        to={`/challenge/${chal.id}`}
                        className="p-3.5 rounded-xl bg-white dark:bg-[#0E1012] border border-slate-200 dark:border-[#292E33] hover:border-cyan-500/50 transition-all flex items-center justify-between group"
                      >
                        <div className="space-y-1 min-w-0 pr-2">
                          <h5 className="font-heading font-bold text-xs text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-500 truncate">
                            {chal.title}
                          </h5>
                          <p className="text-[10px] text-slate-500 truncate">{chal.reason}</p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-cyan-500 group-hover:translate-x-1 transition-all shrink-0" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Ranked Software Engineering Roles List */}
      <div className="space-y-6">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-500 font-heading block">All Analyzed Roles</span>
          <h3 className="font-heading font-bold text-xl text-slate-800 dark:text-[#F0F2F4] mt-1">Software Engineering Role Rankings</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div
              key={role.id}
              onClick={() => setSelectedRole(role)}
              className={`glass-panel p-6 rounded-2xl border transition-all cursor-pointer space-y-4 relative ${
                selectedRole?.id === role.id
                  ? 'border-cyan-500 ring-2 ring-cyan-500/20 shadow-lg'
                  : 'border-slate-200 dark:border-[#292E33] hover:border-slate-400 dark:hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <h4 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">{role.title}</h4>
                  {role.isInterestMatch && (
                    <span className="badge badge-cyan text-[9px] font-bold">
                      🎯 YOUR TARGET GOAL
                    </span>
                  )}
                </div>
                <span className={`badge shrink-0 ${
                  role.matchScore >= 75 ? 'badge-emerald' : role.matchScore >= 55 ? 'badge-indigo' : 'badge-amber'
                }`}>
                  {role.matchLabel}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <div className="space-y-0.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase block">Skill Match</span>
                  <span className="text-lg font-extrabold text-cyan-500 font-heading">{role.matchScore}%</span>
                </div>
                <div className="space-y-0.5 text-right">
                  <span className="text-[10px] text-slate-500 font-bold uppercase block">Market Demand</span>
                  <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{role.marketDemand}</span>
                </div>
              </div>

              {role.profileWeaknesses && role.profileWeaknesses.length > 0 && (
                <div className="text-[10px] text-amber-500 font-medium">
                  ⚠️ Contains growth area: {role.profileWeaknesses.join(', ')}
                </div>
              )}

              <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-[#292E33] pt-3 flex items-center justify-between">
                <span>Top Gap: <strong>{role.skillGaps?.[0]?.skill || 'None'}</strong></span>
                <span className="text-cyan-500 font-semibold flex items-center gap-1">
                  <span>View Details</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Data Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-100 dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] text-center text-xs text-slate-500 space-y-1">
        <p className="font-medium text-slate-600 dark:text-slate-400">{insights?.disclaimer || 'Market insights are based on the latest available market data and may change over time.'}</p>
        <p className="text-[10px]">BuggyMan evaluates demonstrated skills dynamically. Update your profile strengths or continue solving challenges to refine your match scores.</p>
      </div>
    </div>
  );
}
