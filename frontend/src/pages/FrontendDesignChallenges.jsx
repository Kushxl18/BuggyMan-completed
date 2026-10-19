import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Palette, 
  Sparkles, 
  Eye, 
  Layers, 
  CheckCircle2,
  AlertCircle,
  Layout
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
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-purple">FRONTEND STUDIO</span>
            <span className="badge badge-indigo text-[10px] uppercase font-bold">Personalized</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Palette className="w-7 h-7 text-indigo-500" />
            <span>Frontend & Component Debugging</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>UI & state challenges adapted to your frontend architecture proficiency</span>
          </p>
        </div>

        <SearchBar 
          value={searchVal}
          onChange={setSearchVal}
          onClear={() => setSearchVal('')}
          placeholder="Search Frontend challenges..."
        />
      </div>

      {/* Difficulty Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 glass-panel p-4 rounded-xl border border-slate-200 dark:border-[#292E33]">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mr-2">
          <Layers className="w-3.5 h-3.5 text-indigo-500" />
          <span>Difficulty:</span>
        </span>
        {['All', 'Easy', 'Medium', 'Hard'].map((d) => (
          <button
            key={d}
            onClick={() => setSelectedDifficulty(d)}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              selectedDifficulty === d
                ? 'bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30'
                : 'bg-white dark:bg-[#1B1F23] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-[#292E33]'
            }`}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Challenge Grid */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          {filteredChallenges.map((chal) => {
            const cardTitle = chal.displayTitle || (chal.displayNumber ? `${chal.displayNumber}. ${chal.canonicalTitle || chal.title}` : chal.title);
            const cardTopics = (chal.topics && chal.topics.length > 0) 
              ? chal.topics.slice(0, 2) 
              : [chal.category || 'React'].filter(Boolean);
            const previewTarget = chal.previewTarget || 'Live UI Component';

            return (
              <div key={chal.id} className="glass-panel rounded-2xl p-5 flex flex-col justify-between hover:border-indigo-500/50 dark:hover:border-slate-700/80 transition-all duration-300 relative group shadow-sm dark:shadow-md">
                <div className="relative z-10 space-y-3.5">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className={`badge ${
                        chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                      }`}>
                        {chal.difficulty}
                      </span>
                      {chal.isSolved && (
                        <span className="badge badge-emerald flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                          <span>PASSED</span>
                        </span>
                      )}
                    </div>
                    <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{chal.technology || 'React'}</span>
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-heading font-bold text-base text-slate-900 dark:text-slate-100 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors leading-snug">
                      {cardTitle}
                    </h3>

                    {/* Topic / Skills Tags */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                      <span className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mr-0.5">Skills:</span>
                      {cardTopics.map(t => (
                        <span key={t} className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700/60">
                          {t}
                        </span>
                      ))}
                    </div>

                    {/* Component Target */}
                    <div className="flex items-center gap-1.5 pt-1 text-[11px] text-slate-600 dark:text-slate-400 font-mono">
                      <Eye className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                      <span className="truncate">Target: {previewTarget}</span>
                    </div>
                  </div>

                  {chal.reason && (
                    <p className="text-[11px] text-indigo-700 dark:text-indigo-400 font-medium pt-1 flex items-center gap-1.5 bg-indigo-500/5 dark:bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/10 dark:border-indigo-500/20">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
                      <span>{chal.reason}</span>
                    </p>
                  )}
                </div>

                <div className="relative z-10 border-t border-slate-200 dark:border-slate-800/80 pt-4 mt-4 flex items-center justify-between">
                  <div className="text-[10px] text-slate-600 dark:text-slate-400 font-bold space-y-0.5">
                    <p className="uppercase">EST. TIME: <span className="text-slate-800 dark:text-slate-200 font-semibold">{chal.timeEstimate || '10 mins'}</span></p>
                    <p className="uppercase">REWARD: <span className="text-cyan-700 dark:text-cyan-400 font-bold">{chal.points || 100} XP</span></p>
                  </div>

                  <Link 
                    to={`/challenge/${chal.id}`}
                    className="button-primary px-4 py-2 text-xs"
                  >
                    <Layout className="w-3.5 h-3.5" />
                    <span>{chal.isSolved ? 'Review Studio' : 'Launch Studio'}</span>
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
