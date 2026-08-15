import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Palette, 
  Sparkles, 
  Search, 
  AlertCircle, 
  Play, 
  Loader2, 
  Layout, 
  Eye, 
  Wand2, 
  Layers, 
  Smartphone 
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';

const INITIAL_DESIGN_CHALLENGES = [
  {
    id: 'FE-E01',
    title: 'Flexbox alignment is off center',
    description: 'A navigation header element fails to align vertically in the center due to missing align-items properties on the flex container.',
    difficulty: 'Easy',
    technology: 'CSS / Flexbox',
    category: 'Layout',
    timeEstimate: '10 mins',
    points: 100,
    previewTarget: 'Centered Navbar Branding & Actions',
    tags: ['flexbox', 'alignment', 'css']
  },
  {
    id: 'FE-E02',
    title: 'Glassmorphism backdrop-filter missing',
    description: 'A floating card component lacks the backdrop-filter attribute, making background text unreadable when scrolling.',
    difficulty: 'Easy',
    technology: 'CSS / Styling',
    category: 'Visual Effects',
    timeEstimate: '10 mins',
    points: 100,
    previewTarget: 'Frosted Glass Modal Overlay',
    tags: ['glassmorphism', 'backdrop-filter']
  },
  {
    id: 'FE-M01',
    title: 'CSS Grid column overlap on mobile',
    description: 'A 3-column product grid breaks responsive layouts on mobile screens because grid-template-columns lacks minmax rules.',
    difficulty: 'Medium',
    technology: 'CSS Grid',
    category: 'Responsive Design',
    timeEstimate: '15 mins',
    points: 150,
    previewTarget: 'Fluid Auto-Fit Product Card Grid',
    tags: ['css-grid', 'responsive', 'media-queries']
  },
  {
    id: 'FE-M02',
    title: 'Hover transition causes layout shift',
    description: 'A card button changes border width on hover, causing neighboring DOM elements to jump 2px unexpectedly.',
    difficulty: 'Medium',
    technology: 'CSS Animations',
    category: 'Transitions',
    timeEstimate: '15 mins',
    points: 150,
    previewTarget: 'Jitter-Free Card Hover State',
    tags: ['transitions', 'box-shadow', 'transforms']
  },
  {
    id: 'FE-H01',
    title: 'Dark/Light mode contrast failure',
    description: 'Toggle button shifts theme state, but specific text components inherit low-contrast hex values failing WCAG standards.',
    difficulty: 'Hard',
    technology: 'Tailwind / CSS Vars',
    category: 'Accessibility & Theme',
    timeEstimate: '20 mins',
    points: 250,
    previewTarget: 'WCAG AAA Compliant Dark/Light Toggle',
    tags: ['wcag', 'css-variables', 'dark-mode']
  }
];

export default function FrontendDesignChallenges({ addToast }) {
  const [challenges, setChallenges] = useState(INITIAL_DESIGN_CHALLENGES);
  const [searchVal, setSearchVal] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [generating, setGenerating] = useState(false);
  const [genDifficulty, setGenDifficulty] = useState('Medium');

  const handleGenerateDesignChallenge = async () => {
    try {
      setGenerating(true);
      await new Promise(r => setTimeout(r, 1000));
      const newChal = {
        id: `fe-ai-${Date.now()}`,
        title: `AI UI: ${genDifficulty} CSS Animation #${Math.floor(Math.random() * 900 + 100)}`,
        description: `Dynamically generated ${genDifficulty} frontend challenge requiring keyframe timing adjustments and layout stabilization.`,
        difficulty: genDifficulty,
        technology: 'React & CSS',
        category: 'AI Generated UI',
        timeEstimate: genDifficulty === 'Easy' ? '10 mins' : genDifficulty === 'Medium' ? '15 mins' : '20 mins',
        points: genDifficulty === 'Easy' ? 100 : genDifficulty === 'Medium' ? 150 : 250,
        previewTarget: 'Smooth 60fps Micro-interaction Animation',
        tags: ['ai-generated', 'animations', 'ui-fix']
      };
      setChallenges(prev => [newChal, ...prev]);
      addToast(`Generated dynamic ${genDifficulty} UI challenge!`, 'success');
    } catch (err) {
      addToast('Failed to generate UI challenge.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const filteredChallenges = challenges.filter(c => {
    const matchesSearch = c.title.toLowerCase().includes(searchVal.toLowerCase()) ||
                          c.description.toLowerCase().includes(searchVal.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-cyan">FRONTEND STUDIO</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">UI / UX • CSS Grid • Micro-interactions</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Palette className="w-7 h-7 text-cyan-500" />
            <span>Frontend Design & CSS Styling Arena</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Fix responsive layout bugs, glassmorphism CSS, animations, and component styling.</p>
        </div>

        <SearchBar 
          value={searchVal} 
          onChange={setSearchVal} 
          onClear={() => setSearchVal('')} 
          placeholder="Search UI challenges..."
        />
      </div>

      {/* AI Design Challenge Generator Banner */}
      <div className="glass-panel p-6 rounded-xl border border-cyan-500/30 bg-white dark:bg-[#15181B] relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 dark:text-cyan-400">
              <Wand2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="badge badge-cyan">AI UI GENERATOR</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Create component visual design challenges</span>
              </div>
              <h2 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4]">Generate Frontend UI Challenge</h2>
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

            <button
              onClick={handleGenerateDesignChallenge}
              disabled={generating}
              className="button-primary px-5 py-2 text-xs font-bold whitespace-nowrap"
            >
              {generating ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating UI Task...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                  <span>Generate UI Challenge</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Difficulty Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 glass-panel p-4 rounded-xl border border-slate-200 dark:border-[#292E33]">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mr-2">
          <Layers className="w-3.5 h-3.5 text-cyan-500" />
          <span>Difficulty Filter:</span>
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
      {filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredChallenges.map((chal) => (
            <div key={chal.id} className="glass-panel rounded-xl p-6 flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-200 relative group">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className={`badge ${
                    chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                  }`}>
                    {chal.difficulty}
                  </span>
                  <span className="badge badge-cyan">
                    {chal.technology}
                  </span>
                </div>

                <div className="space-y-2">
                  <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                    {chal.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    {chal.description}
                  </p>
                </div>

                {/* Target Component Mock Preview */}
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-xs space-y-2">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-[11px] font-semibold">
                    <span className="flex items-center gap-1.5">
                      <Eye className="w-3.5 h-3.5 text-cyan-500" />
                      Visual Target:
                    </span>
                    <span className="text-slate-700 dark:text-slate-300 font-medium">{chal.previewTarget}</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {chal.tags.map(t => (
                      <span key={t} className="badge badge-cyan text-[10px]">
                        #{t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-200 dark:border-[#292E33] pt-4 mt-5 flex items-center justify-between">
                <div className="text-[10px] text-slate-500 font-bold space-y-0.5">
                  <p className="uppercase">EST. TIME: <span className="text-slate-700 dark:text-slate-300">{chal.timeEstimate}</span></p>
                  <p className="uppercase">XP REWARD: <span className="text-cyan-600 dark:text-cyan-400">{chal.points} XP</span></p>
                </div>

                <Link 
                  to={`/challenge/${chal.id}`}
                  className="button-primary px-4 py-2 text-xs"
                >
                  <Layout className="w-3.5 h-3.5" />
                  <span>Launch Studio</span>
                </Link>

              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-xl p-12 text-center max-w-lg mx-auto text-slate-600 dark:text-slate-400">
          <AlertCircle className="w-10 h-10 text-cyan-500 mx-auto mb-3" />
          <h3 className="font-heading font-bold text-slate-800 dark:text-[#F0F2F4]">No Design Challenges Found</h3>
          <p className="text-xs text-slate-500 mt-1">Try clearing your filters or generating a new UI challenge using AI.</p>
        </div>
      )}
    </div>
  );
}
