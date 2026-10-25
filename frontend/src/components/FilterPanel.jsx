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
    <div className="w-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#161B22] rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-1.5 text-slate-700 dark:text-slate-300 font-medium">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span>Filters</span>
        </div>

        {/* Difficulty Selection */}
        <div className="flex items-center gap-2">
          <label className="text-[11px] font-mono text-slate-500 font-medium">DIFFICULTY</label>
          <select
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 text-xs rounded px-2.5 py-1 focus:border-blue-500 outline-none cursor-pointer"
          >
            {difficulties.map(diff => (
              <option key={diff} value={diff}>{diff}</option>
            ))}
          </select>
        </div>

        {/* Technology Selection */}
        <div className="flex items-center gap-2">
          <label className="text-[11px] font-mono text-slate-500 font-medium">TECH</label>
          <select
            value={selectedTech}
            onChange={(e) => setSelectedTech(e.target.value)}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 text-xs rounded px-2.5 py-1 focus:border-blue-500 outline-none cursor-pointer"
          >
            {technologies.map(tech => (
              <option key={tech} value={tech}>{tech}</option>
            ))}
          </select>
        </div>

        {/* Category Selection */}
        <div className="flex items-center gap-2">
          <label className="text-[11px] font-mono text-slate-500 font-medium">CATEGORY</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 text-xs rounded px-2.5 py-1 focus:border-blue-500 outline-none cursor-pointer"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters && onReset && (
        <button
          onClick={onReset}
          className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset</span>
        </button>
      )}
    </div>
  );
}
