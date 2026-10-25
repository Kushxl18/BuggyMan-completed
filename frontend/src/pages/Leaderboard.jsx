import React, { useState, useEffect } from 'react';
import { Trophy, Flame, CheckCircle, Medal } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function Leaderboard({ user, addToast }) {
  const [board, setBoard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLeaderboard() {
      try {
        setLoading(true);
        const data = await challengeService.getLeaderboard();
        setBoard(data || []);
      } catch (err) {
        if (addToast) addToast('Failed to load leaderboard database.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadLeaderboard();
  }, [addToast]);

  const getRankMedal = (rank) => {
    if (rank === 1) return <Medal className="w-5 h-5 text-amber-500 fill-amber-500/20" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-slate-400 fill-slate-400/20" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-amber-700 fill-amber-700/20" />;
    return <span className="text-slate-500 font-mono font-bold w-5 text-center text-xs">{rank}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200/80 dark:border-white/[0.06] pb-4">
        <h1 className="font-heading font-extrabold text-2xl text-slate-900 dark:text-slate-100 flex items-center gap-2.5 tracking-tight">
          <Trophy className="w-6 h-6 text-amber-500 fill-amber-500/10 shrink-0" />
          <span>Leaderboard & Rankings</span>
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Real-time leaderboard calculated directly by backend evaluation engines.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : board.length > 0 ? (
        <div className="bg-white dark:bg-[#10141F] rounded-xl overflow-hidden border border-slate-200/80 dark:border-white/[0.08] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-50/80 dark:bg-white/[0.02] border-b border-slate-200/80 dark:border-white/[0.06] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="p-4 w-20 text-center">Rank</th>
                  <th className="p-4">Student</th>
                  <th className="p-4">College</th>
                  <th className="p-4 text-center">Solved</th>
                  <th className="p-4 text-center">Streak</th>
                  <th className="p-4 text-right pr-6">Total XP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04] text-slate-700 dark:text-slate-300">
                {board.map((row) => {
                  const isCurrentUser = user && (row.username === user.username || String(row.id) === String(user.id));
                  return (
                    <tr 
                      key={row.id || row.username}
                      className={`transition-colors ${
                        isCurrentUser 
                          ? 'bg-blue-500/10 dark:bg-blue-500/[0.08] border-l-2 border-l-blue-500 font-semibold' 
                          : 'hover:bg-slate-50/60 dark:hover:bg-white/[0.02]'
                      }`}
                    >
                      <td className="p-4 text-center flex items-center justify-center h-14">
                        {getRankMedal(row.rank)}
                      </td>
                      <td className="p-4 font-medium text-slate-900 dark:text-slate-100">
                        <div className="flex items-center gap-2.5">
                          <img
                            src={row.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
                            alt={row.name}
                            className="w-8 h-8 rounded-full object-cover ring-1 ring-slate-200 dark:ring-white/10"
                          />
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span>{row.name}</span>
                              {isCurrentUser && (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-blue-500/15 text-blue-600 dark:text-blue-400 border border-blue-500/30 uppercase tracking-wider">
                                  You
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono block">@{row.username}</span>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-slate-500 dark:text-slate-400">
                        {row.college || '-'}
                      </td>
                      <td className="p-4 text-center">
                        <span className="badge badge-emerald">
                          <CheckCircle className="w-3 h-3" />
                          <span className="font-mono">{row.solved}</span>
                        </span>
                      </td>
                      <td className="p-4 text-center">
                        <span className="badge badge-amber">
                          <Flame className="w-3 h-3 fill-amber-500" />
                          <span className="font-mono">{row.streak}d</span>
                        </span>
                      </td>
                      <td className="p-4 text-right pr-6 font-bold font-mono text-blue-600 dark:text-blue-400 tabular-nums">
                        {row.score} XP
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <EmptyState
          icon={Trophy}
          title="No Ranked Students Yet"
          description="Complete challenges and earn XP to rank on the global leaderboard."
        />
      )}
    </div>
  );
}
