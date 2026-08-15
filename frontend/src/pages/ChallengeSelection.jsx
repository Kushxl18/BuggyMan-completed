import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Code2, Play, Search, AlertCircle, ArrowRight, Sparkles, Loader2, Bot } from 'lucide-react';
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
        const data = await challengeService.getChallenges();
        setChallenges(data);
      } catch (err) {
        addToast('Failed to load challenges list.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadChallenges();
  }, []);

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
    const matchesSearch = c.title.toLowerCase().includes(searchVal.toLowerCase()) ||
                          c.description.toLowerCase().includes(searchVal.toLowerCase());
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
          <h1 className="font-heading font-extrabold text-2xl text-slate-100">Debugging Arena</h1>
          <p className="text-xs text-slate-400 mt-1">Select a challenge or generate brand new bugs dynamically using AI.</p>
        </div>
        <SearchBar 
          value={searchVal} 
          onChange={setSearchVal} 
          onClear={() => setSearchVal('')} 
        />
      </div>

      {/* AI Challenge Generator Banner */}
      <div className="glass-panel p-6 rounded-xl border border-cyan-500/30 bg-white dark:bg-[#15181B] relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 dark:text-cyan-400">
              <Bot className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="badge badge-cyan">AI GENERATOR</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Generate fresh real-world bugs instantly</span>
              </div>
              <h2 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4]">Create Dynamic AI Challenge</h2>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            {/* Difficulty Selector */}
            <div className="flex bg-slate-100 dark:bg-[#1B1F23] p-1 rounded-lg border border-slate-200 dark:border-[#292E33] text-xs font-semibold">
              {['Easy', 'Medium', 'Hard'].map((diff) => (
                <button
                  key={diff}
                  onClick={() => setGenDifficulty(diff)}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    genDifficulty === diff 
                      ? diff === 'Easy' ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                        : diff === 'Medium' ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                        : 'bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {diff}
                </button>
              ))}
            </div>

            {/* Technology Selector */}
            <select
              value={genTech}
              onChange={(e) => setGenTech(e.target.value)}
              className="bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-lg px-3 py-2 text-xs font-semibold text-slate-800 dark:text-[#F0F2F4] outline-none focus:border-cyan-500 cursor-pointer"
            >
              <option value="React">React</option>
              <option value="Django">Django</option>
            </select>

            {/* Generate Button */}
            <button
              onClick={handleGenerateChallenge}
              disabled={generating}
              className="button-primary px-5 py-2 text-xs font-bold whitespace-nowrap"
            >
              {generating ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-cyan-200" />
                  <span>Generate Challenge</span>
                </>
              )}
            </button>
          </div>
        </div>
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
            <div key={chal.id} className="glass-panel rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700/80 transition-all duration-300 relative group">
              <div className="relative z-10 space-y-4">
                <div className="flex justify-between items-center">
                  <span className={`badge ${
                    chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                  }`}>
                    {chal.difficulty}
                  </span>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">{chal.technology}</span>
                </div>

                <div className="space-y-1.5">
                  <h3 className="font-heading font-bold text-base text-slate-200 group-hover:text-slate-100 transition-colors">
                    {chal.title}
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                    {chal.description}
                  </p>
                </div>
              </div>

              <div className="relative z-10 border-t border-slate-800/80 pt-4 mt-5 flex items-center justify-between">
                <div className="text-[10px] text-slate-500 font-bold space-y-0.5">
                  <p className="uppercase">EST. TIME: <span className="text-slate-300">{chal.timeEstimate}</span></p>
                  <p className="uppercase">XP REWARD: <span className="text-cyan-400">{chal.points} XP</span></p>
                </div>

                <Link 
                  to={`/challenge/${chal.id}`}
                  className="button-primary px-4 py-2 text-xs"
                >
                  <span>Start Challenge</span>
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
