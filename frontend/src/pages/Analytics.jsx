import React, { useState, useEffect } from 'react';
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
  Cell, 
  Legend, 
  BarChart, 
  Bar 
} from 'recharts';
import { BarChart3, CheckCircle, Percent, AlertCircle, ArrowUpRight, Flame, Sparkles, Target, Zap } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { challengeService } from '../services/challengeService';
import { Link } from 'react-router-dom';

export default function Analytics({ addToast }) {
  const [data, setData] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        const [res, insights] = await Promise.all([
          challengeService.getAnalytics(),
          challengeService.getAIInsights().catch(() => null)
        ]);
        setData(res);
        if (insights) setAiInsights(insights);
      } catch (err) {
        if (addToast) addToast('Error loading analytics graphs.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, [addToast]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Color mappings for Pie/Bar charts
  const COLORS = ['#009CC2', '#1A9C55', '#C98200', '#D1242F', '#8b5cf6'];

  const solvedCount = data?.solvedCount ?? data?.totalSolved ?? data?.total_solved ?? 0;
  const accuracyRate = data?.accuracyRate ?? data?.accuracy ?? data?.accuracy_rate ?? 0;
  const avgTime = data?.avgTime ?? data?.avg_time ?? '0m 00s';
  const streakDays = data?.streakDays ?? data?.streak ?? data?.streak_days ?? 0;
  const weeklyProgress = data?.weeklyProgress ?? data?.timeTrend ?? [];
  const bugStats = data?.bugStats ?? [];

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-8 animate-fade-in px-4">
      {/* Page Title */}
      <div className="flex justify-between items-end border-b border-slate-200 dark:border-[#292E33] pb-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 font-heading block">Performance Dashboard</span>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] mt-1">Debugging Insights & Skill Growth</h1>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl space-y-1">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-medium">Challenges Solved</span>
            <CheckCircle className="w-4 h-4 text-emerald-500" />
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
            <ArrowUpRight className="w-4 h-4 text-cyan-500" />
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

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Weekly Solve Velocity (Line Chart) */}
        <div className="lg:col-span-2 glass-card p-6 rounded-xl space-y-4">
          <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Solve Velocity (Last 7 Days)</h3>
          <div className="h-64 w-full text-xs">
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

        {/* Bug Category Breakdown (Pie Chart) */}
        <div className="lg:col-span-1 glass-card p-6 rounded-xl space-y-4 flex flex-col justify-between">
          <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Bug Types Encountered</h3>
          <div className="h-52 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={bugStats}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
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

        {/* AI Personalized Growth & Recommendation Card */}
        {aiInsights && (
          <div className="lg:col-span-3 glass-panel p-6 rounded-xl border border-cyan-500/30 space-y-4 relative overflow-hidden bg-white dark:bg-[#15181B]">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-[#292E33] pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">AI Personalized Developer Growth Insights</h3>
              </div>
              <span className="badge badge-cyan">
                {aiInsights.provider || 'AI Engine'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
              <div className="bg-slate-50 dark:bg-[#1B1F23] p-4 rounded-lg border border-slate-200 dark:border-[#292E33] space-y-2">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold uppercase tracking-wider text-[10px]">
                  <CheckCircle className="w-3.5 h-3.5" />
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

            <div className="bg-slate-50 dark:bg-[#1B1F23] p-4 rounded-lg border border-slate-200 dark:border-[#292E33] space-y-1 font-sans text-xs">
              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-400 block">Recommended Focus Plan:</span>
              <p className="text-slate-800 dark:text-[#F0F2F4] leading-relaxed">{aiInsights.recommendedFocus}</p>
            </div>

            {aiInsights.learningStyleInsight && (
              <div className="bg-slate-50 dark:bg-[#1B1F23] p-4 rounded-lg border border-slate-200 dark:border-[#292E33] space-y-1 font-sans text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-500 block">Learning Velocity Insight:</span>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{aiInsights.learningStyleInsight}</p>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <Link to="/challenges" className="button-primary text-xs font-semibold px-4 py-2 flex items-center gap-2">
                <span>Practice Recommended Challenges</span>
                <ArrowUpRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
