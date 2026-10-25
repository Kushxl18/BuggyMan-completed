import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bot, Bug, Lock, CheckCircle2, Loader2, Lightbulb, Compass, Code, ShoppingBag, ArrowRight } from 'lucide-react';
import { challengeService } from '../../services/challengeService';

export default function AIHintPanel({ challenge, userCode = '', testResults = [], addToast, user, setUser }) {
  const [loadingLevel, setLoadingLevel] = useState(null);
  const [unlockedHints, setUnlockedHints] = useState([]);
  const [balance, setBalance] = useState(user?.bugbytes_balance ?? user?.bugbytesBalance ?? 50);

  const HINT_TIERS = [
    {
      level: 1,
      name: 'Tier 1: Architectural Context',
      cost: 5,
      icon: <Lightbulb className="w-3.5 h-3.5 text-amber-400" />,
      desc: 'High-level theory and failure pattern analysis'
    },
    {
      level: 2,
      name: 'Tier 2: Targeted Diagnosis',
      cost: 10,
      icon: <Compass className="w-3.5 h-3.5 text-cyan-400" />,
      desc: 'Pinpoints specific component or condition defect'
    },
    {
      level: 3,
      name: 'Tier 3: Structural Solution',
      cost: 15,
      icon: <Code className="w-3.5 h-3.5 text-emerald-400" />,
      desc: 'Algorithmic pseudocode and implementation approach'
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
      if (addToast) addToast(`You need ${cost} BugBytes to unlock Hint ${level}. Complete challenges to earn credits.`, 'error');
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
          addToast(res.already_unlocked ? `Hint ${level} loaded.` : `Hint ${level} unlocked (${res.cost} BugBytes).`, 'success');
        }
      }
    } catch (err) {
      const errMsg = err?.message || 'AI assistance is temporarily unavailable. Credits were not deducted.';
      if (addToast) addToast(errMsg, 'error');
    } finally {
      setLoadingLevel(null);
    }
  };

  if (!challenge) return null;

  return (
    <div className="w-80 bg-[#161B22] border-l border-[#30363D] flex flex-col h-full overflow-y-auto select-none">
      {/* Header & Balance Display */}
      <div className="p-3 border-b border-[#30363D] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-cyan-400" />
          <div>
            <h3 className="text-xs font-semibold text-slate-200 uppercase font-mono tracking-wide">AI Assistant</h3>
            <p className="text-[10px] text-slate-400 font-mono">Grounded Code Analysis</p>
          </div>
        </div>

        {/* BugBytes Badge */}
        <Link 
          to="/store"
          className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#0D1117] border border-[#30363D] text-amber-400 hover:border-amber-500/50 transition-colors font-mono text-xs"
          title="BugBytes Balance"
        >
          <Bug className="w-3 h-3" />
          <span className="font-semibold">{balance}</span>
          <span className="text-[10px] text-slate-400">BB</span>
        </Link>
      </div>

      {/* Low BugBytes Store Callout */}
      {balance < 5 && (
        <div className="mx-3 mt-3 p-3 rounded bg-[#0D1117] border border-amber-500/30 text-[11px] space-y-2">
          <div className="flex items-center gap-1.5 font-semibold text-amber-300">
            <ShoppingBag className="w-3.5 h-3.5 shrink-0" />
            <span>Low BugBytes Balance</span>
          </div>
          <p className="text-[10px] text-slate-400 leading-normal">
            Earn BugBytes by resolving challenges or acquire demo credits from the store.
          </p>
          <Link 
            to="/store" 
            className="w-full py-1 px-2 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold text-[10px] flex items-center justify-center gap-1 transition-colors"
          >
            <span>Open Credits Store</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      )}

      {/* Progressive Hint Tiers */}
      <div className="p-3 space-y-2.5 flex-1">
        {HINT_TIERS.map(tier => {
          const unlockedObj = unlockedHints.find(h => (h.hint_level || h.hintLevel) === tier.level);
          const isUnlocked = Boolean(unlockedObj);
          const isLoading = loadingLevel === tier.level;

          return (
            <div key={tier.level} className="p-3 rounded bg-[#0D1117] border border-[#30363D] space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {tier.icon}
                  <span className="text-xs font-semibold text-slate-200">{tier.name}</span>
                </div>
                {isUnlocked ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                ) : (
                  <button
                    onClick={() => handleUnlockHint(tier.level, tier.cost)}
                    disabled={isLoading}
                    className={`flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded border transition-colors ${
                      balance >= tier.cost
                        ? 'bg-[#21262D] hover:bg-[#30363D] text-amber-400 border-[#30363D]'
                        : 'bg-[#161B22] text-slate-500 border-[#21262D] cursor-not-allowed'
                    }`}
                  >
                    {isLoading ? (
                      <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />
                    ) : (
                      <>
                        <Lock className="w-2.5 h-2.5" />
                        <span>{tier.cost} BB</span>
                      </>
                    )}
                  </button>
                )}
              </div>

              <p className="text-[11px] text-slate-400 leading-normal">{tier.desc}</p>

              {/* Unlocked Hint Text */}
              {isUnlocked && unlockedObj && (
                <div className="pt-2 border-t border-[#30363D] mt-2 space-y-1">
                  <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-emerald-400 block">Guidance</span>
                  <div className="text-xs text-slate-200 leading-relaxed font-mono bg-[#161B22] p-2.5 rounded border border-[#30363D] whitespace-pre-wrap">
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
