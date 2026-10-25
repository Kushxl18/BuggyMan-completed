import React, { useState, useEffect, useRef, useCallback } from 'react';

import { useParams, useNavigate } from 'react-router-dom';

import { 

  Swords, 

  Play, 

  Send, 

  RotateCcw, 

  ArrowLeft, 

  Sun, 

  Moon, 

  Loader2, 

  Trophy, 

  Crown, 

  AlertTriangle, 

  Clock, 

  CheckCircle2, 

  XCircle, 

  Zap, 

  User, 

  ShieldAlert, 

  Flame, 

  Sparkles, 

  RefreshCw, 

  Activity, 

  Check, 

  X,

  Volume2,

  VolumeX

} from 'lucide-react';

import ProblemStatementPanel from './Challenge/ProblemStatementPanel';

import CodeEditor from './Challenge/CodeEditor';

import OutputPanel from './Challenge/OutputPanel';

import { challengeService } from '../services/challengeService';

// Helper to normalize file schemas

const normalizeFiles = (rawFiles = []) => {

  if (!Array.isArray(rawFiles) || rawFiles.length === 0) {

    return [{ name: 'index.js', content: '// Write your solution here\n' }];

  }

  return rawFiles.map((file, index) => {

    if (typeof file === 'string') {

      return { name: `file${index + 1}.txt`, content: file };

    }

    const name = file?.name || file?.filename || file?.fileName || file?.path || `file${index + 1}.txt`;

    return {

      name,

      content: file?.content || file?.source || ''

    };

  });

};

const formatSeconds = (totalSeconds) => {

  if (totalSeconds < 0) totalSeconds = 0;

  const mins = Math.floor(totalSeconds / 60);

  const secs = totalSeconds % 60;

  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;

};

export default function PvPArena({ user, setUser, addToast, theme = 'dark', toggleTheme }) {

  const { battleId } = useParams();

  const navigate = useNavigate();

  // Core Battle State

  const [battle, setBattle] = useState(null);

  const [challenge, setChallenge] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  // Editor Workspace State

  const [files, setFiles] = useState([]);

  const [activeFile, setActiveFile] = useState(null);

  const [activeTab, setActiveTab] = useState('problem');

  const [isRunning, setIsRunning] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [runOutput, setRunOutput] = useState('');

  const [compileError, setCompileError] = useState('');

  // PvP Progress & Opponent tracking

  const [player1TestsPassed, setPlayer1TestsPassed] = useState(0);

  const [player2TestsPassed, setPlayer2TestsPassed] = useState(0);

  const [totalTestCases, setTotalTestCases] = useState(3);

  const [combatLogs, setCombatLogs] = useState([]);

  const [opponentStatus, setOpponentStatus] = useState('Coding solution...');

  // Timer Countdown State

  const [timeRemaining, setTimeRemaining] = useState(600); // 10 minutes default

  const [timerActive, setTimerActive] = useState(false);

  // Battle Result & Overlay State

  const [battleResult, setBattleResult] = useState(null); // null | { isWinner, winnerName, solveTime, xpEarned, message }

  const [showExitConfirm, setShowExitConfirm] = useState(false);

  // References for live synchronization

  const filesRef = useRef([]);

  const activeFileRef = useRef(null);

  const pollIntervalRef = useRef(null);

  const countdownIntervalRef = useRef(null);

  const hasFinishedRef = useRef(false);

  useEffect(() => {

    filesRef.current = files;

  }, [files]);

  useEffect(() => {

    activeFileRef.current = activeFile;

  }, [activeFile]);

  // Log combat events

  const addCombatLog = useCallback((message, type = 'info') => {

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    setCombatLogs(prev => [{ id: Math.random().toString(), timestamp, message, type }, ...prev.slice(0, 19)]);

  }, []);

  // 1. Initialize Battle on Mount

  useEffect(() => {

    let isMounted = true;

    async function initArena() {

      setLoading(true);

      setError(null);

      try {

        // Step 1: Fetch initial battle status

        let statusData;

        try {

          statusData = await challengeService.getBattleStatus(battleId);

        } catch (e) {

          console.warn('Initial status fetch failed, starting fresh battle session', e);

        }

        // Step 2: Call start battle endpoint

        try {

          await challengeService.startBattle(battleId);

        } catch (startErr) {

          console.warn('Battle already started or start endpoint bypassed', startErr);

        }

        if (!isMounted) return;

        // If no challenge is present from statusData, fallback to default challenge

        let loadedChallenge = statusData?.challenge;

        if (!loadedChallenge) {

          try {

            loadedChallenge = await challengeService.getChallengeById('RE-E01');

          } catch (cErr) {

            loadedChallenge = {

              id: 'pvp-default',

              title: 'Fix React State Mutation Bug',

              description: 'The counter state does not increment because state is being mutated directly.\n\nFix the handler to update state immutably.',

              difficulty: 'Easy',

              technology: 'React',

              category: 'State Management',

              testCases: [

                { id: 1, name: 'State increments immutably', input: 'click', expected: '1', passed: false },

                { id: 2, name: 'Multiple clicks register sequentially', input: 'click x3', expected: '3', passed: false },

                { id: 3, name: 'No direct state mutation warning', input: 'audit', expected: 'pure', passed: false }

              ],

              files: [

                {

                  name: 'Counter.jsx',

                  content: `import React, { useState } from 'react';\n\nexport default function Counter() {\n  let [count, setCount] = useState(0);\n\n  const handleIncrement = () => {\n    // BUG: Mutating count directly instead of calling setCount with new value\n    count = count + 1;\n    setCount(count);\n  };\n\n  return (\n    <div className="p-4 text-center">\n      <h2 className="text-xl font-bold">Counter: {count}</h2>\n      <button onClick={handleIncrement} className="px-4 py-2 bg-cyan-500 text-white rounded mt-2">\n        Increment\n      </button>\n    </div>\n  );\n}`

                }

              ]

            };

          }

        }

        const normalized = normalizeFiles(loadedChallenge?.files || []);

        setChallenge(loadedChallenge);

        setFiles(normalized);

        filesRef.current = normalized;

        setActiveFile(normalized[0] || null);

        activeFileRef.current = normalized[0] || null;

        const totalTests = loadedChallenge?.testCases?.length || 3;

        setTotalTestCases(totalTests);

        // Configure timer

        const initialTime = statusData?.timeRemaining || statusData?.timeLimit || 600;

        setTimeRemaining(initialTime);

        setTimerActive(true);

        // Update battle object

        setBattle(statusData || {

          battleId,

          player1: { name: user?.name || 'You', avatar: user?.avatar },

          player2: { name: 'Challenger', rating: 1450 }

        });

        addCombatLog('Battle arena initialized. Both developers have identical files!', 'system');

        addCombatLog('Clock started. First developer to pass all tests wins!', 'system');

      } catch (err) {

        if (isMounted) {

          setError(err?.message || 'Failed to initialize PvP arena.');

          if (addToast) addToast('Error loading battle session.', 'error');

        }

      } finally {

        if (isMounted) setLoading(false);

      }

    }

    initArena();

    return () => {

      isMounted = false;

      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

    };

  }, [battleId, user, addToast, addCombatLog]);

  // 2. Timer Countdown Effect

  useEffect(() => {

    if (!timerActive || battleResult) {

      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

      return;

    }

    countdownIntervalRef.current = setInterval(() => {

      setTimeRemaining(prev => {

        if (prev <= 1) {

          clearInterval(countdownIntervalRef.current);

          handleTimeExpired();

          return 0;

        }

        return prev - 1;

      });

    }, 1000);

    return () => {

      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

    };

  }, [timerActive, battleResult]);

  // 3. Status Polling Effect (every 3 seconds for opponent progress)

  useEffect(() => {

    if (loading || battleResult) return;

    pollIntervalRef.current = setInterval(async () => {

      if (hasFinishedRef.current) return;

      try {

        const latest = await challengeService.getBattleStatus(battleId);

        if (!latest) return;

        setBattle(prev => ({ ...prev, ...latest }));

        // Update opponent progress

        const oppProg = latest.player2Progress || latest.player2_progress || {};

        const oppTests = oppProg.tests_passed ?? latest.player2?.testsPassed ?? latest.player2?.tests_passed ?? 0;

        setPlayer2TestsPassed(prev => {

          if (oppTests > prev) {

            addCombatLog(`Opponent passed test ${oppTests}/${totalTestCases}!`, 'warning');

            setOpponentStatus(`Passed test ${oppTests}/${totalTestCases}`);

          }

          return oppTests;

        });

        // Check if opponent finished all tests first

        if (oppTests >= totalTestCases && !hasFinishedRef.current && (latest.status === 'COMPLETED' || oppProg.submitted)) {

          handleOpponentWon(latest.player2);

        }

        // Check if status is COMPLETED

        if (latest.status === 'COMPLETED' && !hasFinishedRef.current) {

          const winnerId = latest.winner?.id || latest.winnerId || latest.winner;

          const isWinner = Boolean(latest.isWinner ?? (winnerId === user?.id || latest.winner === 'usr-current'));

          finishBattle({

            isWinner,

            winnerName: isWinner ? (user?.name || 'You') : (latest.player2?.name || 'Opponent'),

            solveTime: formatSeconds(600 - (latest.timeRemaining || timeRemaining)),

            xpEarned: isWinner ? 150 : 40,

            message: isWinner 

              ? 'Flawless Victory! You fixed the bug and passed all test cases first!' 

              : 'Defeat! Your opponent submitted a passing solution before you.'

          });

        }

      } catch (err) {

        console.warn('PvP polling warning:', err);

      }

    }, 3000);

    return () => {

      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    };

  }, [battleId, loading, battleResult, totalTestCases, user, timeRemaining, addCombatLog]);

  // Handle battle completion

  const finishBattle = (resultData) => {

    hasFinishedRef.current = true;

    setTimerActive(false);

    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

    setBattleResult(resultData);

    if (resultData.isWinner) {

      if (addToast) addToast('VICTORY! All tests passed first!', 'success');

      // Update user BugBytes / XP if setUser is available

      if (typeof setUser === 'function') {

        setUser(prev => prev ? ({ ...prev, totalScore: (prev.totalScore || 0) + (resultData.xpEarned || 150) }) : prev);

      }

    } else {

      if (addToast) addToast('Battle finished. Better luck next time!', 'info');

    }

  };

  // Handle opponent winning first

  const handleOpponentWon = (opp) => {

    finishBattle({

      isWinner: false,

      winnerName: opp?.name || 'Opponent',

      solveTime: formatSeconds(600 - timeRemaining),

      xpEarned: 40,

      message: `${opp?.name || 'Your opponent'} submitted a complete fix first!`

    });

  };

  // Handle timer reaching 0:00

  const handleTimeExpired = async () => {

    addCombatLog('Time limit expired! Evaluating final code...', 'system');

    await handleSubmitSolution();

  };

  // File selection

  const handleSelectFile = (file) => {

    const currentActive = activeFileRef.current || activeFile;

    const updatedFiles = (filesRef.current || files).map(f => 

      f.name === currentActive?.name ? { ...f, content: currentActive.content } : f

    );

    filesRef.current = updatedFiles;

    setFiles(updatedFiles);

    activeFileRef.current = file;

    setActiveFile(file);

  };

  // Code edit

  const handleCodeChange = (newContent) => {

    const currentActive = activeFileRef.current || activeFile;

    if (currentActive) {

      const updatedActive = { ...currentActive, content: newContent };

      activeFileRef.current = updatedActive;

      setActiveFile(updatedActive);

      const updatedFiles = (filesRef.current || files).map(f => 

        f.name === currentActive.name ? { ...f, content: newContent } : f

      );

      filesRef.current = updatedFiles;

      setFiles(updatedFiles);

    }

  };

  // Reset code to initial state

  const handleResetCode = () => {

    if (window.confirm('Reset your code files back to initial buggy state?')) {

      const defaultFiles = normalizeFiles(challenge?.files || []);

      filesRef.current = defaultFiles;

      setFiles(defaultFiles);

      activeFileRef.current = defaultFiles[0] || null;

      setActiveFile(defaultFiles[0] || null);

      setRunOutput('');

      setCompileError('');

      if (addToast) addToast('Workspace code reset.', 'info');

    }

  };

  // Run Code & Tests

  const handleRunCode = async () => {

    if (!challenge || isRunning) return;

    setIsRunning(true);

    setRunOutput('');

    setCompileError('');

    addCombatLog('Running tests on your code...', 'info');

    try {

      const currentActive = activeFileRef.current || activeFile;

      const currentFiles = filesRef.current || files;

      const syncedFiles = currentFiles.map(f => 

        f.name === currentActive?.name ? { ...f, content: currentActive.content } : f

      );

      const primaryFile = syncedFiles.find(f => f.name === currentActive?.name) || syncedFiles[0];

      // Execute code

      const res = await challengeService.runChallenge(challenge.id, primaryFile?.content || '', syncedFiles);

      // Extract test cases

      const returnedCases = res?.testCases || res?.test_cases || [];

      let passedCount = 0;

      if (returnedCases.length > 0) {

        setChallenge(prev => prev ? { ...prev, testCases: returnedCases } : prev);

        passedCount = returnedCases.filter(t => t.passed).length;

      } else if (res?.success) {

        passedCount = totalTestCases;

      }

      setPlayer1TestsPassed(passedCount);

      // Post progress update to PvP backend

      try {

        await challengeService.updateBattleProgress(battleId, {

          testsPassed: passedCount,

          testsTotal: totalTestCases,

          totalTests: totalTestCases

        });

      } catch (pErr) {

        console.warn('Progress update failed:', pErr);

      }

      // Display console outputs

      let logs = res?.stdout || '';

      if (res?.aiSummary) logs = `[EVALUATOR]\n${res.aiSummary}\n\n` + logs;

      setRunOutput(logs || (res?.success ? 'All tests passed cleanly!' : 'Tests executed with failures.'));

      if (res?.stderr || res?.error) {

        setCompileError(res.stderr || res.error);

      }

      addCombatLog(`Your tests completed: ${passedCount}/${totalTestCases} passing`, passedCount === totalTestCases ? 'success' : 'info');

      if (passedCount === totalTestCases) {

        if (addToast) addToast('All tests passing! Ready to submit.', 'success');

      } else {

        if (addToast) addToast(`Passed ${passedCount}/${totalTestCases} tests.`, 'info');

      }

    } catch (err) {

      setCompileError(err?.message || 'Execution error');

      addCombatLog(`Execution failed: ${err?.message || 'Error'}`, 'error');

      if (addToast) addToast('Error running code tests.', 'error');

    } finally {

      setIsRunning(false);

    }

  };

  // Submit Final Solution

  const handleSubmitSolution = async () => {

    if (isSubmitting || hasFinishedRef.current) return;

    setIsSubmitting(true);

    addCombatLog('Submitting solution to evaluator...', 'system');

    try {

      const currentActive = activeFileRef.current || activeFile;

      const currentFiles = filesRef.current || files;

      const syncedFiles = currentFiles.map(f => 

        f.name === currentActive?.name ? { ...f, content: currentActive.content } : f

      );

      const primaryFile = syncedFiles.find(f => f.name === currentActive?.name) || syncedFiles[0];

      const res = await challengeService.submitBattleSolution(battleId, primaryFile?.content || '', syncedFiles);

      const winnerId = res?.winner?.id || res?.winnerId || res?.winner;

      const isWin = Boolean(res?.isWinner ?? (winnerId === user?.id || res?.winner === 'usr-current' || res?.success));

      const solveTimeStr = formatSeconds(res?.solveTime || (600 - timeRemaining));

      finishBattle({

        isWinner: Boolean(isWin),

        winnerName: isWin ? (user?.name || 'You') : (battle?.player2?.name || 'Opponent'),

        solveTime: solveTimeStr,

        xpEarned: res?.xpEarned || (isWin ? 150 : 40),

        message: res?.message || (isWin 

          ? 'Victory! You solved the debugging challenge first!' 

          : 'Submission evaluated. Opponent took first place.')

      });

    } catch (err) {

      console.warn('Submit error fallback:', err);

      // Fallback submit evaluation based on current passed tests

      const isWin = player1TestsPassed >= player2TestsPassed && player1TestsPassed > 0;

      finishBattle({

        isWinner: isWin,

        winnerName: isWin ? (user?.name || 'You') : (battle?.player2?.name || 'Opponent'),

        solveTime: formatSeconds(600 - timeRemaining),

        xpEarned: isWin ? 150 : 40,

        message: isWin 

          ? 'Victory! You solved the debugging challenge first!' 

          : 'Opponent finished with a higher test score.'

      });

    } finally {

      setIsSubmitting(false);

    }

  };

  // Quit match handler

  const handleExitMatch = () => {

    if (!battleResult) {

      setShowExitConfirm(true);

    } else {

      navigate('/pvp');

    }

  };

  const confirmExit = async () => {

    try {

      await challengeService.cancelBattle(battleId);

    } catch (e) {}

    navigate('/pvp');

  };

  if (loading) {

    return (

      <div className="h-screen w-screen flex flex-col items-center justify-center bg-slate-950 text-slate-100 gap-4 select-none">

        <div className="relative">

          <div className="w-16 h-16 rounded-full border-4 border-slate-800 border-t-cyan-500 animate-spin" />

          <Swords className="w-6 h-6 text-rose-500 absolute inset-0 m-auto" />

        </div>

        <div className="text-center space-y-1">

          <h2 className="text-lg font-heading font-bold">Synchronizing PvP Arena</h2>

          <p className="text-xs text-slate-500 font-mono">Generating identical sandbox environment...</p>

        </div>

      </div>

    );

  }

  if (error && !challenge) {

    return (

      <div className="h-screen w-screen flex flex-col items-center justify-center bg-slate-950 text-slate-100 p-6">

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-md w-full text-center space-y-4 shadow-2xl">

          <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center mx-auto">

            <AlertTriangle className="w-6 h-6" />

          </div>

          <h2 className="text-xl font-heading font-bold">Arena Connection Lost</h2>

          <p className="text-xs text-slate-400">{error}</p>

          <button

            onClick={() => navigate('/pvp')}

            className="w-full button-primary py-2.5 text-xs font-bold"

          >

            Return to PvP Lobby

          </button>

        </div>

      </div>

    );

  }

  const isTimerCritical = timeRemaining < 60;

  const p1Ratio = Math.round((player1TestsPassed / (totalTestCases || 1)) * 100);

  const p2Ratio = Math.round((player2TestsPassed / (totalTestCases || 1)) * 100);

  return (

    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden select-none font-sans">

      

      {/* ARENA TOP BAR */}

      <header className="h-16 bg-slate-900/95 border-b border-slate-800/90 flex items-center justify-between px-4 gap-4 shrink-0 shadow-md">

        

        {/* Left: Back / Title */}

        <div className="flex items-center gap-3 min-w-0">

          <button

            onClick={handleExitMatch}

            className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-slate-100 transition-colors"

            title="Leave Battle"

          >

            <ArrowLeft className="w-4 h-4" />

          </button>

          

          <div className="min-w-0 truncate">

            <div className="flex items-center gap-2">

              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1">

                <Swords className="w-3 h-3" /> PvP

              </span>

              <h1 className="text-sm font-heading font-bold text-slate-100 truncate">

                {challenge?.title || 'PvP Debugging Battle'}

              </h1>

            </div>

            <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider truncate">

              {challenge?.technology} • {challenge?.difficulty}

            </p>

          </div>

        </div>

        {/* Center: DUAL PLAYER PROGRESS INDICATOR */}

        <div className="flex items-center gap-4 bg-slate-950/80 border border-slate-800/80 px-4 py-1.5 rounded-2xl max-w-xl w-full justify-between">

          

          {/* Player 1 (You) */}

          <div className="flex items-center gap-2.5 min-w-0 flex-1">

            {user?.avatar ? (

              <img src={user.avatar} alt="You" className="w-7 h-7 rounded-full object-cover border border-cyan-500 shrink-0" />

            ) : (

              <div className="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-300 font-bold text-[10px] flex items-center justify-center border border-cyan-500 shrink-0">

                YOU

              </div>

            )}

            <div className="min-w-0 flex-1">

              <div className="flex items-center justify-between text-[11px] mb-1">

                <span className="font-bold text-cyan-400 truncate">You</span>

                <span className="font-mono text-[10px] font-bold text-cyan-300">{player1TestsPassed}/{totalTestCases} Tests</span>

              </div>

              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

                <div 

                  className="h-full bg-cyan-500 transition-all duration-300 rounded-full" 

                  style={{ width: `${p1Ratio}%` }} 

                />

              </div>

            </div>

          </div>

          {/* VS Center Badge & Timer */}

          <div className="flex flex-col items-center px-3 border-x border-slate-800/80 shrink-0">

            <div className={`flex items-center gap-1 font-mono text-xs font-extrabold ${

              isTimerCritical ? 'text-rose-400 animate-pulse' : 'text-slate-200'

            }`}>

              <Clock className={`w-3.5 h-3.5 ${isTimerCritical ? 'text-rose-500' : 'text-cyan-400'}`} />

              <span>{formatSeconds(timeRemaining)}</span>

            </div>

            <span className="text-[9px] font-extrabold uppercase tracking-widest text-slate-500">

              VS

            </span>

          </div>

          {/* Player 2 (Opponent) */}

          <div className="flex items-center gap-2.5 min-w-0 flex-1 justify-end">

            <div className="min-w-0 flex-1 text-right">

              <div className="flex items-center justify-between text-[11px] mb-1">

                <span className="font-mono text-[10px] font-bold text-rose-300">{player2TestsPassed}/{totalTestCases} Tests</span>

                <span className="font-bold text-rose-400 truncate">{battle?.player2?.name || 'Opponent'}</span>

              </div>

              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

                <div 

                  className="h-full bg-rose-500 transition-all duration-300 rounded-full ml-auto" 

                  style={{ width: `${p2Ratio}%` }} 

                />

              </div>

            </div>

            {battle?.player2?.avatar ? (

              <img src={battle.player2.avatar} alt="Opponent" className="w-7 h-7 rounded-full object-cover border border-rose-500 shrink-0" />

            ) : (

              <div className="w-7 h-7 rounded-full bg-rose-500/20 text-rose-300 font-bold text-[10px] flex items-center justify-center border border-rose-500 shrink-0">

                OP

              </div>

            )}

          </div>

        </div>

        {/* Right: Controls & Submission */}

        <div className="flex items-center gap-2 shrink-0">

          <button

            onClick={toggleTheme}

            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-400 hover:text-slate-200 transition-colors"

            title="Toggle editor theme"

          >

            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}

          </button>

          <button

            onClick={handleResetCode}

            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-400 hover:text-slate-200 transition-colors"

            title="Reset workspace files"

          >

            <RotateCcw className="w-4 h-4" />

          </button>

          {/* Run Code Button */}

          <button

            onClick={handleRunCode}

            disabled={isRunning || Boolean(battleResult)}

            className="button-secondary px-3.5 py-2 text-xs border-cyan-500/30 text-cyan-400 bg-cyan-950/20 hover:bg-cyan-950/40 disabled:opacity-50 font-bold flex items-center gap-1.5"

          >

            {isRunning ? (

              <>

                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />

                <span>Running...</span>

              </>

            ) : (

              <>

                <Play className="w-3.5 h-3.5 fill-cyan-400" />

                <span>Run Code</span>

              </>

            )}

          </button>

          {/* Submit Solution Button */}

          <button

            onClick={handleSubmitSolution}

            disabled={isSubmitting || isRunning || Boolean(battleResult)}

            className="button-primary px-4 py-2 text-xs font-bold disabled:opacity-50 flex items-center gap-1.5 shadow-lg shadow-cyan-500/20"

          >

            {isSubmitting ? (

              <>

                <Loader2 className="w-3.5 h-3.5 animate-spin text-white" />

                <span>Submitting...</span>

              </>

            ) : (

              <>

                <Send className="w-3.5 h-3.5" />

                <span>Submit Solution</span>

              </>

            )}

          </button>

        </div>

      </header>

      {/* ARENA CENTRAL WORKSPACE */}

      <div className="flex-1 flex overflow-hidden">

        

        {/* Left Side: Problem Statement Panel */}

        <ProblemStatementPanel

          challenge={challenge}

          files={files}

          activeFile={activeFile}

          onSelectFile={handleSelectFile}

          activeTab={activeTab}

          setActiveTab={setActiveTab}

          addToast={addToast}

        />

        {/* Center: Monaco Editor & Output Panel */}

        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden border-r border-slate-800">

          

          {/* File Tabs Selector */}

          <div className="h-9 bg-slate-950/90 border-b border-slate-800/80 flex items-center px-2 select-none gap-1 overflow-x-auto shrink-0">

            {files.map(f => (

              <button

                key={f.name}

                onClick={() => handleSelectFile(f)}

                className={`px-3 py-1.5 text-xs font-medium rounded-t-lg transition-all ${

                  f.name === activeFile?.name

                    ? 'bg-slate-900 text-slate-100 border-t-2 border-cyan-500 font-semibold'

                    : 'text-slate-500 hover:text-slate-300 hover:bg-slate-900/40'

                }`}

              >

                {f.name}

              </button>

            ))}

          </div>

          {/* Monaco Editor Container */}

          <div className="flex-1 min-h-[300px] relative flex flex-col w-full overflow-hidden">

            <CodeEditor

              file={activeFile}

              onChange={handleCodeChange}

              theme={theme}

            />

          </div>

          {/* Output & Terminal Panel */}

          <OutputPanel

            challenge={challenge}

            userCode={activeFile?.content || ''}

            testCases={challenge?.testCases || []}

            runOutput={runOutput}

            isRunning={isRunning}

            compileError={compileError}

            files={files}

            technology={challenge?.technology}

          />

        </div>

        {/* Right Side: Opponent Live Progress & Combat Log Panel */}

        <div className="w-80 bg-slate-900/90 flex flex-col h-full border-l border-slate-800 shrink-0 overflow-hidden">

          

          {/* Opponent Card Header */}

          <div className="p-4 border-b border-slate-800 bg-slate-950/60 space-y-3">

            <div className="flex items-center justify-between">

              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">

                <Activity className="w-3.5 h-3.5 text-rose-500 animate-pulse" />

                Opponent Telemetry

              </span>

              <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-400 border border-rose-500/20">

                Live

              </span>

            </div>

            <div className="flex items-center gap-3">

              {battle?.player2?.avatar ? (

                <img 

                  src={battle.player2.avatar} 

                  alt="Opponent" 

                  className="w-10 h-10 rounded-full object-cover border border-rose-500/60" 

                />

              ) : (

                <div className="w-10 h-10 rounded-full bg-rose-500/20 text-rose-300 font-bold text-xs flex items-center justify-center border border-rose-500/40">

                  {battle?.player2?.name?.slice(0, 2).toUpperCase() || 'OP'}

                </div>

              )}

              <div className="min-w-0 flex-1">

                <p className="text-sm font-heading font-bold text-slate-100 truncate">

                  {battle?.player2?.name || 'CyberSamurai'}

                </p>

                <p className="text-[11px] text-slate-400 font-mono">

                  Rating: {battle?.player2?.rating || 1450} • Gold Tier

                </p>

              </div>

            </div>

            {/* Opponent Test Progress Bar */}

            <div className="space-y-1.5 pt-1">

              <div className="flex items-center justify-between text-xs font-semibold">

                <span className="text-slate-400">Tests Passing</span>

                <span className="font-mono text-rose-400 font-bold">{player2TestsPassed} / {totalTestCases}</span>

              </div>

              <div className="w-full h-2 bg-slate-950 rounded-full border border-slate-800 overflow-hidden">

                <div 

                  className="h-full bg-rose-500 transition-all duration-500 rounded-full shadow-glow-rose"

                  style={{ width: `${p2Ratio}%` }}

                />

              </div>

            </div>

            {/* Live Status Pill */}

            <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-xs flex items-center gap-2">

              <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />

              <span className="text-slate-300 font-medium truncate">{opponentStatus}</span>

            </div>

          </div>

          {/* Test Cases Status Checklist */}

          <div className="p-4 border-b border-slate-800/80 space-y-2">

            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">

              Test Suite Progression

            </h3>

            <div className="space-y-1.5">

              {Array.from({ length: totalTestCases }).map((_, idx) => {

                const isPassedYou = idx < player1TestsPassed;

                const isPassedOpponent = idx < player2TestsPassed;

                return (

                  <div 

                    key={idx} 

                    className="flex items-center justify-between p-2 rounded-xl bg-slate-950/70 border border-slate-800/60 text-xs"

                  >

                    <span className="font-medium text-slate-300">Test Case #{idx + 1}</span>

                    <div className="flex items-center gap-3">

                      {/* You */}

                      <span className={`flex items-center gap-1 text-[10px] font-bold ${

                        isPassedYou ? 'text-cyan-400' : 'text-slate-600'

                      }`}>

                        {isPassedYou ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}

                        You

                      </span>

                      {/* Opponent */}

                      <span className={`flex items-center gap-1 text-[10px] font-bold ${

                        isPassedOpponent ? 'text-rose-400' : 'text-slate-600'

                      }`}>

                        {isPassedOpponent ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}

                        Enemy

                      </span>

                    </div>

                  </div>

                );

              })}

            </div>

          </div>

          {/* Live Battle Combat Log */}

          <div className="flex-1 flex flex-col min-h-0 p-4 space-y-2">

            <h3 className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">

              <span>Combat Log</span>

              <span className="text-[10px] text-slate-500 font-mono">Live</span>

            </h3>

            <div className="flex-1 overflow-y-auto space-y-2 pr-1 text-[11px] font-mono">

              {combatLogs.map((log) => (

                <div 

                  key={log.id} 

                  className={`p-2 rounded-lg border leading-tight ${

                    log.type === 'system' ? 'bg-cyan-950/20 border-cyan-500/20 text-cyan-300' :

                    log.type === 'warning' ? 'bg-rose-950/20 border-rose-500/20 text-rose-300' :

                    log.type === 'success' ? 'bg-emerald-950/20 border-emerald-500/20 text-emerald-300' :

                    log.type === 'error' ? 'bg-rose-950/40 border-rose-500/40 text-rose-400' :

                    'bg-slate-950 border-slate-800 text-slate-400'

                  }`}

                >

                  <span className="text-[10px] text-slate-500 block mb-0.5">{log.timestamp}</span>

                  {log.message}

                </div>

              ))}

            </div>

          </div>

        </div>

      </div>

      {/* CONFIRM EXIT MODAL */}

      {showExitConfirm && (

        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-sm w-full space-y-4 shadow-2xl">

            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center mx-auto">

              <ShieldAlert className="w-6 h-6" />

            </div>

            <div className="text-center space-y-1">

              <h3 className="text-lg font-heading font-bold text-slate-100">Forfeit Battle?</h3>

              <p className="text-xs text-slate-400 leading-relaxed">

                Leaving an ongoing multiplayer battle will result in an automatic forfeit and rating penalty.

              </p>

            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">

              <button

                onClick={() => setShowExitConfirm(false)}

                className="button-secondary py-2.5 text-xs font-semibold"

              >

                Keep Fighting

              </button>

              <button

                onClick={confirmExit}

                className="bg-rose-600 hover:bg-rose-500 text-white font-bold py-2.5 px-3 rounded-xl text-xs transition-colors"

              >

                Forfeit & Exit

              </button>

            </div>

          </div>

        </div>

      )}

      {/* FULL-SCREEN BATTLE RESULTS OVERLAY */}

      {battleResult && (

        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md animate-fade-in">

          

          {/* Confetti Particle Animation (CSS keyframe based) */}

          {battleResult.isWinner && (

            <div className="absolute inset-0 pointer-events-none overflow-hidden">

              {Array.from({ length: 40 }).map((_, i) => (

                <div

                  key={i}

                  className="absolute w-2 h-2 rounded-full opacity-80 animate-ping"

                  style={{

                    backgroundColor: ['#06b6d4', '#3b82f6', '#f59e0b', '#10b981', '#ec4899'][i % 5],

                    top: `${Math.random() * 90}%`,

                    left: `${Math.random() * 95}%`,

                    animationDuration: `${1 + Math.random() * 2}s`,

                    animationDelay: `${Math.random() * 0.5}s`

                  }}

                />

              ))}

            </div>

          )}

          <div className="relative bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-8 max-w-lg w-full text-center space-y-6 shadow-2xl overflow-hidden">

            

            {/* Ambient Winner Aura */}

            <div className={`absolute top-0 left-1/2 -translate-x-1/2 -mt-16 w-64 h-64 rounded-full blur-3xl pointer-events-none ${

              battleResult.isWinner ? 'bg-cyan-500/20' : 'bg-rose-500/15'

            }`} />

            {/* Winner Trophy / Crown Badge */}

            <div className="relative">

              <div className={`w-20 h-20 rounded-3xl mx-auto flex items-center justify-center shadow-xl border ${

                battleResult.isWinner 

                  ? 'bg-gradient-to-tr from-amber-500 to-yellow-300 text-slate-950 border-amber-300 shadow-amber-500/30'

                  : 'bg-rose-950/60 border-rose-500/40 text-rose-400 shadow-rose-500/20'

              }`}>

                {battleResult.isWinner ? (

                  <Crown className="w-10 h-10 animate-bounce" />

                ) : (

                  <Swords className="w-10 h-10" />

                )}

              </div>

            </div>

            {/* Result Title & Subtitle */}

            <div className="space-y-1 relative z-10">

              <h2 className={`text-3xl font-heading font-extrabold tracking-tight ${

                battleResult.isWinner ? 'text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-cyan-400 to-blue-400' : 'text-slate-200'

              }`}>

                {battleResult.isWinner ? 'VICTORY!' : 'DEFEAT'}

              </h2>

              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">

                {battleResult.message}

              </p>

            </div>

            {/* Head-to-Head Performance Card */}

            <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-4 space-y-3 relative z-10">

              <div className="grid grid-cols-2 gap-4 divide-x divide-slate-800">

                {/* You */}

                <div className="space-y-1 text-center">

                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">You</p>

                  <p className="text-xl font-heading font-extrabold text-cyan-400">

                    {player1TestsPassed} / {totalTestCases}

                  </p>

                  <p className="text-[10px] text-slate-500 font-mono">Tests Passed</p>

                </div>

                {/* Opponent */}

                <div className="space-y-1 text-center pl-4">

                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">

                    {battle?.player2?.name || 'Opponent'}

                  </p>

                  <p className="text-xl font-heading font-extrabold text-rose-400">

                    {player2TestsPassed} / {totalTestCases}

                  </p>

                  <p className="text-[10px] text-slate-500 font-mono">Tests Passed</p>

                </div>

              </div>

              {/* Match Stats row */}

              <div className="border-t border-slate-800/80 pt-3 flex items-center justify-around text-xs">

                <div>

                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Solve Time</span>

                  <span className="font-mono font-bold text-slate-200">{battleResult.solveTime}</span>

                </div>

                <div>

                  <span className="text-[10px] font-bold text-slate-500 uppercase block">XP Earned</span>

                  <span className="font-mono font-bold text-emerald-400">+{battleResult.xpEarned} XP</span>

                </div>

                <div>

                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Rating Change</span>

                  <span className={`font-mono font-bold ${battleResult.isWinner ? 'text-cyan-400' : 'text-rose-400'}`}>

                    {battleResult.isWinner ? '+24 pts' : '-12 pts'}

                  </span>

                </div>

              </div>

            </div>

            {/* Action Buttons */}

            <div className="grid grid-cols-2 gap-3 pt-2 relative z-10">

              <button

                onClick={() => navigate('/pvp')}

                className="button-secondary py-3 text-xs font-bold"

              >

                Back to Lobby

              </button>

              <button

                onClick={() => {

                  setBattleResult(null);

                  navigate('/pvp');

                }}

                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-3 rounded-xl text-xs transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"

              >

                <Swords className="w-4 h-4" />

                <span>Next Battle</span>

              </button>

            </div>

          </div>

        </div>

      )}

    </div>

  );

}

