import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, 
  Sparkles, 
  Table, 
  Terminal, 
  Layers,
  CheckCircle2,
  AlertCircle,
  Play
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function SQLChallenges({ addToast }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');

  useEffect(() => {
    async function loadBackendSQLChallenges() {
      try {
        setLoading(true);
        const data = await challengeService.getChallenges({ arena: 'sql', personalized: true });
        if (Array.isArray(data)) {
          setChallenges(data);
        }
      } catch (err) {
        console.error('Failed to sync backend SQL challenges:', err);
        if (addToast) addToast('Failed to load SQL challenges', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadBackendSQLChallenges();
  }, [addToast]);

  const handleResetFilters = () => {
    setSearchVal('');
    setSelectedDifficulty('All');
  };

  const filteredChallenges = challenges.filter(c => {
    const titleToMatch = (c.displayTitle || c.title || '').toLowerCase();
    const tablesStr = Array.isArray(c.tables) ? c.tables.join(' ').toLowerCase() : '';
    const matchesSearch = titleToMatch.includes(searchVal.toLowerCase()) ||
                          tablesStr.includes(searchVal.toLowerCase()) ||
                          (c.category || '').toLowerCase().includes(searchVal.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-cyan">DATABASE LAB</span>
            <span className="badge badge-indigo text-[10px] uppercase font-bold">Personalized</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Database className="w-7 h-7 text-cyan-500" />
            <span>SQL Debugging & Query Optimization</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>SQL challenges adapted to your query & schema proficiency</span>
          </p>
        </div>

        <SearchBar 
          value={searchVal}
          onChange={setSearchVal}
          onClear={() => setSearchVal('')}
          placeholder="Search SQL challenges..."
        />
      </div>

      {/* Difficulty Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 glass-panel p-4 rounded-xl border border-slate-200 dark:border-[#292E33]">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mr-2">
          <Layers className="w-3.5 h-3.5 text-cyan-500" />
          <span>Difficulty:</span>
        </span>
        {['All', 'Easy', 'Medium', 'Hard'].map((d) => (
          <button
            key={d}
            onClick={() => setSelectedDifficulty(d)}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              selectedDifficulty === d
                ? 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
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
              : [chal.category || 'SQL'].filter(Boolean);
            const tables = (chal.tables && chal.tables.length > 0) 
              ? chal.tables 
              : ['orders', 'customers'];

            return (
              <div key={chal.id} className="glass-panel rounded-2xl p-5 flex flex-col justify-between hover:border-cyan-500/50 dark:hover:border-slate-700/80 transition-all duration-300 relative group shadow-sm dark:shadow-md">
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
                    <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{chal.technology || 'SQL'}</span>
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-heading font-bold text-base text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors leading-snug">
                      {cardTitle}
                    </h3>

                    {/* Topic Tags */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
                      <span className="text-[11px] text-slate-400 dark:text-slate-500 font-medium mr-0.5">Topics:</span>
                      {cardTopics.map(t => (
                        <span key={t} className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700/60">
                          {t}
                        </span>
                      ))}
                    </div>

                    {/* Tables Involved */}
                    <div className="flex items-center gap-1.5 pt-1 text-[11px] text-slate-600 dark:text-slate-400 font-mono">
                      <Table className="w-3.5 h-3.5 text-cyan-500 shrink-0" />
                      <span className="truncate">Tables: {tables.join(', ')}</span>
                    </div>
                  </div>

                  {chal.reason && (
                    <p className="text-[11px] text-cyan-700 dark:text-cyan-400 font-medium pt-1 flex items-center gap-1.5 bg-cyan-500/5 dark:bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/10 dark:border-cyan-500/20">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 shrink-0" />
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
                    <Terminal className="w-3.5 h-3.5" />
                    <span>{chal.isSolved ? 'Review SQL Lab' : 'Launch SQL Lab'}</span>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No SQL Challenges Found"
          description="We couldn't find any SQL challenges matching your search query or filter tags."
          actionLabel="Clear All Filters"
          onAction={handleResetFilters}
        />
      )}
    </div>
  );
}
