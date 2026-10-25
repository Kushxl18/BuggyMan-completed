import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bot, Bug, Lock, CheckCircle2, AlertCircle, Loader2, Lightbulb, Compass, Brain, ShoppingBag, ArrowRight } from 'lucide-react';
import { challengeService } from '../services/challengeService';

export default function AIHintPanel({ challengeId, currentCode, testResults, user, setUser, addToast }) {
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

  // Fetch unlocked hints for this challenge on mount
  useEffect(() => {
    async function loadHints() {
      if (!challengeId) return;
      try {
        const hints = await challengeService.getUnlockedHints(challengeId);
        if (Array.isArray(hints)) {
          setUnlockedHints(hints);
        }
      } catch (err) {
        // Silent fail for guest/offline
      }
    }
    loadHints();
  }, [challengeId]);

  // Keep local balance updated if user prop changes
  useEffect(() => {
    if (user) {
      setBalance(user.bugbytes_balance ?? user.bugbytesBalance ?? 50);
    }
  }, [user]);

  const handleUnlockHint = async (level, cost) => {
    const isUnlocked = unlockedHints.some(h => (h.hint_level || h.hintLevel) === level);
    if (!isUnlocked && balance < cost) {
      if (addToast) addToast(`You need ${cost} BugBytes to unlock Hint ${level}. Complete challenges to earn BugBytes!`, 'error');
      return;
    }

    try {
      setLoadingLevel(level);
      const res = await challengeService.requestAIHint(challengeId, level, {
        code: currentCode,
        testResults: testResults
      });

      if (res.hint) {
        // Update unlocked hints list
        setUnlockedHints(prev => {
          const filtered = prev.filter(h => (h.hint_level || h.hintLevel) !== level);
          return [...filtered, { hint_level: level, hintLevel: level, hint_content: res.hint, hintContent: res.hint }];
        });

        // Update user balance if charged
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

  return (
    <div className="glass-panel p-5 rounded-2xl border border-cyan-500/20 bg-slate-900/80 space-y-4">
      {/* Header & Balance Display */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-sm text-slate-100 flex items-center gap-1.5">
              <span>AI Debugging Assistant</span>
              <span className="badge badge-cyan text-[9px]">GROQ POWERED</span>
            </h3>
            <p className="text-[10px] text-slate-400">Progressive mentorship hints without revealing full solutions.</p>
          </div>
        </div>

        {/* BugBytes Badge */}
        <Link 
          to="/store"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 transition-all cursor-pointer"
          title="Visit BugBytes Store (Mock Purchase & Rewards)"
        >
          <Bug className="w-4 h-4 text-amber-400" />
          <span className="font-heading font-extrabold text-xs">{balance}</span>
          <span className="text-[10px] uppercase font-bold text-amber-500/80">BugBytes</span>
        </Link>
      </div>

      {/* Zero/Low BugBytes Store Callout */}
      {balance < 5 && (
        <div className="p-3.5 rounded-xl bg-slate-950 border border-amber-500/30 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="space-y-0.5">
            <div className="flex items-center gap-1.5 font-bold text-amber-300">
              <ShoppingBag className="w-3.5 h-3.5 shrink-0" />
              <span>Low or Zero BugBytes</span>
            </div>
            <p className="text-[11px] text-slate-400">
              Solving challenges is 100% free and earns BugBytes, or purchase demo credits at the Store!
            </p>
          </div>
          <Link 
            to="/store" 
            className="button-secondary text-[10px] py-1.5 px-3 whitespace-nowrap flex items-center gap-1 text-amber-300 border-amber-500/40"
          >
            <span>BugBytes Store</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      )}

      {/* 3 Tier Progressive Hint Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {HINT_TIERS.map(tier => {
          const isUnlocked = unlockedHints.some(h => (h.hint_level || h.hintLevel) === tier.level);
          const isLoading = loadingLevel === tier.level;

          return (
            <button
              key={tier.level}
              onClick={() => handleUnlockHint(tier.level, tier.cost)}
              disabled={isLoading}
              className={`p-3 rounded-xl border text-left transition-all relative overflow-hidden flex flex-col justify-between ${
                isUnlocked
                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                  : balance >= tier.cost
                  ? 'border-slate-700 bg-slate-800/80 hover:border-cyan-500/50 hover:bg-slate-800 text-slate-200'
                  : 'border-slate-800 bg-slate-900/50 text-slate-500 cursor-not-allowed opacity-75'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {tier.icon}
                    <span className="font-heading font-bold text-xs">{tier.name}</span>
                  </div>
                  {isUnlocked ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <div className="flex items-center gap-1 text-[10px] font-bold text-amber-400">
                      <Bug className="w-3 h-3" />
                      <span>{tier.cost}</span>
                    </div>
                  )}
                </div>
                <p className="text-[10px] text-slate-400 leading-tight">{tier.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-700/50 flex items-center justify-between text-[10px] font-semibold">
                {isLoading ? (
                  <span className="text-cyan-400 flex items-center gap-1">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Thinking...</span>
                  </span>
                ) : isUnlocked ? (
                  <span className="text-emerald-400 font-bold">Unlocked (Free Read)</span>
                ) : (
                  <span className={balance >= tier.cost ? 'text-cyan-400' : 'text-rose-400'}>
                    {balance >= tier.cost ? `Unlock for ${tier.cost} BB` : `Need ${tier.cost} BB`}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Unlocked Hints List Display */}
      {unlockedHints.length > 0 && (
        <div className="space-y-3 pt-2 border-t border-slate-800">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">Unlocked Mentor Hints:</span>
          {unlockedHints.map(hint => (
            <div key={hint.hint_level || hint.hintLevel} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs border-b border-slate-800/80 pb-2">
                <span className="font-heading font-bold text-cyan-400 flex items-center gap-1.5">
                  <Bot className="w-3.5 h-3.5" />
                  <span>Level {hint.hint_level || hint.hintLevel} Hint</span>
                </span>
                <span className="badge badge-emerald text-[9px]">UNLOCKED</span>
              </div>
              <div className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                {hint.hint_content || hint.hintContent}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
