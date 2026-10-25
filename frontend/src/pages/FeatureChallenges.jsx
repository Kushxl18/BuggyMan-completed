import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Layers, 
  Search, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Trophy, 
  Zap, 
  FileCode2, 
  Filter,
  Terminal,
  FolderGit2
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function FeatureChallenges({ addToast }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');
  
  // Filter States
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedTech, setSelectedTech] = useState('All');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await challengeService.getFeatureChallenges();
        setChallenges(data || []);
      } catch (err) {
        if (addToast) addToast('Failed to load feature challenges.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [addToast]);

  const categories = ['All', 'Backend', 'Frontend', 'Full-Stack'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];
  const technologies = ['All', 'Python / FastAPI', 'Node / Express', 'React / JavaScript'];

  const filteredChallenges = challenges.filter(c => {
    const matchesSearch = 
      (c.title || '').toLowerCase().includes(searchVal.toLowerCase()) ||
      (c.description || '').toLowerCase().includes(searchVal.toLowerCase()) ||
      (c.technology || '').toLowerCase().includes(searchVal.toLowerCase()) ||
      (c.category || '').toLowerCase().includes(searchVal.toLowerCase());

    const matchesCategory = selectedCategory === 'All' || (c.category || '').toLowerCase() === selectedCategory.toLowerCase();
    const matchesDifficulty = selectedDifficulty === 'All' || (c.difficulty || '').toLowerCase() === selectedDifficulty.toLowerCase();
    const matchesTech = selectedTech === 'All' || (c.technology || '').toLowerCase().includes(selectedTech.toLowerCase());

    return matchesSearch && matchesCategory && matchesDifficulty && matchesTech;
  });

  const getDifficultyColor = (diff) => {
    switch ((diff || '').toLowerCase()) {
      case 'easy':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'hard':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'medium':
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-7xl mx-auto">
      {/* 1. Header Overview Banner */}
      <div className="border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-5 md:p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_24px_rgba(0,0,0,0.1)]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 max-w-2xl">
            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900/60">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                Multi-File Architecture
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">BuggyMan Feature Arena</span>
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">
              Feature Implementation Arena
            </h1>
            <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              Receive realistic feature specifications and implement production-ready code inside existing multi-file repositories. Navigate project file trees, implement new capabilities, pass regression suites, and verify edge cases.
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono text-slate-600 dark:text-slate-400 self-start md:self-center shrink-0 border border-slate-200/80 dark:border-white/[0.08] rounded-lg p-3 bg-slate-50/70 dark:bg-white/[0.02] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
            <div>
              <span className="text-slate-400 block text-[10px]">CHALLENGES</span>
              <span className="text-base font-semibold text-slate-900 dark:text-slate-100 tabular-nums">{challenges.length}</span>
            </div>
            <div className="w-px h-7 bg-slate-200 dark:bg-white/[0.08]" />
            <div>
              <span className="text-slate-400 block text-[10px]">EVALUATION</span>
              <span className="text-base font-semibold text-blue-600 dark:text-blue-400">5-Tier Scoring</span>
            </div>
          </div>
        </div>

        {/* Search & Category Tabs */}
        <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  selectedCategory === cat
                    ? 'bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative w-full md:w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              placeholder="Search features or tech..."
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
        </div>

        {/* Secondary Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-100 dark:border-slate-800/60 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Difficulty:</span>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="py-1 px-2 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              {difficulties.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Technology:</span>
            <select
              value={selectedTech}
              onChange={(e) => setSelectedTech(e.target.value)}
              className="py-1 px-2 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 focus:outline-none"
            >
              {technologies.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          {(selectedCategory !== 'All' || selectedDifficulty !== 'All' || selectedTech !== 'All' || searchVal) && (
            <button
              onClick={() => {
                setSelectedCategory('All');
                setSelectedDifficulty('All');
                setSelectedTech('All');
                setSearchVal('');
              }}
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline ml-auto"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* 2. Challenge Grid */}
      {filteredChallenges.length === 0 ? (
        <EmptyState 
          title="No feature challenges found" 
          description="Try broadening your search or adjusting your category and difficulty filters."
          actionText="Clear Filters"
          onAction={() => {
            setSelectedCategory('All');
            setSelectedDifficulty('All');
            setSelectedTech('All');
            setSearchVal('');
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredChallenges.map((challenge) => {
            const isSolved = challenge.isSolved || challenge.is_solved;
            const fileCount = (challenge.files || []).length;
            const reqCount = (challenge.requirements || []).length;

            return (
              <div 
                key={challenge.id}
                className="glass-panel border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#10141F] rounded-xl p-4 flex flex-col justify-between hover:border-slate-300 dark:hover:border-white/[0.18] hover:-translate-y-0.5 hover:shadow-xl dark:hover:shadow-black/50 transition-all duration-200 h-full group shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]"
              >
                <div className="space-y-3">
                  {/* Top Tags */}
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                        {challenge.category}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 truncate">
                        {challenge.technology}
                      </span>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border shrink-0 ${getDifficultyColor(challenge.difficulty)}`}>
                      {challenge.difficulty}
                    </span>
                  </div>

                  {/* Title & Description */}
                  <div>
                    <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                      {challenge.title}
                      {isSolved && (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" title="Completed" />
                      )}
                    </h3>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed line-clamp-3">
                      {challenge.description}
                    </p>
                  </div>

                  {/* Metadata Indicators */}
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-500 dark:text-slate-400 pt-1">
                    <div className="flex items-center gap-1.5">
                      <FolderGit2 className="w-3.5 h-3.5 text-slate-400" />
                      <span>{fileCount} Repo Files</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>{challenge.timeEstimate || '30 mins'}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Trophy className="w-3.5 h-3.5 text-blue-500" />
                      <span>{challenge.points} XP</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-amber-500" />
                      <span>+{challenge.bugbytesReward || 35} BB</span>
                    </div>
                  </div>
                </div>

                {/* Primary Action Button */}
                <div className="pt-3 mt-4 border-t border-slate-100 dark:border-slate-800/80">
                  <Link
                    to={`/feature-challenges/${challenge.id}`}
                    className="button-primary w-full text-xs justify-between"
                  >
                    <span>Open Codebase Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
