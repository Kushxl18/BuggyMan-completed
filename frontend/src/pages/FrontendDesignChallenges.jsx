import React, { useState, useEffect } from 'react';
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
  Smartphone,
  CheckCircle2
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { challengeService } from '../services/challengeService';

const INITIAL_DESIGN_CHALLENGES = [
  {
    id: 'FE-E01',
    title: 'Flexbox alignment collapses on mobile',
    description: 'A navigation header collapses items on smaller viewports because align-items and flex-wrap properties conflict.',
    difficulty: 'Easy',
    technology: 'CSS / Flexbox',
    category: 'Layout & Responsiveness',
    timeEstimate: '10 mins',
    points: 100,
    previewTarget: 'Responsive Header Flexbox',
    tags: ['flexbox', 'mobile-responsive', 'header']
  },
  {
    id: 'FE-E02',
    title: 'CSS Grid overlapping grid areas',
    description: 'Card grid elements overlap on medium viewports due to explicit grid-template-areas misconfiguration.',
    difficulty: 'Easy',
    technology: 'CSS Grid',
    category: 'Grid Systems',
    timeEstimate: '12 mins',
    points: 100,
    previewTarget: 'Non-overlapping Product Grid',
    tags: ['css-grid', 'layout', 'responsive']
  },
  {
    id: 'FE-M01',
    title: 'Glassmorphism backdrop-filter blur broken',
    description: 'Backdrop filter blur effects do not render properly over dark surfaces due to missing vendor prefixes and stacking contexts.',
    difficulty: 'Medium',
    technology: 'CSS / Glassmorphism',
    category: 'Visual Effects',
    timeEstimate: '15 mins',
    points: 150,
    previewTarget: 'Frosted Glass Modal Overlay',
    tags: ['backdrop-filter', 'glassmorphism', 'z-index']
  },
  {
    id: 'FE-M02',
    title: 'Flickering CSS transition on hover',
    description: 'Hover micro-interaction causes layout shift and flickering on child text elements during scale animation.',
    difficulty: 'Medium',
    technology: 'CSS Animations',
    category: 'Micro-interactions',
    timeEstimate: '15 mins',
    points: 150,
    previewTarget: 'Smooth 60fps Micro-interaction Button',
    tags: ['transform', 'transitions', 'hardware-accel']
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
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [generating, setGenerating] = useState(false);
  const [genDifficulty, setGenDifficulty] = useState('Medium');

  useEffect(() => {
    async function loadBackendDesignChallenges() {
      try {
        setLoading(true);
        const data = await challengeService.getChallenges({ arena: 'frontend', personalized: true });
        if (Array.isArray(data) && data.length > 0) {
          const apiFormatted = data.map(c => ({
            ...c,
            id: String(c.id),
            previewTarget: c.previewTarget || 'Live UI Preview Component',
            tags: c.tags || ['ui', 'css', 'react']
          }));
          setChallenges(apiFormatted);
        }
      } catch (err) {
        console.error('Failed to sync backend Frontend challenges:', err);
      } finally {
        setLoading(false);
      }
    }
    loadBackendDesignChallenges();
  }, []);

  const handleGenerateDesignChallenge = async () => {
    try {
      setGenerating(true);
      const newChal = await challengeService.generateChallenge({
        difficulty: genDifficulty,
        technology: 'React',
        category: 'AI Generated UI'
      });
      const formattedChal = {
        ...newChal,
        id: String(newChal.id),
        previewTarget: 'Smooth 60fps Micro-interaction Animation',
        tags: ['ai-generated', 'animations', 'ui-fix']
      };
      setChallenges(prev => [formattedChal, ...prev]);
      addToast(`Generated dynamic ${genDifficulty} UI challenge!`, 'success');
    } catch (err) {
      addToast('Failed to generate UI challenge.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const filteredChallenges = challenges.filter(c => {
    const matchesSearch = (c.title || '').toLowerCase().includes(searchVal.toLowerCase()) ||
                          (c.description || '').toLowerCase().includes(searchVal.toLowerCase());
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
            <span className="badge badge-indigo text-[10px] uppercase font-bold">Personalized</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Palette className="w-7 h-7 text-cyan-500" />
            <span>Frontend Design & CSS Styling Arena</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>UI & Styling challenges adapted to your frontend proficiency</span>
          </p>
        </div>

        <SearchBar 
          value={searchVal} 
          onChange={setSearchVal} 
          onClear={() => setSearchVal('')} 
          placeholder="Search UI challenges..."
        />
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
      {loading ? (
        <div className="flex-1 flex items-center justify-center min-h-[300px]">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredChallenges.map((chal) => (
            <div key={chal.id} className="glass-panel rounded-xl p-6 flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-200 relative group">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className={`badge ${
                      chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                    }`}>
                      {chal.difficulty}
                    </span>
                    {chal.isSolved && (
                      <span className="badge badge-emerald flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        <span>PASSED</span>
                      </span>
                    )}
                  </div>
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

                {chal.reason && (
                  <p className="text-[11px] text-cyan-400/90 font-medium flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span>{chal.reason}</span>
                  </p>
                )}

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
                    {(chal.tags || []).map(t => (
                      <span key={t} className="badge badge-cyan text-[10px]">
                        #{t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-200 dark:border-[#292E33] pt-4 mt-5 flex items-center justify-between">
                <div className="text-[10px] text-slate-500 font-bold space-y-0.5">
                  <p className="uppercase">EST. TIME: <span className="text-slate-700 dark:text-slate-300">{chal.timeEstimate || '10 mins'}</span></p>
                  <p className="uppercase">XP REWARD: <span className="text-cyan-600 dark:text-cyan-400">{chal.points || 100} XP</span></p>
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
