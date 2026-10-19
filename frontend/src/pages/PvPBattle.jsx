import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Swords, 
  Zap, 
  Users, 
  Clock, 
  Copy, 
  Check, 
  Trophy, 
  X, 
  Loader2, 
  ArrowRight, 
  Shield, 
  Flame, 
  Sparkles, 
  RefreshCw, 
  AlertCircle, 
  Play, 
  Award,
  Crown,
  ChevronRight,
  Code2
} from 'lucide-react';
import { challengeService } from '../services/challengeService';

export default function PvPBattle({ user, addToast }) {
  const navigate = useNavigate();

  // Mode and Lobby States
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedTimeLimit, setSelectedTimeLimit] = useState(600); // 10 minutes in seconds
  const [customRoomCode, setCustomRoomCode] = useState('');
  const [isJoining, setIsJoining] = useState(false);
  const [isQuickMatching, setIsQuickMatching] = useState(false);
  const [isCreatingRoom, setIsCreatingRoom] = useState(false);

  // Waiting modal & active matchmaking state
  const [activeBattle, setActiveBattle] = useState(null);
  const [isWaitingModalOpen, setIsWaitingModalOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [matchFoundCountdown, setMatchFoundCountdown] = useState(null);
  const [matchedOpponent, setMatchedOpponent] = useState(null);

  // History and Stats
  const [history, setHistory] = useState([]);
  const [historyFilter, setHistoryFilter] = useState('All');
  const [historyLoading, setHistoryLoading] = useState(true);

  // Polling ref
  const pollIntervalRef = useRef(null);

  // Load PvP history on mount
  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await challengeService.getPvPHistory();
      if (Array.isArray(res)) {
        setHistory(res);
      } else if (res?.history && Array.isArray(res.history)) {
        setHistory(res.history);
      }
    } catch (err) {
      console.warn('Failed to load PvP history:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Clean up polling interval when component unmounts
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // Polling logic when in waiting state
  const startStatusPolling = useCallback((battleId) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const statusData = await challengeService.getBattleStatus(battleId);
        if (!statusData) return;

        setActiveBattle(prev => ({ ...prev, ...statusData }));

        // Check if matched
        if (statusData.status === 'MATCHED' || (statusData.player2 && statusData.player2.name)) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
          
          setMatchedOpponent(statusData.player2);
          setMatchFoundCountdown(3);

          if (addToast) {
            addToast(`Opponent matched: ${statusData.player2?.name || 'Challenger'}!`, 'success');
          }

          // 3-second countdown to arena navigation
          let count = 3;
          const countdownTimer = setInterval(() => {
            count -= 1;
            if (count > 0) {
              setMatchFoundCountdown(count);
            } else {
              clearInterval(countdownTimer);
              setIsWaitingModalOpen(false);
              navigate(`/pvp/arena/${statusData.battleId || battleId}`);
            }
          }, 1000);
        }
      } catch (err) {
        console.warn('Error polling battle status:', err);
      }
    }, 2000);
  }, [navigate, addToast]);

  // 1. Quick Match Action
  const handleQuickMatch = async () => {
    setIsQuickMatching(true);
    try {
      const battle = await challengeService.quickMatch({
        difficulty: selectedDifficulty,
        timeLimit: selectedTimeLimit
      });

      if (!battle || !battle.battleId) {
        throw new Error('Could not initiate match.');
      }

      setActiveBattle(battle);
      setIsWaitingModalOpen(true);
      setMatchedOpponent(null);
      setMatchFoundCountdown(null);

      if (battle.status === 'MATCHED' && battle.player2) {
        // Immediate match found!
        setMatchedOpponent(battle.player2);
        setMatchFoundCountdown(3);
        let count = 3;
        const countdownTimer = setInterval(() => {
          count -= 1;
          if (count > 0) {
            setMatchFoundCountdown(count);
          } else {
            clearInterval(countdownTimer);
            setIsWaitingModalOpen(false);
            navigate(`/pvp/arena/${battle.battleId}`);
          }
        }, 1000);
      } else {
        // Wait for opponent
        startStatusPolling(battle.battleId);
      }
    } catch (err) {
      if (addToast) addToast(err?.message || 'Quick Match failed to initialize.', 'error');
    } finally {
      setIsQuickMatching(false);
    }
  };

  // 2. Create Custom Room Action
  const handleCreateRoom = async () => {
    setIsCreatingRoom(true);
    try {
      const battle = await challengeService.createBattle({
        difficulty: selectedDifficulty,
        timeLimit: selectedTimeLimit
      });

      if (!battle || !battle.battleId) {
        throw new Error('Failed to create battle room.');
      }

      setActiveBattle(battle);
      setIsWaitingModalOpen(true);
      setMatchedOpponent(null);
      setMatchFoundCountdown(null);

      // Start polling for player 2 joining
      startStatusPolling(battle.battleId);
      if (addToast) addToast('Battle room created! Share your code with an opponent.', 'info');
    } catch (err) {
      if (addToast) addToast(err?.message || 'Failed to create room.', 'error');
    } finally {
      setIsCreatingRoom(false);
    }
  };

  // 3. Join Battle Room Action
  const handleJoinRoom = async (e) => {
    if (e) e.preventDefault();
    const code = customRoomCode.trim().toUpperCase();
    if (!code) {
      if (addToast) addToast('Please enter a room code.', 'warning');
      return;
    }

    setIsJoining(true);
    try {
      const battle = await challengeService.joinBattle(code);
      if (!battle || !battle.battleId) {
        throw new Error('Invalid room code or room is full.');
      }

      if (addToast) addToast('Connected to battle room! Entering arena...', 'success');
      navigate(`/pvp/arena/${battle.battleId}`);
    } catch (err) {
      if (addToast) addToast(err?.message || 'Unable to join room. Verify code.', 'error');
    } finally {
      setIsJoining(false);
    }
  };

  // Cancel waiting battle
  const handleCancelBattle = async () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    if (activeBattle?.battleId) {
      try {
        await challengeService.cancelBattle(activeBattle.battleId);
      } catch (e) {}
    }

    setIsWaitingModalOpen(false);
    setActiveBattle(null);
    setMatchedOpponent(null);
    setMatchFoundCountdown(null);
    if (addToast) addToast('Matchmaking cancelled.', 'info');
  };

  // Copy room code to clipboard
  const handleCopyRoomCode = () => {
    const code = activeBattle?.roomCode || '';
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
    if (addToast) addToast('Room code copied to clipboard!', 'success');
  };

  // Calculate statistics from history
  const totalBattles = history.length;
  const wins = history.filter(h => h.result === 'Won').length;
  const winRate = totalBattles > 0 ? Math.round((wins / totalBattles) * 100) : 0;
  const currentStreak = (() => {
    let streak = 0;
    for (const h of history) {
      if (h.result === 'Won') streak++;
      else break;
    }
    return streak;
  })();

  const filteredHistory = history.filter(item => {
    if (historyFilter === 'All') return true;
    return item.result === historyFilter;
  });

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-white via-slate-50 to-cyan-50/40 dark:from-slate-900 dark:via-slate-900/90 dark:to-slate-950 border border-slate-200 dark:border-slate-800/80 p-8 shadow-sm dark:shadow-xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-bold tracking-wide uppercase">
              <Swords className="w-3.5 h-3.5 animate-pulse" />
              Live Multiplayer Arena
            </div>
            <h1 className="text-3xl md:text-4xl font-heading font-extrabold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-3">
              <span>⚔️</span> PvP Debugging Battle
            </h1>
            <p className="text-slate-600 dark:text-slate-400 text-sm md:text-base leading-relaxed">
              Race in real-time against another developer to diagnose, isolate, and fix broken code first. All players receive the exact same bug!
            </p>
          </div>

          {/* Quick Stats Pill Header */}
          <div className="flex items-center gap-3 bg-white/90 dark:bg-slate-950/70 border border-slate-200 dark:border-slate-800/80 p-2 rounded-2xl shrink-0 backdrop-blur-sm shadow-sm">
            <div className="px-4 py-2 text-center border-r border-slate-200 dark:border-slate-800">
              <p className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Win Rate</p>
              <p className="text-xl font-heading font-extrabold text-cyan-600 dark:text-cyan-400">{winRate}%</p>
            </div>
            <div className="px-4 py-2 text-center border-r border-slate-200 dark:border-slate-800">
              <p className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Win Streak</p>
              <p className="text-xl font-heading font-extrabold text-amber-500 dark:text-amber-400 flex items-center justify-center gap-1">
                <Flame className="w-4 h-4 fill-amber-500 dark:fill-amber-400 text-amber-500 dark:text-amber-400" />
                {currentStreak}
              </p>
            </div>
            <div className="px-4 py-2 text-center">
              <p className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Rating</p>
              <p className="text-xl font-heading font-extrabold text-rose-500 dark:text-rose-400">1,480</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main 3 Action Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* CARD 1: Quick Match */}
        <div className="relative group rounded-2xl bg-white dark:bg-gradient-to-b dark:from-cyan-950/30 dark:to-slate-900/60 border border-cyan-500/30 hover:border-cyan-500/60 p-6 transition-all duration-300 shadow-sm dark:shadow-lg flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 dark:border-cyan-500/30 shadow-inner">
                <Zap className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                Instant Queue
              </span>
            </div>

            <div>
              <h2 className="text-lg font-heading font-bold text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors">
                Quick Match
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                Find an available opponent at your skill rating instantly with random challenge selection.
              </p>
            </div>

            {/* Quick Match Options */}
            <div className="space-y-2 pt-2">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 block">
                Target Difficulty
              </label>
              <div className="grid grid-cols-4 gap-1.5 bg-slate-100 dark:bg-slate-950/80 p-1 rounded-xl border border-slate-200 dark:border-slate-800">
                {['All', 'Easy', 'Medium', 'Hard'].map((diff) => (
                  <button
                    key={diff}
                    type="button"
                    onClick={() => setSelectedDifficulty(diff)}
                    className={`py-1.5 text-xs font-bold rounded-lg transition-all ${
                      selectedDifficulty === diff
                        ? 'bg-cyan-500 text-white shadow-sm'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-white dark:hover:bg-slate-900'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={handleQuickMatch}
              disabled={isQuickMatching}
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50"
            >
              {isQuickMatching ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching Opponents...</span>
                </>
              ) : (
                <>
                  <Swords className="w-4 h-4" />
                  <span>Find Opponent Now</span>
                  <ArrowRight className="w-4 h-4 ml-auto" />
                </>
              )}
            </button>
            <p className="text-[10px] text-center text-slate-500 dark:text-slate-400 mt-2 font-medium">
              Average queue time: ~5 seconds
            </p>
          </div>
        </div>

        {/* CARD 2: Create Custom Room */}
        <div className="relative group rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/60 hover:border-purple-400/50 dark:hover:border-slate-700/80 p-6 transition-all duration-300 shadow-sm dark:shadow-lg flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                <Users className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                Friendly Duel
              </span>
            </div>

            <div>
              <h2 className="text-lg font-heading font-bold text-slate-900 dark:text-slate-100 group-hover:text-purple-600 dark:group-hover:text-purple-300 transition-colors">
                Create Room
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                Configure match rules, generate an invite code, and invite a friend or teammate to battle.
              </p>
            </div>

            {/* Time Limit Selector */}
            <div className="space-y-2 pt-2">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 block">
                Time Limit
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: '5 Mins', val: 300 },
                  { label: '10 Mins', val: 600 },
                  { label: '15 Mins', val: 900 }
                ].map((t) => (
                  <button
                    key={t.val}
                    type="button"
                    onClick={() => setSelectedTimeLimit(t.val)}
                    className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                      selectedTimeLimit === t.val
                        ? 'bg-purple-500/15 dark:bg-purple-500/20 border-purple-500/50 text-purple-700 dark:text-purple-300 font-bold'
                        : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:border-purple-300 dark:hover:border-slate-700'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-6">
            <button
              onClick={handleCreateRoom}
              disabled={isCreatingRoom}
              className="w-full button-secondary py-3 px-4 rounded-xl text-slate-800 dark:text-slate-200 hover:text-slate-950 dark:hover:text-white border-purple-400/40 dark:border-purple-500/30 hover:border-purple-500 bg-purple-50 dark:bg-purple-950/20 hover:bg-purple-100 dark:hover:bg-purple-950/40 font-bold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isCreatingRoom ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-purple-600 dark:text-purple-400" />
                  <span>Generating Room...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                  <span>Create Battle Room</span>
                </>
              )}
            </button>
            <p className="text-[10px] text-center text-slate-500 dark:text-slate-400 mt-2 font-medium">
              Produces a 6-character room code
            </p>
          </div>
        </div>

        {/* CARD 3: Join Private Room */}
        <div className="relative group rounded-2xl bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800/60 hover:border-rose-400/50 dark:hover:border-slate-700/80 p-6 transition-all duration-300 shadow-sm dark:shadow-lg flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                <Swords className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20">
                Direct Code
              </span>
            </div>

            <div>
              <h2 className="text-lg font-heading font-bold text-slate-900 dark:text-slate-100 group-hover:text-rose-600 dark:group-hover:text-rose-300 transition-colors">
                Join Room
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                Have a battle code from a friend? Paste it below to jump directly into their lobby arena.
              </p>
            </div>

            {/* Room Code Input Form */}
            <form onSubmit={handleJoinRoom} className="space-y-2 pt-2">
              <label className="text-[11px] font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 block">
                Enter Room Code
              </label>
              <div className="relative">
                <input
                  type="text"
                  maxLength={12}
                  value={customRoomCode}
                  onChange={(e) => setCustomRoomCode(e.target.value.toUpperCase())}
                  placeholder="e.g. ROOM-8492"
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl px-4 py-2.5 text-sm font-mono font-bold tracking-widest text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-600 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500 uppercase transition-all"
                />
              </div>
            </form>
          </div>

          <div className="pt-6">
            <button
              onClick={handleJoinRoom}
              disabled={isJoining || !customRoomCode.trim()}
              className="w-full bg-rose-600 hover:bg-rose-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-rose-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isJoining ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Entering Room...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>Join Battle</span>
                </>
              )}
            </button>
            <p className="text-[10px] text-center text-slate-500 dark:text-slate-400 mt-2 font-medium">
              Case insensitive code
            </p>
          </div>
        </div>

      </div>

      {/* Rules & How PvP Works Banner */}
      <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800/60 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-500 dark:text-amber-400 shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-heading font-bold text-slate-900 dark:text-slate-200">How PvP Battles Work</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Both developers get the same challenge files. Run tests anytime. The first to pass 100% of the test suite or score highest before time expires wins!
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold text-slate-600 dark:text-slate-400 shrink-0">
          <span className="flex items-center gap-1.5"><Crown className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" /> +150 XP on Win</span>
          <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" /> Real-time Timer</span>
        </div>
      </div>

      {/* Battle History Section */}
      <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800/60 rounded-2xl p-6 space-y-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-heading font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500 dark:text-amber-400" />
              Recent Battle History
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
              Review your past head-to-head debugging matches and rating progress.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-2">
            <div className="flex bg-slate-100 dark:bg-slate-950 p-1 rounded-xl border border-slate-200 dark:border-slate-800">
              {['All', 'Won', 'Lost'].map((filter) => (
                <button
                  key={filter}
                  onClick={() => setHistoryFilter(filter)}
                  className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                    historyFilter === filter
                      ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <button
              onClick={fetchHistory}
              className="p-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-950 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
              title="Refresh history"
            >
              <RefreshCw className={`w-4 h-4 ${historyLoading ? 'animate-spin text-cyan-500' : ''}`} />
            </button>
          </div>
        </div>

        {/* History Table */}
        {historyLoading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-500 dark:text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
            <p className="text-xs">Loading battle archives...</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center mx-auto text-slate-400 dark:text-slate-500">
              <Swords className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">No battles recorded yet</p>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Jump into a Quick Match or challenge a teammate to record your first competitive debugging battle!
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] uppercase tracking-wider font-bold text-slate-500 dark:text-slate-400">
                  <th className="py-3 px-4">Result</th>
                  <th className="py-3 px-4">Opponent</th>
                  <th className="py-3 px-4">Challenge</th>
                  <th className="py-3 px-4 text-center">Score</th>
                  <th className="py-3 px-4 text-center">Solve Time</th>
                  <th className="py-3 px-4 text-right">XP Earned</th>
                  <th className="py-3 px-4 text-right">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60 text-xs">
                {filteredHistory.map((item) => {
                  const isWin = item.result === 'Won';
                  const isLoss = item.result === 'Lost';
                  return (
                    <tr 
                      key={item.id || item.battleId} 
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors group"
                    >
                      {/* Result Pill */}
                      <td className="py-3.5 px-4 font-bold">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${
                          isWin 
                            ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                            : isLoss
                            ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                            : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                        }`}>
                          {isWin ? <Trophy className="w-3 h-3" /> : isLoss ? <X className="w-3 h-3" /> : <Shield className="w-3 h-3" />}
                          {item.result}
                        </span>
                      </td>

                      {/* Opponent Info */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2.5">
                          {item.opponentAvatar ? (
                            <img 
                              src={item.opponentAvatar} 
                              alt={item.opponentName} 
                              className="w-7 h-7 rounded-full object-cover border border-slate-300 dark:border-slate-700 shrink-0" 
                            />
                          ) : (
                            <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center font-bold text-[10px] shrink-0">
                              {item.opponentName?.slice(0, 2).toUpperCase() || 'OP'}
                            </div>
                          )}
                          <div>
                            <p className="font-semibold text-slate-900 dark:text-slate-200 group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors">
                              {item.opponentName}
                            </p>
                            {item.opponentRating && (
                              <p className="text-[10px] text-slate-500 font-mono">
                                Rating: {item.opponentRating}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Challenge Title */}
                      <td className="py-3.5 px-4">
                        <div>
                          <p className="font-medium text-slate-900 dark:text-slate-200 truncate max-w-xs">
                            {item.challengeTitle}
                          </p>
                          <div className="flex items-center gap-2 mt-0.5">
                            {item.technology && (
                              <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase">
                                {item.technology}
                              </span>
                            )}
                            {item.difficulty && (
                              <span className={`text-[10px] font-bold ${
                                item.difficulty === 'Easy' ? 'text-emerald-600 dark:text-emerald-400' :
                                item.difficulty === 'Medium' ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'
                              }`}>
                                • {item.difficulty}
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Score comparison */}
                      <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-800 dark:text-slate-300">
                        <span>{item.testsPassed}</span>
                        {item.opponentTestsPassed && (
                          <span className="text-slate-500 font-normal"> vs {item.opponentTestsPassed}</span>
                        )}
                      </td>

                      {/* Solve Time */}
                      <td className="py-3.5 px-4 text-center font-mono text-slate-600 dark:text-slate-400">
                        {item.solveTime || '--'}
                      </td>

                      {/* XP Earned */}
                      <td className="py-3.5 px-4 text-right font-bold">
                        <span className={isWin ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-600 dark:text-slate-400'}>
                          +{item.xpEarned || 0} XP
                        </span>
                      </td>

                      {/* Date */}
                      <td className="py-3.5 px-4 text-right text-slate-500">
                        {item.date || 'Recent'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* WAITING ROOM & MATCHMAKING MODAL */}
      {isWaitingModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-8 max-w-md w-full shadow-2xl relative overflow-hidden">
            
            {/* Background glow orb */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-48 h-48 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none" />

            {/* Content when MATCHED vs WAITING */}
            {matchFoundCountdown !== null ? (
              // STATE A: Opponent Found & Countdown
              <div className="text-center space-y-6 animate-fade-in py-4">
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
                  <Swords className="w-8 h-8 animate-bounce" />
                </div>

                <div className="space-y-1">
                  <h3 className="text-2xl font-heading font-extrabold text-slate-900 dark:text-slate-100">
                    Opponent Found!
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Match ready. Entering the arena in...
                  </p>
                </div>

                {/* Big Countdown Number */}
                <div className="py-2">
                  <span className="text-6xl font-heading font-extrabold text-cyan-600 dark:text-cyan-400 animate-pulse tracking-tight">
                    {matchFoundCountdown}
                  </span>
                </div>

                {/* Opponent Card Preview */}
                {matchedOpponent && (
                  <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex items-center gap-3 text-left">
                    {matchedOpponent.avatar ? (
                      <img 
                        src={matchedOpponent.avatar} 
                        alt={matchedOpponent.name} 
                        className="w-10 h-10 rounded-full object-cover border border-rose-500/50" 
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-300 font-bold flex items-center justify-center border border-rose-500/30">
                        {matchedOpponent.name?.slice(0, 2).toUpperCase() || 'OP'}
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-slate-900 dark:text-slate-200 truncate">
                        {matchedOpponent.name}
                      </p>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                        Challenger • Rating {matchedOpponent.rating || 1420}
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30">
                      VS
                    </span>
                  </div>
                )}
              </div>
            ) : (
              // STATE B: Waiting for opponent
              <div className="text-center space-y-6 py-2">
                
                {/* Radar Pulse Animation */}
                <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full bg-cyan-500/20 animate-ping opacity-75" />
                  <div className="relative w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-950 border-2 border-cyan-500/50 flex items-center justify-center text-cyan-600 dark:text-cyan-400 shadow-glow-cyan">
                    <Swords className="w-7 h-7" />
                  </div>
                </div>

                <div className="space-y-1">
                  <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 flex items-center justify-center gap-2">
                    <span>Waiting for Opponent</span>
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                      <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                      <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-bounce"></span>
                    </span>
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Matchmaking in progress. Share the room code below with a friend.
                  </p>
                </div>

                {/* Room Code Display Box */}
                {activeBattle?.roomCode && (
                  <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 space-y-2">
                    <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                      Battle Room Code
                    </p>
                    <div className="flex items-center justify-between gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 shadow-sm">
                      <span className="font-mono text-xl font-extrabold text-cyan-600 dark:text-cyan-400 tracking-wider">
                        {activeBattle.roomCode}
                      </span>
                      <button
                        onClick={handleCopyRoomCode}
                        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
                        title="Copy code"
                      >
                        {copiedCode ? (
                          <Check className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Cancel Matchmaking Button */}
                <div className="pt-2">
                  <button
                    onClick={handleCancelBattle}
                    className="w-full button-secondary py-2.5 text-xs text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 border-rose-300 dark:border-rose-500/30 bg-rose-50 dark:bg-rose-950/20"
                  >
                    Cancel Matchmaking
                  </button>
                </div>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
