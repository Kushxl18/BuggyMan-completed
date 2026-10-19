import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  User, 
  Mail, 
  GraduationCap, 
  BookOpen, 
  Award, 
  Flame, 
  CheckCircle2, 
  Edit3, 
  Key, 
  X, 
  Loader2,
  BarChart3,
  Percent,
  ArrowUpRight,
  ArrowRight,
  Sparkles,
  Target,
  Clock,
  Briefcase,
  Layers
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';
import ProgressBar from '../components/ProgressBar';
import { authService } from '../services/authService';
import { challengeService } from '../services/challengeService';

export default function UserProfile({ addToast, setUser }) {
  const [profile, setProfile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'analytics'
  
  // Modals state
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isPassOpen, setIsPassOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  // Edit fields
  const [editName, setEditName] = useState('');
  const [editCollege, setEditCollege] = useState('');
  const [editBio, setEditBio] = useState('');
  const [editAvatar, setEditAvatar] = useState('');
  const [editStrengths, setEditStrengths] = useState([]);
  const [editWeaknesses, setEditWeaknesses] = useState([]);

  // Password fields
  const [oldPass, setOldPass] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirmNewPass, setConfirmNewPass] = useState('');

  const SKILL_CATEGORIES = ['Backend', 'SQL', 'Frontend', 'APIs', 'Security', 'Testing', 'DevOps'];
  const COLORS = ['#009CC2', '#1A9C55', '#C98200', '#D1242F', '#8b5cf6'];

  useEffect(() => {
    async function loadProfileAndAnalytics() {
      try {
        setLoading(true);
        const [res, analyticsData, insightsData] = await Promise.all([
          authService.getCurrentUser(),
          challengeService.getAnalytics().catch(() => null),
          challengeService.getAIInsights().catch(() => null)
        ]);
        setProfile(res);
        setEditName(res.name);
        setEditCollege(res.college);
        setEditBio(res.bio);
        setEditAvatar(res.avatar);
        setEditStrengths(res.strengths || []);
        setEditWeaknesses(res.weaknesses || []);

        if (analyticsData) setAnalytics(analyticsData);
        if (insightsData) setAiInsights(insightsData);
      } catch (err) {
        if (addToast) addToast('Failed to load user profile & analytics.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadProfileAndAnalytics();
  }, [addToast]);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setModalLoading(true);
    try {
      const updated = await authService.updateProfile({
        display_name: editName,
        college: editCollege,
        bio: editBio,
        avatar: editAvatar,
        strengths: editStrengths,
        weaknesses: editWeaknesses
      });
      setProfile(updated);
      if (typeof setUser === 'function') {
        setUser(updated);
      }
      setIsEditOpen(false);
      if (addToast) addToast('Profile updated successfully!', 'success');
    } catch (err) {
      if (addToast) addToast(err.message || 'Failed to update profile.', 'error');
    } finally {
      setModalLoading(false);
    }
  };

  const handlePassSubmit = async (e) => {
    e.preventDefault();
    if (!oldPass) {
      if (addToast) addToast('Current password is required.', 'warning');
      return;
    }
    if (newPass.length < 6) {
      if (addToast) addToast('New password must be at least 6 characters.', 'warning');
      return;
    }
    if (newPass !== confirmNewPass) {
      if (addToast) addToast('Passwords do not match.', 'error');
      return;
    }

    setModalLoading(true);
    try {
      const updated = await authService.updateProfile({ password: newPass });
      setProfile(updated);
      setIsPassOpen(false);
      setOldPass('');
      setNewPass('');
      setConfirmNewPass('');
      if (addToast) addToast('Password updated successfully!', 'success');
    } catch (err) {
      if (addToast) addToast(err.message || 'Failed to update password.', 'error');
    } finally {
      setModalLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const solvedCount = profile?.challengesSolved ?? analytics?.solvedCount ?? analytics?.totalSolved ?? 0;
  const accuracyRate = analytics?.accuracyRate ?? analytics?.accuracy ?? 0;
  const avgTime = analytics?.avgTime ?? '0m 00s';
  const streakDays = profile?.streak ?? analytics?.streakDays ?? 0;
  const weeklyProgress = analytics?.weeklyProgress ?? analytics?.timeTrend ?? [];
  const bugStats = analytics?.bugStats ?? [];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#292E33] pb-4">
        <div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4]">My Profile & Skill Analytics</h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Review your personal profile, skill profiler matrices, strengths, and debugging performance metrics.</p>
        </div>

        {/* View Toggle Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'overview'
                ? 'bg-cyan-500 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            Profile & Skills
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'analytics'
                ? 'bg-cyan-500 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            Performance Analytics
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: User Card */}
        <div className="lg:col-span-1 glass-card p-6 rounded-xl flex flex-col items-center text-center relative overflow-hidden self-start">
          <div className="relative group mb-4">
            <img
              src={profile.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}
              alt={profile.name}
              className="w-24 h-24 rounded-2xl object-cover ring-4 ring-cyan-500/30 group-hover:ring-cyan-500 transition-all duration-200"
            />
          </div>

          <h2 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4]">{profile.name}</h2>
          <p className="text-xs text-slate-500">@{profile.username}</p>

          <p className="text-xs text-slate-600 dark:text-slate-400 mt-4 leading-relaxed italic max-w-xs">
            "{profile.bio || 'No biography written yet.'}"
          </p>

          <div className="w-full space-y-3.5 border-t border-slate-200 dark:border-[#292E33] pt-5 mt-5 text-left text-xs">
            <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-400">
              <Mail className="w-4 h-4 text-cyan-500 shrink-0" />
              <span className="truncate">{profile.email}</span>
            </div>
            <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-400">
              <GraduationCap className="w-4 h-4 text-cyan-500 shrink-0" />
              <span>{profile.college}</span>
            </div>
          </div>

          <div className="w-full grid grid-cols-2 gap-3 mt-6 pt-2">
            <button
              onClick={() => setIsEditOpen(true)}
              className="button-secondary text-xs py-2 px-3 flex items-center justify-center gap-1.5"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Profile</span>
            </button>
            <button
              onClick={() => setIsPassOpen(true)}
              className="button-secondary text-xs py-2 px-3 flex items-center justify-center gap-1.5"
            >
              <Key className="w-3.5 h-3.5" />
              <span>Password</span>
            </button>
          </div>
        </div>

        {/* Right Column: Dynamic Tabs Content */}
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'overview' && (
            <>
              {/* Summary Stats Row */}
              <div className="grid grid-cols-3 gap-4">
                <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total XP</span>
                  <div className="inline-flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-heading font-extrabold text-xl">
                    <Award className="w-5 h-5" />
                    <span>{profile.totalScore}</span>
                  </div>
                </div>
                <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Solved</span>
                  <div className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-heading font-extrabold text-xl">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>{solvedCount}</span>
                  </div>
                </div>
                <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">BugBytes Balance</span>
                  <div className="inline-flex items-center gap-1.5 text-amber-500 font-heading font-extrabold text-xl">
                    <span className="text-lg">🐞</span>
                    <span>{profile.bugbytes_balance ?? profile.bugbytesBalance ?? 50}</span>
                  </div>
                </div>
                <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Current Streak</span>
                  <div className="inline-flex items-center gap-1 text-amber-500 font-heading font-extrabold text-xl">
                    <Flame className="w-5 h-5 fill-amber-500 text-amber-500" />
                    <span>{streakDays} Days</span>
                  </div>
                </div>
              </div>

              {/* Compact Career Direction Summary Card */}
              <div className="glass-panel p-5 rounded-xl border border-cyan-500/30 bg-slate-900/60 text-slate-100 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-heading font-bold text-xs text-slate-100">Career Direction & Role Suitability</h4>
                    <p className="text-[11px] text-slate-400">Discover software roles aligned with your demonstrated skill profiler matrix.</p>
                  </div>
                </div>
                <Link to="/career-insights" className="button-primary text-xs px-3.5 py-1.5 flex items-center gap-1.5 whitespace-nowrap shrink-0">
                  <span>Explore Career Insights</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Strengths & Weaknesses Preferences */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="glass-card p-6 rounded-xl space-y-3">
                  <h3 className="font-heading font-bold text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Registered Strengths</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.strengths && profile.strengths.length > 0 ? (
                      profile.strengths.map((str) => (
                        <span key={str} className="badge badge-emerald text-xs font-semibold px-3 py-1">
                          {str}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500 italic">None selected yet.</span>
                    )}
                  </div>
                </div>

                <div className="glass-card p-6 rounded-xl space-y-3">
                  <h3 className="font-heading font-bold text-sm text-rose-600 dark:text-rose-400 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    <span>Areas You Want to Improve</span>
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.weaknesses && profile.weaknesses.length > 0 ? (
                      profile.weaknesses.map((wk) => (
                        <span key={wk} className="badge badge-rose text-xs font-semibold px-3 py-1">
                          {wk}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500 italic">None selected yet.</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Dynamic Skill Profiler Matrix */}
              <div className="glass-card p-6 rounded-xl space-y-5">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-[#292E33] pb-3">
                  <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Dynamic Skill Profiler Matrix</h3>
                  <span className="text-[10px] text-cyan-500 font-bold uppercase tracking-wider">0-100% Calculated Mastery</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
                  {profile.skills && Object.entries(profile.skills).map(([skill, val]) => (
                    <div key={skill} className="space-y-2">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-600 dark:text-slate-400">{skill}</span>
                        <span className="text-slate-800 dark:text-[#F0F2F4]">{val}%</span>
                      </div>
                      <ProgressBar value={val} max={100} color={val >= 75 ? 'emerald' : val >= 50 ? 'indigo' : 'rose'} />
                    </div>
                  ))}
                </div>
              </div>

              {/* Badges Box */}
              <div className="glass-card p-6 rounded-xl space-y-4">
                <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Earned Milestones & Badges</h3>
                {profile.badges && profile.badges.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {profile.badges.map((badge) => (
                      <div key={badge.name} className="glass-panel p-4 rounded-lg border border-slate-200 dark:border-[#292E33] text-center space-y-2 group transition-all duration-200">
                        <div className="text-3xl text-gradient group-hover:scale-110 transition-transform">
                          {badge.icon}
                        </div>
                        <div>
                          <h4 className="font-heading font-bold text-xs text-slate-800 dark:text-[#F0F2F4]">{badge.name}</h4>
                          <p className="text-[10px] text-slate-500 mt-0.5 leading-relaxed">{badge.desc}</p>
                          <span className="text-[9px] text-cyan-600 dark:text-cyan-400 font-bold block mt-2">{badge.date}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-center rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] space-y-2">
                    <span className="text-2xl">🏆</span>
                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">No badges earned yet</p>
                    <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
                      Solve debugging challenges and build daily streaks to unlock your first badges and achievements.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === 'analytics' && (
            <>
              {/* Analytics Metric Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="glass-card p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                    <span className="text-xs font-medium">Challenges Solved</span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  </div>
                  <p className="text-2xl font-extrabold font-heading text-slate-800 dark:text-[#F0F2F4]">{solvedCount}</p>
                </div>

                <div className="glass-card p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                    <span className="text-xs font-medium">Accuracy Rate</span>
                    <Percent className="w-4 h-4 text-cyan-500" />
                  </div>
                  <p className="text-2xl font-extrabold font-heading text-slate-800 dark:text-[#F0F2F4]">{accuracyRate}%</p>
                </div>

                <div className="glass-card p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                    <span className="text-xs font-medium">Avg Solve Time</span>
                    <Clock className="w-4 h-4 text-cyan-500" />
                  </div>
                  <p className="text-2xl font-extrabold font-heading text-slate-800 dark:text-[#F0F2F4]">{avgTime}</p>
                </div>

                <div className="glass-card p-5 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                    <span className="text-xs font-medium">Active Streak</span>
                    <Flame className="w-4 h-4 text-amber-500" />
                  </div>
                  <p className="text-2xl font-extrabold font-heading text-slate-800 dark:text-[#F0F2F4]">{streakDays} Days</p>
                </div>
              </div>

              {/* Solve Velocity Chart */}
              <div className="glass-card p-6 rounded-xl space-y-4">
                <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Solve Velocity (Last 7 Days)</h3>
                <div className="h-60 w-full text-xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={weeklyProgress}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#D8DEE4" />
                      <XAxis dataKey="day" stroke="#59636E" />
                      <YAxis stroke="#59636E" />
                      <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#D8DEE4', borderRadius: '8px', color: '#1F2328' }} />
                      <Line type="monotone" dataKey="solved" stroke="#009CC2" strokeWidth={3} dot={{ fill: '#009CC2', r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Bug Categories Pie Chart */}
              {bugStats && bugStats.length > 0 && bugStats.some(b => b.count > 0) ? (
                <div className="glass-card p-6 rounded-xl space-y-4 flex flex-col justify-between">
                  <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Bug Types Encountered</h3>
                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={bugStats}
                          cx="50%"
                          cy="50%"
                          innerRadius={45}
                          outerRadius={75}
                          paddingAngle={4}
                          dataKey="count"
                        >
                          {bugStats.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#D8DEE4', borderRadius: '8px', color: '#1F2328' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex flex-wrap justify-center gap-x-4 gap-y-2 text-[10px] font-semibold text-slate-600 dark:text-slate-400">
                    {bugStats.map((entry, index) => (
                      <div key={entry.name} className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                        <span>{entry.name} ({entry.count})</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="glass-card p-6 rounded-xl space-y-2 text-center min-h-[160px] flex flex-col items-center justify-center">
                  <span className="text-2xl">📊</span>
                  <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">No bug types recorded yet</p>
                  <p className="text-[11px] text-slate-500 max-w-xs">Solve challenges to see your category breakdown here.</p>
                </div>
              )}

              {/* AI Growth Insights */}
              {aiInsights && (
                <div className="glass-panel p-6 rounded-xl border border-cyan-500/30 space-y-4 relative overflow-hidden bg-white dark:bg-[#15181B]">
                  <div className="flex items-center justify-between border-b border-slate-200 dark:border-[#292E33] pb-3">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-amber-500" />
                      <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">AI Personalized Growth Insights</h3>
                    </div>
                    <span className="badge badge-cyan">
                      {aiInsights.provider || 'AI Engine'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
                    <div className="bg-slate-50 dark:bg-[#1B1F23] p-4 rounded-lg border border-slate-200 dark:border-[#292E33] space-y-2">
                      <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider text-[10px]">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Debugging Strengths</span>
                      </div>
                      <ul className="space-y-1 text-slate-700 dark:text-slate-300 list-disc list-inside">
                        {(aiInsights.debuggingStrengths || []).map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-slate-50 dark:bg-[#1B1F23] p-4 rounded-lg border border-slate-200 dark:border-[#292E33] space-y-2">
                      <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold uppercase tracking-wider text-[10px]">
                        <Target className="w-3.5 h-3.5" />
                        <span>Growth & Practice Focus</span>
                      </div>
                      <ul className="space-y-1 text-slate-700 dark:text-slate-300 list-disc list-inside">
                        {(aiInsights.areasNeedingImprovement || []).map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* MODAL: Edit Profile */}
      {isEditOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 backdrop-blur-sm" onClick={() => setIsEditOpen(false)} />
          <div className="relative w-full max-w-md glass-panel rounded-xl p-6 border border-slate-200 dark:border-[#292E33] shadow-2xl z-10 animate-slide-up">
            <div className="flex justify-between items-center mb-5">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Edit Profile</h3>
              <button onClick={() => setIsEditOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Full Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">College / Institution</label>
                <input
                  type="text"
                  value={editCollege}
                  onChange={(e) => setEditCollege(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Avatar Image URL</label>
                <input
                  type="url"
                  value={editAvatar}
                  onChange={(e) => setEditAvatar(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Biography</label>
                <textarea
                  value={editBio}
                  onChange={(e) => setEditBio(e.target.value)}
                  rows="3"
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none resize-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-emerald-500 uppercase">Strengths</label>
                <div className="flex flex-wrap gap-1.5">
                  {SKILL_CATEGORIES.map((cat) => {
                    const isSel = editStrengths.includes(cat);
                    return (
                      <button
                        type="button"
                        key={`edit-str-${cat}`}
                        onClick={() => {
                          setEditStrengths((prev) => isSel ? prev.filter(s => s !== cat) : [...prev, cat]);
                        }}
                        className={`text-[10px] font-semibold px-2.5 py-1 rounded-md border transition-all ${
                          isSel ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'bg-slate-900 border-slate-800 text-slate-400'
                        }`}
                      >
                        {cat}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-rose-500 uppercase">Areas to Improve</label>
                <div className="flex flex-wrap gap-1.5">
                  {SKILL_CATEGORIES.map((cat) => {
                    const isSel = editWeaknesses.includes(cat);
                    return (
                      <button
                        type="button"
                        key={`edit-wk-${cat}`}
                        onClick={() => {
                          setEditWeaknesses((prev) => isSel ? prev.filter(w => w !== cat) : [...prev, cat]);
                        }}
                        className={`text-[10px] font-semibold px-2.5 py-1 rounded-md border transition-all ${
                          isSel ? 'bg-rose-500/20 border-rose-500 text-rose-300' : 'bg-slate-900 border-slate-800 text-slate-400'
                        }`}
                      >
                        {cat}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex justify-end gap-3.5 pt-2">
                <button type="button" onClick={() => setIsEditOpen(false)} className="button-secondary text-xs py-2 px-4">
                  Cancel
                </button>
                <button type="submit" disabled={modalLoading} className="button-primary text-xs py-2 px-4">
                  {modalLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Save Changes</span>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Change Password */}
      {isPassOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 backdrop-blur-sm" onClick={() => setIsPassOpen(false)} />
          <div className="relative w-full max-w-md glass-panel rounded-xl p-6 border border-slate-200 dark:border-[#292E33] shadow-2xl z-10 animate-slide-up">
            <div className="flex justify-between items-center mb-5">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Change Password</h3>
              <button onClick={() => setIsPassOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handlePassSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Current Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={oldPass}
                  onChange={(e) => setOldPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">New Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={newPass}
                  onChange={(e) => setNewPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Confirm New Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={confirmNewPass}
                  onChange={(e) => setConfirmNewPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="flex justify-end gap-3.5 pt-2">
                <button type="button" onClick={() => setIsPassOpen(false)} className="button-secondary text-xs py-2 px-4">
                  Cancel
                </button>
                <button type="submit" disabled={modalLoading} className="button-primary text-xs py-2 px-4">
                  {modalLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Update Password</span>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
