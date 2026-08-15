import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export default function FilterPanel({ 
  selectedDifficulty, 
  setSelectedDifficulty, 
  selectedTech, 
  setSelectedTech, 
  selectedCategory, 
  setSelectedCategory,
  onReset 
}) {
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];
  const technologies = ['All', 'React', 'Django', 'NodeJS', 'CSS'];
  const categories = ['All', 'State Management', 'Lists & Keys', 'Data Validation', 'Styling'];

  const hasActiveFilters = selectedDifficulty !== 'All' || selectedTech !== 'All' || selectedCategory !== 'All';

  return (
    <div className="w-full glass-panel rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
      <div className="flex flex-wrap items-center gap-6">
        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200 font-semibold text-sm">
          <Filter className="w-4 h-4 text-cyan-500" />
          <span>Filters</span>
        </div>

        {/* Difficulty Selection */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-slate-500 font-semibold">DIFFICULTY</label>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-1.5 focus:border-cyan-500 outline-none cursor-pointer"
          >
            {difficulties.map(diff => (
              <option key={diff} value={diff}>{diff}</option>
            ))}
          </select>
        </div>

        {/* Technology Selection */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-slate-500 font-semibold">TECHNOLOGY</label>
          <select
            value={selectedTech}
            onChange={(e) => setSelectedTech(e.target.value)}
            className="bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-1.5 focus:border-cyan-500 outline-none cursor-pointer"
          >
            {technologies.map(tech => (
              <option key={tech} value={tech}>{tech}</option>
            ))}
          </select>
        </div>

        {/* Category Selection */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-slate-500 font-semibold">BUG CATEGORY</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-1.5 focus:border-cyan-500 outline-none cursor-pointer"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <button
          onClick={onReset}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors font-medium border border-slate-800 px-3 py-1.5 rounded-lg bg-slate-950/20"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      )}
    </div>
  );
}
