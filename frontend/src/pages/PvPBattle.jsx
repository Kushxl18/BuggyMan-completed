import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Swords, 
  Zap, 
  Users, 
  UserX,
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
  Code2,
  Share2,
  Radio
} from 'lucide-react';
import { challengeService } from '../services/challengeService';

export default function PvPBattle({ user, addToast }) {
  const navigate = useNavigate();

  // Mode and Lobby States
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedTimeLimit, setSelectedTimeLimit] = useState(600); // 10 minutes default
  const [customRoomCode, setCustomRoomCode] = useState('');
  const [isQuickMatching, setIsQuickMatching] = useState(false);
  const [isCreatingRoom, setIsCreatingRoom] = useState(false);
  const [isJoining, setIsJoining] = useState(false);

  // Waiting modal & active matchmaking state
  const [isWaitingModalOpen, setIsWaitingModalOpen] = useState(false);
  const [waitingType, setWaitingType] = useState('quick_match'); // 'quick_match' | 'custom_room'
  const [searchSeconds, setSearchSeconds] = useState(0);
  const [isSearchTimedOut, setIsSearchTimedOut] = useState(false);
  const [activeBattle, setActiveBattle] = useState(null);
  const [matchFoundCountdown, setMatchFoundCountdown] = useState(null);
  const [matchedOpponent, setMatchedOpponent] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);

  // Truthful real-time presence & online stats (Zero fake numbers)
  const [onlineStats, setOnlineStats] = useState({
    totalOnline: 1,
    otherOnline: 0,
    waitingInQueue: 0,
    activeBattles: 0,
    hasActiveOpponents: false,
  });

  // History and Stats
  const [history, setHistory] = useState([]);
  const [historyFilter, setHistoryFilter] = useState('All');
  const [historyLoading, setHistoryLoading] = useState(true);

  // Polling and Timer refs
  const pollIntervalRef = useRef(null);
  const searchTimerRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);

  // Fetch real online stats from backend
  const fetchOnlineStats = useCallback(async () => {
    try {
      const stats = await challengeService.getPvPOnlineStats();
      if (stats && typeof stats.totalOnline === 'number') {
        setOnlineStats(stats);
      }
    } catch (err) {
      // Quiet fail on background stats
    }
  }, []);

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

  // Periodic heartbeat & presence refresh every 10 seconds
  useEffect(() => {
    fetchHistory();
    fetchOnlineStats();

    heartbeatIntervalRef.current = setInterval(() => {
      fetchOnlineStats();
    }, 10000);

    return () => {
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [fetchHistory, fetchOnlineStats]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      if (searchTimerRef.current) clearInterval(searchTimerRef.current);
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
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

        // Check if another human player matched
        if (statusData.status === 'MATCHED' || (statusData.player2 && statusData.player2.name)) {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          if (searchTimerRef.current) {
            clearInterval(searchTimerRef.current);
            searchTimerRef.current = null;
          }

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
              navigate(`/pvp/arena/${statusData.battleId || statusData.id || battleId}`);
            }
          }, 1000);
        }
      } catch (err) {
        console.warn('Error polling battle status:', err);
      }
    }, 2000);
  }, [navigate, addToast]);

  // Start search timer for Quick Match (25 second timeout limit)
  const startSearchTimer = useCallback((battleId) => {
    if (searchTimerRef.current) {
      clearInterval(searchTimerRef.current);
    }
    setSearchSeconds(0);
    setIsSearchTimedOut(false);

    let elapsed = 0;
    searchTimerRef.current = setInterval(() => {
      elapsed += 1;
      setSearchSeconds(elapsed);

      // After 25 seconds of searching with no opponent:
      if (elapsed >= 25) {
        if (searchTimerRef.current) {
          clearInterval(searchTimerRef.current);
          searchTimerRef.current = null;
        }
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        setIsSearchTimedOut(true);
      }
    }, 1000);
  }, []);

  // 1. Quick Match Action (Real Humans Only)
  const handleQuickMatch = async () => {
    setIsQuickMatching(true);
    setWaitingType('quick_match');
    setIsSearchTimedOut(false);

    try {
      const battle = await challengeService.quickMatch({
        difficulty: selectedDifficulty,
        difficultyFilter: selectedDifficulty,
        timeLimit: selectedTimeLimit,
        timeLimitSeconds: selectedTimeLimit
      });

      const bId = battle?.battleId || battle?.id;
      if (!battle || !bId) {
        throw new Error('Could not initiate match.');
      }

      setActiveBattle(battle);
      setMatchedOpponent(null);
      setMatchFoundCountdown(null);

      // Check if immediately matched with a waiting human
      if (battle.status === 'MATCHED' && battle.player2) {
        setMatchedOpponent(battle.player2);
        setMatchFoundCountdown(3);
        setIsWaitingModalOpen(true);

        let count = 3;
        const countdownTimer = setInterval(() => {
          count -= 1;
          if (count > 0) {
            setMatchFoundCountdown(count);
          } else {
            clearInterval(countdownTimer);
            setIsWaitingModalOpen(false);
            navigate(`/pvp/arena/${bId}`);
          }
        }, 1000);
      } else {
        // Wait in queue and search for real human opponent
        setIsWaitingModalOpen(true);
        startStatusPolling(bId);
        startSearchTimer(bId);
        fetchOnlineStats();
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
    setWaitingType('custom_room');
    setIsSearchTimedOut(false);

    try {
      const battle = await challengeService.createBattle({
        difficulty: selectedDifficulty,
        difficultyFilter: selectedDifficulty,
        timeLimit: selectedTimeLimit,
        timeLimitSeconds: selectedTimeLimit
      });

      const bId = battle?.battleId || battle?.id;
      if (!battle || !bId) {
        throw new Error('Failed to create battle room.');
      }

      setActiveBattle(battle);
      setIsWaitingModalOpen(true);
      setMatchedOpponent(null);
      setMatchFoundCountdown(null);

      // Start polling for player 2 joining
      startStatusPolling(bId);
      fetchOnlineStats();

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
      const bId = battle?.battleId || battle?.id;
      if (!battle || !bId) {
        throw new Error('Invalid room code or room is full.');
      }

      if (addToast) addToast('Connected to battle room! Entering arena...', 'success');
      navigate(`/pvp/arena/${bId}`);
    } catch (err) {
      if (addToast) addToast(err?.message || 'Unable to join room. Verify code.', 'error');
    } finally {
      setIsJoining(false);
    }
  };

  // Cancel waiting battle
  const handleCancelBattle = async () => {
    setIsWaitingModalOpen(false);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    if (searchTimerRef.current) {
      clearInterval(searchTimerRef.current);
      searchTimerRef.current = null;
    }

    const bId = activeBattle?.battleId || activeBattle?.id;
    if (bId) {
      try {
        await challengeService.cancelBattle(bId);
      } catch (e) {}
    }
    setActiveBattle(null);
    setMatchedOpponent(null);
    setMatchFoundCountdown(null);
    setIsSearchTimedOut(false);
    setSearchSeconds(0);

    if (addToast) addToast('Matchmaking cancelled.', 'info');
  };

  // Retry searching for Quick Match
  const handleRetrySearch = () => {
    const bId = activeBattle?.battleId || activeBattle?.id;
    if (bId) {
      setIsSearchTimedOut(false);
      startStatusPolling(bId);
      startSearchTimer(bId);
      fetchOnlineStats();
    } else {
      handleQuickMatch();
    }
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
      <div className="relative overflow-hidden rounded-md bg-gradient-to-br from-white via-slate-50 to-cyan-50/40 dark:from-slate-900 dark:via-slate-900/90 dark:to-slate-950 border border-slate-200 dark:border-slate-800/80 p-8 shadow-sm dark:shadow-xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 hidden" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-64 h-64 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-bold tracking-wide uppercase">
                <Swords className="w-3.5 h-3.5 animate-pulse" />
                Live Multiplayer Arena
              </div>

              {/* Truthful Real-Time Online Presence Pill */}
              {onlineStats.otherOnline > 0 ? (
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-bold shadow-sm">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 " />
                  <span>{onlineStats.otherOnline} Developer{onlineStats.otherOnline === 1 ? '' : 's'} Online</span>
                  {onlineStats.waitingInQueue > 0 && (
                    <span className="text-[10px] text-emerald-500 dark:text-emerald-300 font-mono">
                      ({onlineStats.waitingInQueue} in queue)
                    </span>
                  )}
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-xs font-medium">
                  <span className="w-2 h-2 rounded-full bg-slate-400" />
                  <span>1 Online (You) • 0 In Queue</span>
                </div>
              )}
            </div>

            <h1 className="text-3xl md:text-4xl font-heading font-extrabold text-slate-900 dark:text-slate-100 tracking-tight flex items-center gap-3">
              <Swords className="w-7 h-7 text-rose-500 shrink-0 inline-block mr-2" /> PvP Debugging Battle
            </h1>
            <p className="text-slate-600 dark:text-slate-400 text-sm md:text-base leading-relaxed">
              Race in real-time against another developer to diagnose, isolate, and fix broken code first. Human vs. human — both developers receive the exact same bug report and codebase!
            </p>
          </div>

          {/* Quick Stats Pill Panel */}
          <div className="flex items-center gap-3 bg-white/70 dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-3 shadow-sm backdrop-blur-sm self-stretch md:self-auto justify-around">
            <div className="text-center px-3 border-r border-slate-200 dark:border-slate-800">
              <p className="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400 tracking-wider">Win Rate</p>
              <p className="text-xl font-heading font-extrabold text-cyan-600 dark:text-cyan-400">{winRate}%</p>
            </div>
            <div className="text-center px-3 border-r border-slate-200 dark:border-slate-800">
              <p className="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400 tracking-wider">Wins</p>
              <p className="text-xl font-heading font-extrabold text-emerald-600 dark:text-emerald-400">{wins}</p>
            </div>
            <div className="text-center px-3">
              <p className="text-[10px] uppercase font-bold text-slate-600 dark:text-slate-400 tracking-wider">Streak</p>
              <p className="text-xl font-heading font-extrabold text-amber-600 dark:text-amber-400 flex items-center justify-center gap-1">
                <Flame className="w-4 h-4" /> {currentStreak}
              </p>
            </div>
          </div>
        </div>

        {/* Global Match Preferences Bar */}
        <div className="mt-8 pt-6 border-t border-slate-200/80 dark:border-slate-800/80 flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Difficulty Selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-600 dark:text-slate-400">Difficulty:</span>
              <div className="inline-flex rounded-xl bg-slate-100 dark:bg-slate-950 p-1 border border-slate-200 dark:border-slate-800">
                {['All', 'Easy', 'Medium', 'Hard'].map((diff) => (
                  <button
                    key={diff}
                    onClick={() => setSelectedDifficulty(diff)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                      selectedDifficulty === diff
                        ? 'bg-white dark:bg-slate-800 text-cyan-600 dark:text-cyan-400 shadow-sm font-bold'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>

            {/* Time Limit Selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-600 dark:text-slate-400">Time:</span>
              <div className="inline-flex rounded-xl bg-slate-100 dark:bg-slate-950 p-1 border border-slate-200 dark:border-slate-800">
                {[
                  { label: '5 min', seconds: 300 },
                  { label: '10 min', seconds: 600 },
                  { label: '15 min', seconds: 900 }
                ].map((item) => (
                  <button
                    key={item.seconds}
                    onClick={() => setSelectedTimeLimit(item.seconds)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                      selectedTimeLimit === item.seconds
                        ? 'bg-white dark:bg-slate-800 text-cyan-600 dark:text-cyan-400 shadow-sm font-bold'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-600 dark:text-slate-400">
            <span className="flex items-center gap-1.5">
              <Award className="w-4 h-4 text-amber-500" />
              Victory: <strong className="text-slate-900 dark:text-slate-200 font-bold">+50 XP, +15 BugBytes</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Main 3 Action Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* 1. Quick Match Card */}
        <div className="relative group overflow-hidden rounded-md bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 p-6 flex flex-col justify-between shadow-sm hover:shadow-xl hover:border-cyan-500/40 transition-all duration-300">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center">
                <Zap className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                Instant Queue
              </span>
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                Quick Match
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Search for an available developer in the matchmaking pool. Automatic pairing with live opponents.
              </p>
            </div>
          </div>

          <div className="pt-6 space-y-2">
            <button
              onClick={handleQuickMatch}
              disabled={isQuickMatching}
              className="w-full button-primary py-3 rounded-xl font-bold flex items-center justify-center gap-2 group-hover: transition-all"
            >
              {isQuickMatching ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching for Opponent...</span>
                </>
              ) : (
                <>
                  <Swords className="w-4 h-4" />
                  <span>Find Opponent</span>
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
            <p className="text-[10px] text-center text-slate-600 dark:text-slate-400">
              {onlineStats.otherOnline > 0
                ? `${onlineStats.otherOnline} developer(s) currently online`
                : '1 online (you) • Searches live queue'}
            </p>
          </div>
        </div>

        {/* 2. Create Room Card */}
        <div className="relative group overflow-hidden rounded-md bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 p-6 flex flex-col justify-between shadow-sm hover:shadow-xl hover:border-purple-500/40 transition-all duration-300">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-600 dark:text-purple-400 flex items-center justify-center">
                <Users className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
                Private Duel
              </span>
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                Create Battle Room
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Generate a custom 6-character room code to challenge a friend, coworker, or community member directly.
              </p>
            </div>
          </div>

          <div className="pt-6 space-y-2">
            <button
              onClick={handleCreateRoom}
              disabled={isCreatingRoom}
              className="w-full bg-gradient-to-r from-purple-500 to-indigo-600 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:opacity-95 transition-all shadow-md"
            >
              {isCreatingRoom ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating Room...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Create Battle Room</span>
                </>
              )}
            </button>
            <p className="text-[10px] text-center text-slate-600 dark:text-slate-400">
              Generates a 6-character invite code
            </p>
          </div>
        </div>

        {/* 3. Join Room Card */}
        <div className="relative group overflow-hidden rounded-md bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 p-6 flex flex-col justify-between shadow-sm hover:shadow-xl hover:border-emerald-500/40 transition-all duration-300">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                <Code2 className="w-6 h-6" />
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                Join with Code
              </span>
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                Join Battle Room
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Enter an invitation code from a peer to jump directly into their customized battle arena.
              </p>
            </div>
          </div>

          <form onSubmit={handleJoinRoom} className="pt-6 space-y-3">
            <div className="relative">
              <input
                type="text"
                maxLength={6}
                value={customRoomCode}
                onChange={(e) => setCustomRoomCode(e.target.value.toUpperCase())}
                placeholder="ENTER ROOM CODE (e.g. 7X9K2P)"
                className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 text-xs font-mono font-bold text-center uppercase tracking-widest text-slate-900 dark:text-slate-100 placeholder:text-slate-600 dark:placeholder:text-slate-400 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
            <button
              type="submit"
              disabled={isJoining || !customRoomCode.trim()}
              className="w-full bg-slate-900 hover:bg-slate-800 dark:bg-slate-800 dark:hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isJoining ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  <span>Enter Room</span>
                </>
              )}
            </button>
          </form>
        </div>

      </div>

      {/* Battle Rules & Mechanism Card */}
      <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800/60 rounded-md p-6">
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-4 flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-500" />
          Multiplayer Rules & Scoring
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          <div className="space-y-1">
            <p className="font-bold text-slate-900 dark:text-slate-200">1. Identical Defect Workspace</p>
            <p>Both developers get the exact same broken challenge repository and hidden evaluation tests.</p>
          </div>
          <div className="space-y-1">
            <p className="font-bold text-slate-900 dark:text-slate-200">2. Live Progress Sync</p>
            <p>Watch your opponent's test pass count advance in real time as they run diagnostic tests.</p>
          </div>
          <div className="space-y-1">
            <p className="font-bold text-slate-900 dark:text-slate-200">3. First Valid Fix Wins</p>
            <p>The first player to pass 100% of test cases and submit wins +50 XP and +15 BugBytes!</p>
          </div>
        </div>
      </div>

      {/* Battle History Section */}
      <div className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-heading font-extrabold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Battle Records & Match History
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Track your duel history, performance rating, and previous opponents.
            </p>
          </div>

          {/* History Result Filter Tabs */}
          <div className="inline-flex rounded-xl bg-slate-100 dark:bg-slate-900 p-1 border border-slate-200 dark:border-slate-800 self-start sm:self-auto">
            {['All', 'Won', 'Lost'].map((filter) => (
              <button
                key={filter}
                onClick={() => setHistoryFilter(filter)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                  historyFilter === filter
                    ? 'bg-white dark:bg-slate-800 text-cyan-600 dark:text-cyan-400 shadow-sm font-bold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {/* History Table */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900/50 shadow-sm">
          {historyLoading ? (
            <div className="py-12 flex flex-col items-center justify-center text-slate-600 dark:text-slate-400 space-y-2">
              <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
              <p className="text-xs">Loading combat history...</p>
            </div>
          ) : filteredHistory.length === 0 ? (
            <div className="py-14 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 flex items-center justify-center mx-auto">
                <Swords className="w-6 h-6" />
              </div>
              <p className="text-sm font-bold text-slate-700 dark:text-slate-300">No PvP battles found</p>
              <p className="text-xs text-slate-600 dark:text-slate-400 max-w-sm mx-auto">
                Jump into Quick Match or invite a peer with a room code to record your first victory!
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 text-slate-600 dark:text-slate-400 uppercase tracking-wider text-[10px] font-bold">
                    <th className="py-3 px-4">Result</th>
                    <th className="py-3 px-4">Opponent</th>
                    <th className="py-3 px-4">Challenge</th>
                    <th className="py-3 px-4">Difficulty</th>
                    <th className="py-3 px-4">Tests Passed</th>
                    <th className="py-3 px-4">Solve Time</th>
                    <th className="py-3 px-4">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {filteredHistory.map((item, idx) => {
                    const isWon = item.result === 'Won';
                    return (
                      <tr 
                        key={item.id || idx}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="py-3.5 px-4 font-bold">
                          <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                            isWon
                              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
                          }`}>
                            {isWon ? <Trophy className="w-3 h-3" /> : <X className="w-3 h-3" />}
                            {item.result}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2">
                            {item.opponentAvatar ? (
                              <img 
                                src={item.opponentAvatar} 
                                alt={item.opponentName} 
                                className="w-6 h-6 rounded-full object-cover border border-slate-300 dark:border-slate-700" 
                              />
                            ) : (
                              <div className="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold flex items-center justify-center text-[10px]">
                                {item.opponentName?.slice(0, 2).toUpperCase() || 'OP'}
                              </div>
                            )}
                            <span className="font-bold text-slate-900 dark:text-slate-100">
                              {item.opponentName || 'Challenger'}
                            </span>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 font-medium text-slate-700 dark:text-slate-300 max-w-xs truncate">
                          {item.challengeTitle || 'Defect Reproduction'}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {item.difficulty || 'Medium'}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-mono font-bold text-slate-800 dark:text-slate-200">
                          {item.score || '100%'}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-slate-600 dark:text-slate-400">
                          {item.solveTime || '—'}
                        </td>
                        <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400">
                          {item.date || 'Recently'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* WAITING ROOM & MATCHMAKING MODAL */}
      {isWaitingModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-md animate-fade-in">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-md p-8 max-w-md w-full shadow-2xl relative overflow-hidden">
            
            {/* Background glow orb */}
            <div className="absolute top-0 right-0 -mt-10 -mr-10 w-48 h-48 hidden" />

            {/* STATE 1: Opponent Found & Countdown */}
            {matchFoundCountdown !== null ? (
              <div className="text-center space-y-6 animate-fade-in py-4">
                <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
                  <Swords className="w-8 h-8 " />
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
                        Developer • Rating {matchedOpponent.rating || 1450}
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30">
                      VS
                    </span>
                  </div>
                )}
              </div>

            ) : isSearchTimedOut && waitingType === 'quick_match' ? (

              /* STATE 2: Matchmaking Timeout — "No Players Found" */
              <div className="text-center space-y-6 py-2 animate-fade-in">
                <div className="w-16 h-16 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto shadow-sm">
                  <Users className="w-8 h-8" />
                </div>

                <div className="space-y-2">
                  <h3 className="text-2xl font-heading font-extrabold text-slate-900 dark:text-slate-100">
                    No Opponents Found
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed max-w-sm mx-auto">
                    We searched the matchmaking pool, but no other developers are currently queued for Quick Match.
                  </p>
                </div>

                {/* Real-time platform presence info (Truthful) */}
                <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 text-left space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <Radio className="w-3.5 h-3.5 text-cyan-500" />
                      Live Platform Presence
                    </span>
                    <span className="text-[11px] font-mono text-slate-600 dark:text-slate-400">
                      Real-time
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    {onlineStats.otherOnline === 0 ? (
                      <span>You are currently the only developer online. No other players are active on the site right now.</span>
                    ) : (
                      <span>{onlineStats.otherOnline} other developer(s) online, but none are currently queued in Quick Match.</span>
                    )}
                  </p>
                </div>

                {/* Action Choices */}
                <div className="space-y-2 pt-2">
                  <button
                    onClick={handleRetrySearch}
                    className="w-full button-primary py-2.5 text-xs font-bold flex items-center justify-center gap-2 shadow-sm"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Search Again</span>
                  </button>

                  <button
                    onClick={async () => {
                      await handleCancelBattle();
                      await handleCreateRoom();
                    }}
                    className="w-full bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 dark:text-purple-400 border border-purple-500/30 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-colors"
                  >
                    <Share2 className="w-3.5 h-3.5" />
                    <span>Create Battle Room to Play with Friends</span>
                  </button>

                  <button
                    onClick={handleCancelBattle}
                    className="w-full button-secondary py-2.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                  >
                    Back to Lobby
                  </button>
                </div>
              </div>

            ) : (

              /* STATE 3: Actively Searching / Waiting in Room */
              <div className="text-center space-y-6 py-2 animate-fade-in">
                
                {waitingType === 'quick_match' ? (
                  /* 3A: Quick Match Automated Search (NO ROOM CODE - randomly pairs online players) */
                  <>
                    <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                      <div className="absolute inset-0 rounded-full bg-cyan-500/20  opacity-75" />
                      <div className="relative w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-950 border-2 border-cyan-500/50 flex items-center justify-center text-cyan-600 dark:text-cyan-400 ">
                        <Swords className="w-7 h-7" />
                      </div>
                    </div>

                    <div className="space-y-1">
                      <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 flex items-center justify-center gap-2">
                        <span>Searching for Opponent</span>
                        <span className="flex gap-1">
                          <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full bg-cyan-500"></span>
                          <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full bg-cyan-500"></span>
                          <span className="w-1.5 h-1.5 bg-cyan-500 dark:bg-cyan-400 rounded-full "></span>
                        </span>
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        Searching the matchmaking pool ({searchSeconds}s)...
                      </p>
                    </div>

                    {/* Live Online Status */}
                    <div className="text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/60 rounded-xl py-3 px-4 border border-slate-200 dark:border-slate-800 text-center">
                      {onlineStats.otherOnline > 0 ? (
                        <span className="flex items-center justify-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold">
                          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                          {onlineStats.otherOnline} other developer(s) online • Looking for an available challenger...
                        </span>
                      ) : (
                        <span>
                          1 developer online (you) • Waiting for an opponent to join the queue...
                        </span>
                      )}
                    </div>

                    <p className="text-[11px] text-slate-500 dark:text-slate-400 max-w-xs mx-auto leading-relaxed">
                      Quick Match randomly pairs with online players. To play with a specific friend, use "Create Battle Room".
                    </p>

                    <div className="pt-2">
                      <button
                        onClick={handleCancelBattle}
                        className="w-full button-secondary py-2.5 text-xs text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 border-rose-300 dark:border-rose-500/30 bg-rose-50 dark:bg-rose-950/20"
                      >
                        Cancel Matchmaking
                      </button>
                    </div>
                  </>
                ) : (
                  /* 3B: Custom Battle Room (Private Duel with Friend - Room Code Shown) */
                  <>
                    <div className="w-16 h-16 rounded-2xl bg-purple-500/15 border border-purple-500/30 text-purple-600 dark:text-purple-400 flex items-center justify-center mx-auto shadow-sm">
                      <Users className="w-8 h-8 animate-pulse" />
                    </div>

                    <div className="space-y-1">
                      <h3 className="text-xl font-heading font-extrabold text-slate-900 dark:text-slate-100 flex items-center justify-center gap-2">
                        <span>Private Battle Room</span>
                        <span className="flex gap-1">
                          <span className="w-1.5 h-1.5 bg-purple-500 dark:bg-purple-400 rounded-full bg-cyan-500"></span>
                          <span className="w-1.5 h-1.5 bg-purple-500 dark:bg-purple-400 rounded-full bg-cyan-500"></span>
                          <span className="w-1.5 h-1.5 bg-purple-500 dark:bg-purple-400 rounded-full "></span>
                        </span>
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        Share this room code with your friend to connect and duel.
                      </p>
                    </div>

                    {/* Room Code Display Box (Exclusively for Custom Battle Room) */}
                    {activeBattle?.roomCode && (
                      <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <p className="text-[10px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-widest">
                            Battle Room Code
                          </p>
                          <span className="text-[10px] text-purple-600 dark:text-purple-400 font-bold">
                            Share with friend
                          </span>
                        </div>
                        <div className="flex items-center justify-between gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2.5 shadow-sm">
                          <span className="font-mono text-xl font-extrabold text-purple-600 dark:text-purple-400 tracking-wider">
                            {activeBattle.roomCode}
                          </span>
                          <button
                            onClick={handleCopyRoomCode}
                            className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
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

                    <div className="text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/60 rounded-xl py-2 px-3 border border-slate-200 dark:border-slate-800">
                      Waiting for your friend to enter this code in "Join Battle Room"...
                    </div>

                    <div className="pt-2">
                      <button
                        onClick={handleCancelBattle}
                        className="w-full button-secondary py-2.5 text-xs text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-rose-300 border-rose-300 dark:border-rose-500/30 bg-rose-50 dark:bg-rose-950/20"
                      >
                        Cancel Battle Room
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
