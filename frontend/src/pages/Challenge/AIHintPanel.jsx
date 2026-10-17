import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Bug, Lock, Unlock, CheckCircle2, Loader2, Lightbulb, Compass, Brain, ShoppingBag, ArrowRight } from 'lucide-react';
import { challengeService } from '../../services/challengeService';

export default function AIHintPanel({ challenge, userCode = '', testResults = [], addToast, user, setUser }) {
  const [loadingLevel, setLoadingLevel] = useState(null);
  const [unlockedHints, setUnlockedHints] = useState([]);
  const [balance, setBalance] = useState(user?.bugbytes_balance ?? user?.bugbytesBalance ?? 50);

  const HINT_TIERS = [
    {
      level: 1,
      name: 'Hint 1: Conceptual',
      cost: 5,
      icon: <Lightbulb className="w-4 h-4 text-amber-400" />,
      desc: 'High-level theory & engineering concept'
    },
    {
      level: 2,
      name: 'Hint 2: Directional',
      cost: 10,
      icon: <Compass className="w-4 h-4 text-cyan-400" />,
      desc: 'Points to failing component & logic flaw'
    },
    {
      level: 3,
      name: 'Hint 3: Detailed',
      cost: 15,
      icon: <Brain className="w-4 h-4 text-rose-400" />,
      desc: 'Targeted pseudocode & structural fix'
    }
  ];

  // Fetch unlocked hints and latest BugBytes balance
  useEffect(() => {
    async function loadHintsAndBalance() {
      if (!challenge?.id) return;
      try {
        const [hintsData, summaryData] = await Promise.allSettled([
          challengeService.getUnlockedHints(challenge.id),
          challengeService.getBugBytesSummary()
        ]);

        if (hintsData.status === 'fulfilled' && Array.isArray(hintsData.value)) {
          setUnlockedHints(hintsData.value);
        }

        if (summaryData.status === 'fulfilled' && summaryData.value) {
          const bal = summaryData.value.balance ?? summaryData.value.bugbytes_balance ?? 50;
          setBalance(bal);
          if (typeof setUser === 'function') {
            setUser(prev => prev ? { ...prev, bugbytes_balance: bal, bugbytesBalance: bal } : prev);
          }
        }
      } catch (err) {
        // Silent catch fallback
      }
    }
    loadHintsAndBalance();
  }, [challenge?.id]);

  const handleUnlockHint = async (level, cost) => {
    if (!challenge?.id) return;
    const isUnlocked = unlockedHints.some(h => (h.hint_level || h.hintLevel) === level);
    
    if (!isUnlocked && balance < cost) {
      if (addToast) addToast(`You need ${cost} BugBytes to unlock Hint ${level}. Complete challenges to earn BugBytes!`, 'error');
      return;
    }

    try {
      setLoadingLevel(level);
      const res = await challengeService.requestAIHint(challenge.id, level, {
        code: userCode,
        testResults: testResults
      });

      if (res && res.hint) {
        setUnlockedHints(prev => {
          const filtered = prev.filter(h => (h.hint_level || h.hintLevel) !== level);
          return [...filtered, { hint_level: level, hintLevel: level, hint_content: res.hint, hintContent: res.hint }];
        });

        if (typeof res.remaining_bugbytes === 'number') {
          setBalance(res.remaining_bugbytes);
          if (typeof setUser === 'function') {
            setUser(prev => prev ? { ...prev, bugbytes_balance: res.remaining_bugbytes, bugbytesBalance: res.remaining_bugbytes } : prev);
          }
        }

        if (addToast) {
          addToast(res.already_unlocked ? `Hint ${level} loaded!` : `Hint ${level} unlocked for ${res.cost} BugBytes!`, 'success');
        }
      }
    } catch (err) {
      const errMsg = err?.message || 'AI assistance is temporarily unavailable. Your BugBytes were not deducted.';
      if (addToast) addToast(errMsg, 'error');
    } finally {
      setLoadingLevel(null);
    }
  };

  if (!challenge) return null;

  return (
    <div className="w-80 bg-slate-900 border-l border-slate-800 flex flex-col h-full overflow-y-auto select-none">
      {/* Header & Balance Display */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-heading">AI Debugging Mentor</h3>
            <p className="text-[10px] text-slate-400">Groq Powered Mentorship</p>
          </div>
        </div>

        {/* BugBytes Badge */}
        <Link 
          to="/store"
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition-all cursor-pointer"
          title="Visit BugBytes Store (Mock Purchase & Rewards)"
        >
          <Bug className="w-3.5 h-3.5" />
          <span className="font-heading font-extrabold text-xs">{balance}</span>
          <span className="text-[9px] uppercase font-bold text-amber-500/80">🐞</span>
        </Link>
      </div>

      {/* Zero/Low BugBytes Store Callout */}
      {balance < 5 && (
        <div className="mx-4 mt-3 p-3 rounded-xl bg-slate-950 border border-amber-500/30 text-[11px] space-y-2">
          <div className="flex items-center gap-1.5 font-bold text-amber-300">
            <ShoppingBag className="w-3.5 h-3.5 shrink-0" />
            <span>Need BugBytes for hints?</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Solving challenges is always 100% free and earns BugBytes, or purchase demo credits at the Store!
          </p>
          <Link 
            to="/store" 
            className="w-full py-1 px-2.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold text-[10px] flex items-center justify-center gap-1 transition-all"
          >
            <span>Visit BugBytes Store</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      )}

      {/* 3 Tier Progressive Hint Buttons */}
      <div className="p-4 space-y-3 flex-1">
        {HINT_TIERS.map(tier => {
          const unlockedObj = unlockedHints.find(h => (h.hint_level || h.hintLevel) === tier.level);
          const isUnlocked = Boolean(unlockedObj);
          const isLoading = loadingLevel === tier.level;

          return (
            <div key={tier.level} className="glass-card p-3.5 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {tier.icon}
                  <span className="text-xs font-bold text-slate-200">{tier.name}</span>
                </div>
                {isUnlocked ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <button
                    onClick={() => handleUnlockHint(tier.level, tier.cost)}
                    disabled={isLoading}
                    className={`flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-lg border transition-all ${
                      balance >= tier.cost
                        ? 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border-amber-500/30'
                        : 'bg-slate-950 text-slate-500 border-slate-800 cursor-not-allowed'
                    }`}
                  >
                    {isLoading ? (
                      <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />
                    ) : (
                      <>
                        <Lock className="w-3 h-3" />
                        <span>{tier.cost} 🐞</span>
                      </>
                    )}
                  </button>
                )}
              </div>

              <p className="text-[10px] text-slate-400 leading-tight">{tier.desc}</p>

              {/* Unlocked Hint Text */}
              {isUnlocked && unlockedObj && (
                <div className="pt-2 border-t border-slate-800/80 mt-2 space-y-1">
                  <span className="text-[9px] font-bold uppercase tracking-wider text-emerald-400 block">✓ Unlocked Hint</span>
                  <div className="text-xs text-slate-200 leading-relaxed font-sans bg-slate-950 p-3 rounded-lg border border-slate-800 whitespace-pre-wrap">
                    {unlockedObj.hint_content || unlockedObj.hintContent}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
