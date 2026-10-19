import React, { useState, useEffect } from 'react';
import { Trophy, Flame, CheckCircle, Search, Medal, ShieldAlert } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import SearchBar from '../components/SearchBar';
import { challengeService } from '../services/challengeService';

export default function Leaderboard({ user, addToast }) {
  const [board, setBoard] = useState([]);
  const [searchVal, setSearchVal] = useState('');
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

  const filteredBoard = board.filter(item => 
    item.name.toLowerCase().includes(searchVal.toLowerCase()) ||
    (item.username && item.username.toLowerCase().includes(searchVal.toLowerCase())) ||
    (item.college && item.college.toLowerCase().includes(searchVal.toLowerCase()))
  );

  const getRankMedal = (rank) => {
    if (rank === 1) return <Medal className="w-5 h-5 text-amber-500 fill-amber-500/20" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-slate-400 fill-slate-400/20" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-amber-700 fill-amber-700/20" />;
    return <span className="text-slate-500 font-bold w-5 text-center">{rank}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
            <Trophy className="w-6 h-6 text-amber-500 fill-amber-500/10" />
            <span>Leaderboard & Rankings</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Real-time leaderboard calculated directly by backend evaluation engines.</p>
        </div>

        <SearchBar 
          value={searchVal} 
          onChange={setSearchVal} 
          onClear={() => setSearchVal('')} 
          placeholder="Search student or college..."
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredBoard.length > 0 ? (
        <div className="glass-panel rounded-xl overflow-hidden border border-slate-200 dark:border-[#292E33]">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 dark:bg-[#1B1F23] border-b border-slate-200 dark:border-[#292E33] text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider">
                  <th className="p-4 w-20 text-center">Rank</th>
                  <th className="p-4">Student</th>
                  <th className="p-4">College</th>
                  <th className="p-4 text-center">Solved</th>
                  <th className="p-4 text-center">Streak</th>
                  <th className="p-4 text-right pr-6">Total XP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-[#292E33] text-slate-700 dark:text-slate-300">
                {filteredBoard.map((row) => {
                  const isCurrentUser = user && (row.username === user.username || String(row.id) === String(user.id));
                  return (
                    <tr 
                      key={row.id || row.username}
                      className={`transition-colors ${
                        isCurrentUser 
                          ? 'bg-cyan-500/10 dark:bg-cyan-500/15 border-l-4 border-l-cyan-500 hover:bg-cyan-500/20 font-semibold' 
                          : 'hover:bg-slate-50 dark:hover:bg-[#1B1F23]'
                      }`}
                    >
                      <td className="p-4 text-center flex items-center justify-center h-12">
                        {getRankMedal(row.rank)}
                      </td>
                      <td className="p-4 font-heading font-semibold text-slate-800 dark:text-[#F0F2F4]">
                        <div className="flex items-center gap-2.5">
                          <img
                            src={row.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
                            alt={row.name}
                            className="w-7 h-7 rounded-full object-cover ring-1 ring-cyan-500/30"
                          />
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span>{row.name}</span>
                              {isCurrentUser && (
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-cyan-500 text-white uppercase tracking-wider">
                                  You
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-500 block">@{row.username}</span>
                          </div>
                        </div>
                      </td>
                    <td className="p-4 text-slate-600 dark:text-slate-400">
                      {row.college || '-'}
                    </td>
                    <td className="p-4 text-center">
                      <span className="badge badge-emerald">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>{row.solved}</span>
                      </span>
                    </td>
                    <td className="p-4 text-center">
                      <span className="badge badge-amber">
                        <Flame className="w-3.5 h-3.5 fill-amber-500" />
                        <span>{row.streak}d</span>
                      </span>
                    </td>
                    <td className="p-4 text-right pr-6 font-extrabold text-cyan-600 dark:text-cyan-400 font-heading">
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
          title="No Ranked Students Found"
          description="No leaderboard entries matched your search query. Try clearing your search term."
          actionLabel="Clear Search"
          onAction={() => setSearchVal('')}
        />
      )}
    </div>
  );
}
