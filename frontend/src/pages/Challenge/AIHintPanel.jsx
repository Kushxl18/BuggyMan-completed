import React, { useState } from 'react';
import { Sparkles, Lock, Unlock, Loader2, HelpCircle } from 'lucide-react';
import { challengeService } from '../../services/challengeService';

export default function AIHintPanel({ challenge, userCode = '', testResults = [], addToast }) {
  const [unlockedLevel, setUnlockedLevel] = useState(0); // 0: locked, 1: level 1, 2: level 2, 3: level 3
  const [levelHints, setLevelHints] = useState({});
  const [loadingLevel, setLoadingLevel] = useState(null);

  const handleUnlockLevel = async (targetLevel) => {
    if (!challenge) return;
    if (targetLevel > unlockedLevel + 1) {
      if (addToast) addToast(`Unlock Level ${targetLevel - 1} first!`, 'warning');
      return;
    }

    try {
      setLoadingLevel(targetLevel);
      const prevHintTexts = Object.values(levelHints).map(h => h.hint);
      const res = await challengeService.getHint(challenge.id, {
        code: userCode,
        previousHints: prevHintTexts,
        testResults: testResults,
        level: targetLevel
      });

      if (res && res.hint) {
        setLevelHints(prev => ({ ...prev, [targetLevel]: res }));
        setUnlockedLevel(Math.max(unlockedLevel, targetLevel));
        if (addToast) addToast(`AI Hint Level ${targetLevel} unlocked!`, 'info');
      } else {
        if (addToast) addToast('Unable to generate level hint.', 'error');
      }
    } catch (err) {
      if (addToast) addToast('Failed to connect to AI hint service.', 'error');
    } finally {
      setLoadingLevel(null);
    }
  };

  if (!challenge) return null;

  const levelTitles = {
    1: 'Level 1: Conceptual Direction',
    2: 'Level 2: Specific Guidance',
    3: 'Level 3: Targeted Problem Area'
  };

  return (
    <div className="w-80 bg-slate-900 border-l border-slate-800 flex flex-col h-full overflow-y-auto">
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-violet animate-pulse-glow" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 font-heading">Progressive AI Hints</span>
        </div>
        <div className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] text-slate-400 font-bold">
          Hints Used: {unlockedLevel}/3
        </div>
      </div>

      <div className="p-4 space-y-4 flex-1">
        {[1, 2, 3].map((lvl) => {
          const isUnlocked = unlockedLevel >= lvl;
          const hintObj = levelHints[lvl];
          const isLoading = loadingLevel === lvl;

          return (
            <div key={lvl} className="glass-card p-4 rounded-xl relative overflow-hidden border border-slate-800">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-xs font-bold uppercase text-slate-300">{levelTitles[lvl]}</h4>
                {isUnlocked ? (
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                      {hintObj?.provider || 'AI'}
                    </span>
                    <Unlock className="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                ) : (
                  <button
                    onClick={() => handleUnlockLevel(lvl)}
                    disabled={isLoading || lvl > unlockedLevel + 1}
                    className="flex items-center gap-1.5 text-[11px] font-semibold text-brand-indigo hover:text-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <>
                        <Lock className="w-3.5 h-3.5" />
                        <span>Unlock</span>
                      </>
                    )}
                  </button>
                )}
              </div>

              {isUnlocked && hintObj ? (
                <p className="text-xs text-slate-200 leading-relaxed font-sans bg-slate-950/60 border border-slate-800/80 p-3 rounded-lg">
                  {hintObj.hint}
                </p>
              ) : (
                <div className="py-3 bg-slate-950/30 border border-dashed border-slate-800/80 rounded-lg flex items-center justify-center text-[11px] text-slate-500">
                  {lvl === 1 ? 'Unlock high-level concept' : lvl === 2 ? 'Requires Level 1 unlocked' : 'Requires Level 2 unlocked'}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
