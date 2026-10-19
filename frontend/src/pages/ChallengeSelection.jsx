import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Code2, Play, Search, AlertCircle, ArrowRight, Sparkles, Loader2, Bot, CheckCircle2 } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { challengeService } from '../services/challengeService';

export default function ChallengeSelection({ addToast }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [searchVal, setSearchVal] = useState('');
  
  // Generator state
  const [genDifficulty, setGenDifficulty] = useState('Easy');
  const [genTech, setGenTech] = useState('React');

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

  const handleGenerateChallenge = async () => {
    try {
      setGenerating(true);
      const newChal = await challengeService.generateChallenge({
        difficulty: genDifficulty,
        technology: genTech
      });
      setChallenges((prev) => [newChal, ...prev]);
      addToast(`Generated new ${genDifficulty} ${genTech} challenge!`, 'success');
    } catch (err) {
      addToast('Failed to generate AI challenge.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleResetFilters = () => {
    setSearchVal('');
    setSelectedDifficulty('All');
    setSelectedTech('All');
    setSelectedCategory('All');
    addToast('All filters cleared.', 'info');
  };

  const filteredChallenges = challenges.filter(c => {
    const matchesSearch = (c.title || '').toLowerCase().includes(searchVal.toLowerCase()) ||
                          (c.description || '').toLowerCase().includes(searchVal.toLowerCase());
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
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-heading font-extrabold text-2xl text-slate-900 dark:text-slate-100">Debugging Arena</h1>
            <span className="badge badge-indigo text-[10px] uppercase font-bold">Personalized</span>
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
            <span>Challenges adapted to your skill profile & performance history</span>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
          {filteredChallenges.map((chal) => (
            <div key={chal.id} className="glass-panel rounded-2xl p-6 flex flex-col justify-between hover:border-cyan-500/50 dark:hover:border-slate-700/80 transition-all duration-300 relative group shadow-sm dark:shadow-md">
              <div className="relative z-10 space-y-4">
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
                  <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">{chal.technology}</span>
                </div>

                <div className="space-y-1.5">
                  <h3 className="font-heading font-bold text-base text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                    {chal.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed line-clamp-3">
                    {chal.description}
                  </p>
                </div>

                {chal.reason && (
                  <p className="text-[11px] text-cyan-700 dark:text-cyan-400/90 font-medium pt-1 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-cyan-600 dark:text-cyan-400 shrink-0" />
                    <span>{chal.reason}</span>
                  </p>
                )}
              </div>

              <div className="relative z-10 border-t border-slate-200 dark:border-slate-800/80 pt-4 mt-5 flex items-center justify-between">
                <div className="text-[10px] text-slate-600 dark:text-slate-400 font-bold space-y-0.5">
                  <p className="uppercase">EST. TIME: <span className="text-slate-800 dark:text-slate-200 font-semibold">{chal.timeEstimate || '10 mins'}</span></p>
                  <p className="uppercase">XP REWARD: <span className="text-cyan-700 dark:text-cyan-400 font-bold">{chal.points || 100} XP</span></p>
                </div>

                <Link 
                  to={`/challenge/${chal.id}`}
                  className="button-primary px-4 py-2 text-xs"
                >
                  <span>{chal.isSolved ? 'Review' : 'Start Challenge'}</span>
                  <Play className="w-3 h-3 fill-white" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Challenges Found"
          description="We couldn't find any challenges matching your search query or filter tags. Try resetting filters or generate a new challenge using AI!"
          actionLabel="Clear All Filters"
          onAction={handleResetFilters}
        />
      )}
    </div>
  );
}
