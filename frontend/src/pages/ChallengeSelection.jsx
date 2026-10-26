import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, CheckCircle2 } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function ChallengeSelection({ addToast }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');

  // Filters
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedTech, setSelectedTech] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    async function loadChallenges() {
      try {
        setLoading(true);
        const data = await challengeService.getChallenges({ arena: 'code', personalized: true });
        setChallenges(data);
      } catch (err) {
        addToast('Failed to load challenges list.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadChallenges();
  }, [addToast]);

  const handleResetFilters = () => {
    setSearchVal('');
    setSelectedDifficulty('All');
    setSelectedTech('All');
    setSelectedCategory('All');
    addToast('Filters reset.', 'info');
  };

  const filteredChallenges = challenges.filter(c => {
    const titleToMatch = (c.displayTitle || c.title || '').toLowerCase();
    const matchesSearch = titleToMatch.includes(searchVal.toLowerCase()) ||
                          (c.technology || '').toLowerCase().includes(searchVal.toLowerCase()) ||
                          (c.category || '').toLowerCase().includes(searchVal.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty;
    const matchesTech = selectedTech === 'All' || c.technology === selectedTech;
    const matchesCategory = selectedCategory === 'All' || c.category === selectedCategory;

    return matchesSearch && matchesDifficulty && matchesTech && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200/80 dark:border-white/[0.06] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-semibold text-xl text-slate-900 dark:text-slate-100 tracking-tight">Debugging Arena</h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200/70 dark:border-blue-900/60 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
              Personalized
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-world code defect reproduction and repair sandboxes tailored to your skill profile.
          </p>
        </div>
        <SearchBar 
          value={searchVal} 
          onChange={setSearchVal} 
          onClear={() => setSearchVal('')} 
        />
      </div>

      <FilterPanel
        selectedDifficulty={selectedDifficulty}
        setSelectedDifficulty={setSelectedDifficulty}
        selectedTech={selectedTech}
        setSelectedTech={setSelectedTech}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        onReset={handleResetFilters}
      />

      {/* Grid of Challenges */}
      {filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredChallenges.map((chal) => {
            const cardTitle = chal.displayTitle || (chal.displayNumber ? `${chal.displayNumber}. ${chal.canonicalTitle || chal.title}` : chal.title);
            const cardTopics = (chal.topics && chal.topics.length > 0) 
              ? chal.topics.slice(0, 3) 
              : [chal.category || chal.technology].filter(Boolean);

            return (
              <div 
                key={chal.id} 
                className="glass-panel border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-4 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`badge ${
                        chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                      }`}>
                        {chal.difficulty}
                      </span>
                      {chal.personalizedBadge && !chal.isSolved && (
                        <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-500 dark:text-blue-400 border border-blue-500/20">
                          {chal.personalizedBadge}
                        </span>
                      )}
                      {chal.isSolved && (
                        <span className="badge badge-emerald flex items-center gap-1 font-mono">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                          <span>PASSED</span>
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500 uppercase">{chal.technology}</span>
                  </div>

                  <div className="space-y-1.5">
                    <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors leading-snug">
                      {cardTitle}
                    </h3>

                    {chal.reason && !chal.isSolved && (
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 italic line-clamp-1">
                        {chal.reason}
                      </p>
                    )}
                    
                    {/* Topic Tags */}
                    <div className="flex flex-wrap items-center gap-1 pt-1">
                      {cardTopics.map(t => (
                        <span key={t} className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-50 dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 border border-slate-200/70 dark:border-white/[0.06]">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-500 tabular-nums">
                    {chal.points || 100} XP
                  </span>
                  <Link
                    to={`/challenge/${chal.id}`}
                    className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 transition-colors group-hover:translate-x-0.5"
                  >
                    <span>Debug Issue</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No challenges found"
          description="Try clearing your search query or adjusting your filters."
          actionText="Clear Filters"
          onAction={handleResetFilters}
        />
      )}
    </div>
  );
}
