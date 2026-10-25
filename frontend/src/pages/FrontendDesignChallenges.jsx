import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Palette, 
  Eye, 
  CheckCircle2,
  ArrowRight
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function FrontendDesignChallenges({ addToast }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');

  useEffect(() => {
    async function loadBackendDesignChallenges() {
      try {
        setLoading(true);
        const data = await challengeService.getChallenges({ arena: 'frontend', personalized: true });
        if (Array.isArray(data)) {
          setChallenges(data);
        }
      } catch (err) {
        console.error('Failed to sync backend Frontend challenges:', err);
        if (addToast) addToast('Failed to load Frontend Studio challenges', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadBackendDesignChallenges();
  }, [addToast]);

  const handleResetFilters = () => {
    setSearchVal('');
    setSelectedDifficulty('All');
  };

  const filteredChallenges = challenges.filter(c => {
    const titleToMatch = (c.displayTitle || c.title || '').toLowerCase();
    const matchesSearch = titleToMatch.includes(searchVal.toLowerCase()) ||
                          (c.technology || '').toLowerCase().includes(searchVal.toLowerCase()) ||
                          (c.category || '').toLowerCase().includes(searchVal.toLowerCase()) ||
                          (c.previewTarget || '').toLowerCase().includes(searchVal.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-white/[0.06]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="badge badge-purple font-mono text-[11px]">FRONTEND STUDIO</span>
            <span className="badge badge-gray font-mono text-[10px]">ADAPTIVE</span>
          </div>
          <h1 className="font-heading font-bold text-2xl text-slate-900 dark:text-[#E6EDF3] tracking-tight">
            Component & State Debugging
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            Isolate broken render cycles, state desynchronization, and CSS layout regressions with live DOM feedback.
          </p>
        </div>

        <SearchBar 
          value={searchVal}
          onChange={setSearchVal}
          onClear={() => setSearchVal('')}
          placeholder="Filter Frontend challenges..."
        />
      </div>

      {/* Difficulty Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-white dark:bg-[#161B22] p-2.5 rounded-md border border-slate-200 dark:border-[#30363D]">
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mr-2">
            Difficulty:
          </span>
          {['All', 'Easy', 'Medium', 'Hard'].map((d) => (
            <button
              key={d}
              onClick={() => setSelectedDifficulty(d)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                selectedDifficulty === d
                  ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/30 font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-[#E6EDF3] border border-transparent'
              }`}
            >
              {d}
            </button>
          ))}
        </div>
        <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
          Showing {filteredChallenges.length} of {challenges.length} challenges
        </div>
      </div>

      {/* Challenge Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredChallenges.map((chal) => {
            const cardTitle = chal.displayTitle || (chal.displayNumber ? `${chal.displayNumber}. ${chal.canonicalTitle || chal.title}` : chal.title);
            const cardTopics = (chal.topics && chal.topics.length > 0) 
              ? chal.topics.slice(0, 2) 
              : [chal.category || 'React'].filter(Boolean);
            const previewTarget = chal.previewTarget || 'Live UI Component';

            return (
              <div 
                key={chal.id} 
                className="glass-panel border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-4 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-1.5">
                      <span className={`badge ${
                        chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                      }`}>
                        {chal.difficulty}
                      </span>
                      {chal.isSolved && (
                        <span className="badge badge-emerald flex items-center gap-1 font-mono">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                          <span>RESOLVED</span>
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase">
                      {chal.technology || 'React'}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-heading font-semibold text-sm text-slate-900 dark:text-[#E6EDF3] group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                      {cardTitle}
                    </h3>

                    {/* Component Target */}
                    <div className="flex items-center gap-1.5 mt-2 text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                      <Eye className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">Target: {previewTarget}</span>
                    </div>

                    {/* Topic Tags */}
                    <div className="flex flex-wrap items-center gap-1 mt-2">
                      {cardTopics.map(t => (
                        <span 
                          key={t} 
                          className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-50 dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 border border-slate-200/70 dark:border-white/[0.06]"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  {chal.reason && (
                    <div className="text-[11px] text-purple-700 dark:text-purple-300 font-mono p-2 rounded bg-purple-500/5 dark:bg-purple-500/10 border border-purple-500/15">
                      {chal.reason}
                    </div>
                  )}
                </div>

                <div className="border-t border-slate-100 dark:border-white/[0.06] pt-3 mt-4 flex items-center justify-between">
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                    <span>{chal.timeEstimate || '10 min'}</span>
                    <span className="mx-1.5">|</span>
                    <span className="text-cyan-600 dark:text-cyan-400 font-semibold">{chal.points || 100} XP</span>
                  </div>

                  <Link 
                    to={`/challenge/${chal.id}`}
                    className="button-primary px-3 py-1.5 text-xs inline-flex items-center gap-1.5"
                  >
                    <span>{chal.isSolved ? 'Review Studio' : 'Open Studio'}</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No Design Challenges Found"
          description="We couldn't find any Frontend challenges matching your search query or filter tags."
          actionLabel="Clear All Filters"
          onAction={handleResetFilters}
        />
      )}
    </div>
  );
}
