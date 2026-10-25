import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Briefcase, 
  CheckCircle2, 
  Target, 
  ArrowRight, 
  Award,
  Info,
  GraduationCap,
  Edit3,
  Zap,
  Compass,
  AlertCircle
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
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Page Title & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#30363D] pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="badge badge-cyan font-mono text-[11px]">CAREER SUITABILITY</span>
            <span className="badge badge-gray font-mono text-[10px]">MARKET BENCHMARKS</span>
          </div>
          <h1 className="font-heading font-bold text-2xl text-slate-900 dark:text-[#E6EDF3] tracking-tight">
            Career Role Suitability & Skill Gaps
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Deterministic role compatibility derived from your profile benchmarks and verified debugging performance.
          </p>
        </div>

        <Link
          to="/profile"
          className="button-secondary text-xs px-3 py-1.5 flex items-center gap-1.5 self-start md:self-auto"
        >
          <Award className="w-3.5 h-3.5 text-cyan-500" />
          <span>Skill Profile</span>
        </Link>
      </div>

      {/* User Profile Overview */}
      <div className="p-4 rounded-md border border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <img
              src={currentUser?.avatar || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'}
              alt={currentUser?.name || 'Developer'}
              className="w-11 h-11 rounded object-cover border border-slate-300 dark:border-[#30363D] shrink-0"
            />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-slate-900 dark:text-[#E6EDF3]">
                  {currentUser?.name || currentUser?.username || 'Candidate Profile'}
                </h2>
                <span className="badge badge-cyan font-mono text-[10px]">ACTIVE</span>
              </div>
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-mono">
                <span>{currentUser?.college || 'Engineering Candidate'}</span>
                <span>•</span>
                <span className="text-amber-500 font-semibold">{currentUser?.totalScore || 0} XP</span>
                <span>•</span>
                <span>{currentUser?.challengesSolved || 0} Solved</span>
              </div>
            </div>
          </div>

          <Link
            to="/profile"
            className="button-secondary text-xs px-3 py-1.5 flex items-center gap-1.5 self-start sm:self-auto"
          >
            <Edit3 className="w-3.5 h-3.5 text-slate-400" />
            <span>Edit Profile</span>
          </Link>
        </div>

        {/* Pillars: Strengths, Interests, Areas to Improve */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3 border-t border-slate-100 dark:border-[#21262D]">
          {/* Declared Strengths */}
          <div className="p-3 rounded bg-emerald-50/50 dark:bg-[#0D1117] border border-emerald-500/20 space-y-1">
            <div className="flex items-center gap-1.5 text-[11px] font-mono font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Verified Strengths</span>
            </div>
            <div className="flex flex-wrap gap-1 pt-1">
              {currentUser?.strengths && currentUser.strengths.length > 0 ? (
                currentUser.strengths.map((str) => (
                  <span key={str} className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-[10px] font-mono border border-emerald-500/20">
                    {str}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No declared strengths</span>
              )}
            </div>
          </div>

          {/* Declared Career Interests */}
          <div className="p-3 rounded bg-cyan-50/50 dark:bg-[#0D1117] border border-cyan-500/20 space-y-1">
            <div className="flex items-center gap-1.5 text-[11px] font-mono font-semibold text-cyan-600 dark:text-cyan-400 uppercase tracking-wide">
              <Compass className="w-3.5 h-3.5" />
              <span>Target Roles</span>
            </div>
            <div className="flex flex-wrap gap-1 pt-1">
              {currentUser?.interests && currentUser.interests.length > 0 ? (
                currentUser.interests.map((int) => (
                  <span key={int} className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-[10px] font-mono border border-cyan-500/20">
                    {int}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No declared target roles</span>
              )}
            </div>
          </div>

          {/* Declared Weaknesses */}
          <div className="p-3 rounded bg-amber-50/50 dark:bg-[#0D1117] border border-amber-500/20 space-y-1">
            <div className="flex items-center gap-1.5 text-[11px] font-mono font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wide">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Growth Focus</span>
            </div>
            <div className="flex flex-wrap gap-1 pt-1">
              {currentUser?.weaknesses && currentUser.weaknesses.length > 0 ? (
                currentUser.weaknesses.map((wk) => (
                  <span key={wk} className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-700 dark:text-amber-300 text-[10px] font-mono border border-amber-500/20">
                    {wk}
                  </span>
                ))
              ) : (
                <span className="text-[11px] text-slate-400 italic">No growth areas marked</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Insufficient Data Callout */}
      {isInsufficientData && (
        <div className="p-4 rounded-md border border-amber-500/30 bg-amber-500/5 space-y-2">
          <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-semibold text-xs">
            <Info className="w-4 h-4 shrink-0" />
            <span>Profile-Based Baseline Active</span>
          </div>
          <p className="text-xs text-slate-700 dark:text-slate-300 leading-normal max-w-3xl">
            {insights?.dataMessage || 'Your career recommendations are calculated using your declared strengths, interests, and profile preferences. Solve challenges to build verified performance metrics.'}
          </p>
          <div className="pt-1">
            <Link to="/challenges" className="button-primary text-xs font-semibold px-3 py-1.5 inline-flex items-center gap-1.5">
              <span>Start Debugging Challenges</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}

      {/* Top Role Match Hero Card */}
      {topMatch && (
        <div className="p-6 rounded-md border border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="flex flex-wrap items-center gap-2">
                <span className="badge badge-emerald font-mono text-[10px] uppercase font-bold">
                  TOP ROLE MATCH
                </span>
                {topMatch.isInterestMatch && (
                  <span className="badge badge-cyan font-mono text-[10px] uppercase font-bold">
                    TARGET CAREER GOAL
                  </span>
                )}
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400">{topMatch.matchLabel}</span>
              </div>
              <h2 className="font-heading font-bold text-xl text-slate-900 dark:text-[#E6EDF3]">
                {topMatch.title}
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                {topMatch.explanation}
              </p>
            </div>

            {/* Score Ring / Metrics */}
            <div className="flex items-center gap-3 shrink-0 self-start md:self-auto">
              <div className="text-center p-3 rounded bg-slate-50 dark:bg-[#0D1117] border border-slate-200 dark:border-[#30363D] min-w-[100px]">
                <span className="text-2xl font-bold font-mono text-cyan-600 dark:text-cyan-400 block">{topMatch.matchScore}%</span>
                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Skill Match</span>
              </div>
              <div className="text-center p-3 rounded bg-slate-50 dark:bg-[#0D1117] border border-slate-200 dark:border-[#30363D] min-w-[100px]">
                <span className="text-sm font-semibold font-mono text-emerald-600 dark:text-emerald-400 block">{topMatch.marketDemand}</span>
                <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Market Demand</span>
              </div>
            </div>
          </div>

          {/* Market Metadata */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-[#30363D] pt-3 font-mono">
            <div className="flex items-center gap-4">
              <span>Market Trend: <strong className="text-slate-700 dark:text-slate-300">{topMatch.marketTrend}</strong></span>
              <span>Source: <strong className="text-slate-700 dark:text-slate-300">{topMatch.source}</strong></span>
            </div>
            <span>Updated: <strong className="text-slate-700 dark:text-slate-300">{topMatch.lastUpdated}</strong></span>
          </div>
        </div>
      )}

      {/* Main Grid: Selected Role Deep Dive */}
      {currentRole && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="font-heading font-semibold text-base text-slate-900 dark:text-[#E6EDF3] flex items-center gap-2">
                <Target className="w-4 h-4 text-cyan-500" />
                <span>Role Specification: {currentRole.title}</span>
              </h3>
              <p className="text-xs text-slate-500">Skill alignment breakdown and gap exercises</p>
            </div>
            {currentRole.isInterestMatch && (
              <span className="badge badge-cyan font-mono text-[10px]">
                Aligned with stated target interest
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Relevant Strengths */}
            <div className="p-4 rounded-md border border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] space-y-3">
              <h4 className="font-heading font-semibold text-xs text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 uppercase font-mono tracking-wide border-b border-slate-200 dark:border-[#30363D] pb-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Demonstrated Capabilities</span>
              </h4>
              <div className="space-y-2">
                {currentRole.demonstratedStrengths && currentRole.demonstratedStrengths.length > 0 ? (
                  currentRole.demonstratedStrengths.map((str) => (
                    <div key={str} className="flex items-center justify-between p-2 rounded bg-slate-50 dark:bg-[#0D1117] border border-slate-200 dark:border-[#30363D]">
                      <span className="text-xs text-slate-700 dark:text-slate-300 font-mono">{str}</span>
                      <span className="badge badge-emerald text-[9px] font-mono">VERIFIED</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 italic">No specific strengths recorded yet.</p>
                )}
              </div>
            </div>

            {/* Skill Gaps & Practice CTA */}
            <div className="lg:col-span-2 p-4 rounded-md border border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] space-y-4">
              <h4 className="font-heading font-semibold text-xs text-slate-900 dark:text-[#E6EDF3] flex items-center gap-1.5 uppercase font-mono tracking-wide border-b border-slate-200 dark:border-[#30363D] pb-2">
                <Target className="w-3.5 h-3.5 text-cyan-500" />
                <span>Skill Gaps & Targeted Practice</span>
              </h4>

              <div className="space-y-3">
                {currentRole.skillGaps?.map((gap) => (
                  <div key={gap.skill} className="space-y-1 p-2.5 rounded bg-slate-50 dark:bg-[#0D1117] border border-slate-200 dark:border-[#30363D]">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-700 dark:text-slate-300 flex items-center gap-2">
                        <span>{gap.skill}</span>
                        {gap.isDeclaredWeakness && (
                          <span className="text-[10px] text-amber-500">
                            (Marked for improvement)
                          </span>
                        )}
                      </span>
                      <span className="text-slate-500">{gap.proficiency}% Proficiency</span>
                    </div>
                    <ProgressBar value={gap.proficiency} max={100} color={gap.proficiency >= 50 ? 'indigo' : 'rose'} />
                  </div>
                ))}
              </div>

              {/* Recommended Practice Challenges */}
              {currentRole.recommendedChallenges && currentRole.recommendedChallenges.length > 0 && (
                <div className="space-y-2 pt-1">
                  <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500 block">
                    Recommended Practice Challenges
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {currentRole.recommendedChallenges.map((chal) => (
                      <Link
                        key={chal.id}
                        to={`/challenge/${chal.id}`}
                        className="p-3 rounded bg-white dark:bg-[#0D1117] border border-slate-200 dark:border-[#30363D] hover:border-slate-400 dark:hover:border-slate-500 transition-colors flex items-center justify-between group"
                      >
                        <div className="space-y-0.5 min-w-0 pr-2">
                          <h5 className="font-heading font-semibold text-xs text-slate-900 dark:text-[#E6EDF3] group-hover:text-cyan-500 truncate">
                            {chal.title}
                          </h5>
                          <p className="text-[10px] font-mono text-slate-500 truncate">{chal.reason}</p>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-500 transition-colors shrink-0" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Role Rankings */}
      <div className="space-y-3">
        <div>
          <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500 block">Benchmarks</span>
          <h3 className="font-heading font-semibold text-base text-slate-900 dark:text-[#E6EDF3]">Role Compatibility Rankings</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {roles.map((role) => (
            <div
              key={role.id}
              onClick={() => setSelectedRole(role)}
              className={`p-4 rounded-md border transition-colors cursor-pointer space-y-3 bg-white dark:bg-[#161B22] ${
                selectedRole?.id === role.id
                  ? 'border-cyan-500 ring-1 ring-cyan-500/30'
                  : 'border-slate-200 dark:border-[#30363D] hover:border-slate-400 dark:hover:border-slate-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <h4 className="font-heading font-semibold text-sm text-slate-900 dark:text-[#E6EDF3]">{role.title}</h4>
                  {role.isInterestMatch && (
                    <span className="badge badge-cyan font-mono text-[9px]">
                      TARGET GOAL
                    </span>
                  )}
                </div>
                <span className={`badge shrink-0 font-mono text-[10px] ${
                  role.matchScore >= 75 ? 'badge-emerald' : role.matchScore >= 55 ? 'badge-indigo' : 'badge-amber'
                }`}>
                  {role.matchLabel}
                </span>
              </div>

              <div className="flex items-center justify-between text-xs pt-1 font-mono">
                <div>
                  <span className="text-[10px] text-slate-500 uppercase block">Skill Match</span>
                  <span className="text-base font-bold text-cyan-600 dark:text-cyan-400">{role.matchScore}%</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 uppercase block">Market Demand</span>
                  <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{role.marketDemand}</span>
                </div>
              </div>

              {role.profileWeaknesses && role.profileWeaknesses.length > 0 && (
                <div className="text-[10px] text-amber-500 font-mono">
                  Growth area: {role.profileWeaknesses.join(', ')}
                </div>
              )}

              <div className="text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-[#30363D] pt-2 flex items-center justify-between font-mono">
                <span>Top Gap: <strong className="text-slate-700 dark:text-slate-300">{role.skillGaps?.[0]?.skill || 'None'}</strong></span>
                <span className="text-cyan-500 font-semibold flex items-center gap-1 text-[11px]">
                  <span>Details</span>
                  <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Data Disclaimer */}
      <div className="p-3 rounded bg-slate-100 dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] text-center text-xs text-slate-500 space-y-0.5 font-mono">
        <p className="text-slate-600 dark:text-slate-400">{insights?.disclaimer || 'Market benchmarks reflect current software industry role requirements.'}</p>
        <p className="text-[10px]">Deterministic compatibility updates as debugging challenges are submitted.</p>
      </div>
    </div>
  );
}
