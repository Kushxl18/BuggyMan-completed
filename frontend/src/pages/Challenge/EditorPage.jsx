import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Play, 
  Send, 
  RotateCcw, 
  Sparkles, 
  Timer as TimerIcon, 
  Menu,
  ChevronLeft,
  ChevronRight,
  Shuffle,
  Sun,
  Moon,
  Loader2,
  Code2,
  CheckCircle2,
  Cloud,
  FileCode,
  Coins,
  User as UserIcon
} from 'lucide-react';
import ProblemStatementPanel from './ProblemStatementPanel';
import CodeEditor from './CodeEditor';
import AIHintPanel from './AIHintPanel';
import OutputPanel from './OutputPanel';
import LoadingSpinner from '../../components/LoadingSpinner';
import { challengeService } from '../../services/challengeService';

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

const getWorkspaceStorageKey = (challengeId) => `buggyman-workspace-${challengeId}`;

const readPersistedWorkspace = (challengeId, defaultFiles) => {
  if (!challengeId || !Array.isArray(defaultFiles) || defaultFiles.length === 0) {
    return { files: defaultFiles || [], activeFile: (defaultFiles && defaultFiles[0]) || null };
  }

  try {
    const raw = sessionStorage.getItem(getWorkspaceStorageKey(challengeId));
    if (!raw) return { files: defaultFiles, activeFile: defaultFiles[0] || null };

    const parsed = JSON.parse(raw);
    const persistedFiles = normalizeFiles(parsed.files || defaultFiles);
    const validFiles = (persistedFiles && persistedFiles.length > 0) ? persistedFiles : defaultFiles;
    const activeFile = validFiles.find((file) => file.name === parsed.activeFileName) || validFiles[0] || null;
    return { files: validFiles, activeFile };
  } catch (error) {
    return { files: defaultFiles, activeFile: defaultFiles[0] || null };
  }
};

export default function EditorPage({ user, setUser, addToast, theme, toggleTheme, settings }) {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [challenge, setChallenge] = useState(null);
  const [files, setFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [activeTab, setActiveTab] = useState('description');
  const [isRunning, setIsRunning] = useState(false);
  const [runOutput, setRunOutput] = useState('');
  const [compileError, setCompileError] = useState('');
  const [lastRunResult, setLastRunResult] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [showHintPanel, setShowHintPanel] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(() => {
    try {
      const saved = sessionStorage.getItem(`buggyman-timer-${id || '1'}`);
      return saved ? parseInt(saved, 10) : 0;
    } catch {
      return 0;
    }
  });
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  const filesRef = useRef([]);
  const activeFileRef = useRef(null);

  const currentId = parseInt(id || '1', 10);
  const prevId = Math.max(1, currentId - 1);
  const nextId = Math.min(120, currentId + 1);

  useEffect(() => {
    filesRef.current = files;
  }, [files]);

  useEffect(() => {
    activeFileRef.current = activeFile;
  }, [activeFile]);

  // Timer counting up in seconds with persistence
  useEffect(() => {
    const currentTimerId = id || '1';
    try {
      const saved = sessionStorage.getItem(`buggyman-timer-${currentTimerId}`);
      setTimeElapsed(saved ? parseInt(saved, 10) : 0);
    } catch {
      setTimeElapsed(0);
    }

    const timer = setInterval(() => {
      setTimeElapsed(prev => {
        const next = prev + 1;
        try {
          sessionStorage.setItem(`buggyman-timer-${currentTimerId}`, next.toString());
        } catch {}
        return next;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [id]);

  useEffect(() => {
    async function fetchChallenge() {
      setLoading(true);
      setErrorMessage('');
      setRunOutput('');
      setCompileError('');
      setLastRunResult(null);

      try {
        const data = await challengeService.getChallengeById(id || '1');
        const defaultFiles = normalizeFiles(data?.files || []);
        const persisted = readPersistedWorkspace(data?.id || id, defaultFiles);

        setChallenge(data);
        setFiles(persisted.files);
        filesRef.current = persisted.files;
        setActiveFile(persisted.activeFile);
        activeFileRef.current = persisted.activeFile;
        setActiveTab('description');

        // Load any stored submissions for this challenge
        try {
          const stored = localStorage.getItem(`buggyman-submissions-${data?.id || id}`);
          if (stored) {
            setSubmissions(JSON.parse(stored));
          } else {
            setSubmissions([]);
          }
        } catch (e) {}

      } catch (err) {
        setErrorMessage(err?.message || 'Unable to load this challenge right now.');
        if (addToast) addToast('Error loading challenge files.', 'error');
      } finally {
        setLoading(false);
      }
    }

    fetchChallenge();
  }, [id]);

  useEffect(() => {
    if (!challenge?.id || files.length === 0) return;

    const workspaceState = {
      files: files.map((file) => ({ ...file })),
      activeFileName: activeFile?.name || files[0]?.name || null
    };
    sessionStorage.setItem(getWorkspaceStorageKey(challenge.id), JSON.stringify(workspaceState));
  }, [challenge?.id, files, activeFile]);

  const handleSelectFile = (file) => {
    const currentActive = activeFileRef.current || activeFile;
    const updatedFiles = (filesRef.current || files).map((f) => (f.name === currentActive?.name ? { ...f, content: currentActive.content } : f));
    filesRef.current = updatedFiles;
    setFiles(updatedFiles);
    activeFileRef.current = file;
    setActiveFile(file);
  };

  const handleCodeChange = (val) => {
    const currentActive = activeFileRef.current || activeFile;
    if (currentActive) {
      const updatedActive = { ...currentActive, content: val };
      activeFileRef.current = updatedActive;
      setActiveFile(updatedActive);

      const updatedFiles = (filesRef.current || files).map((f) => (f.name === currentActive.name ? { ...f, content: val } : f));
      filesRef.current = updatedFiles;
      setFiles(updatedFiles);
    }
  };

  const handleResetProject = () => {
    if (window.confirm('Are you sure you want to reset the current challenge code back to default?')) {
      const defaultFiles = normalizeFiles(challenge?.files || []);
      filesRef.current = defaultFiles;
      setFiles(defaultFiles);
      activeFileRef.current = defaultFiles[0] || null;
      setActiveFile(defaultFiles[0] || null);
      setRunOutput('');
      setCompileError('');
      setLastRunResult(null);
      if (challenge?.id) {
        sessionStorage.removeItem(getWorkspaceStorageKey(challenge.id));
      }
      if (addToast) addToast('Workspace files reverted to default.', 'info');
    }
  };

  const handleRandomChallenge = () => {
    const randomId = Math.floor(Math.random() * 120) + 1;
    navigate(`/challenge/${randomId}`);
  };

  const handleRunCode = async () => {
    if (!challenge?.id) return;
    setIsRunning(true);
    setRunOutput('');
    setCompileError('');

    try {
      const currentActive = activeFileRef.current || activeFile;
      const currentFiles = filesRef.current && filesRef.current.length > 0 ? filesRef.current : files;

      const syncedFiles = currentFiles.map((f) =>
        f.name === currentActive?.name ? { ...f, content: currentActive.content } : f
      );
      filesRef.current = syncedFiles;
      setFiles(syncedFiles);
      const primaryFile = syncedFiles.find((f) => f.name === currentActive?.name) || currentActive || syncedFiles[0];

      const res = await challengeService.runChallenge(challenge.id, primaryFile?.content || '', syncedFiles);
      setLastRunResult({ ...res, isSubmit: false });

      const returnedCases = res?.testCases || res?.test_cases || [];
      if (returnedCases.length > 0) {
        setChallenge((prev) => (prev ? { ...prev, testCases: returnedCases } : prev));
      }

      let consoleLogs = res?.stdout || '';
      if (res?.aiSummary) {
        consoleLogs = `[EVALUATOR SUMMARY]\n${res.aiSummary}\n\n` + consoleLogs;
      }
      setRunOutput(consoleLogs || 'Execution completed successfully.');
      
      if (res?.stderr || res?.error) {
        setCompileError(res.stderr || res.error);
      }

      if (addToast) addToast(res?.success ? 'Run completed: all tests passed!' : 'Run finished with test/execution failures.', res?.success ? 'success' : 'warning');
    } catch (err) {
      setCompileError(err?.message || 'Execution error');
      if (addToast) addToast('Run failed to connect to evaluator.', 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!challenge?.id) {
      if (addToast) addToast('This challenge is not ready to submit yet.', 'error');
      return;
    }

    setIsRunning(true);
    try {
      const currentActive = activeFileRef.current || activeFile;
      const currentFiles = filesRef.current && filesRef.current.length > 0 ? filesRef.current : files;

      const syncedFiles = currentFiles.map((f) =>
        f.name === currentActive?.name ? { ...f, content: currentActive.content } : f
      );
      filesRef.current = syncedFiles;
      setFiles(syncedFiles);
      const primaryFile = syncedFiles.find((f) => f.name === currentActive?.name) || currentActive || syncedFiles[0];

      const res = await challengeService.submitChallenge(challenge.id, primaryFile?.content || '', syncedFiles);
      
      const newSubmission = {
        success: Boolean(res?.success),
        score: res?.score || 0,
        timeTaken: formatTime(timeElapsed),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        testsPassed: res?.testsPassed || res?.tests_passed || (res?.success ? 3 : 1),
        testsTotal: res?.testsTotal || res?.tests_total || 3
      };

      const updatedSubmissions = [newSubmission, ...submissions];
      setSubmissions(updatedSubmissions);
      try {
        localStorage.setItem(`buggyman-submissions-${challenge.id}`, JSON.stringify(updatedSubmissions.slice(0, 10)));
      } catch (e) {}

      const submissionState = {
        success: Boolean(res?.success),
        score: res?.score || 0,
        timeTaken: formatTime(timeElapsed),
        bugsFixed: res?.bugsFixed || (res?.success ? 1 : 0),
        remainingIssues: res?.remainingIssues || (res?.success ? 0 : 1),
        testCases: res?.testCases || res?.test_cases || [],
        aiSummary: res?.aiSummary || (res?.success ? 'All test cases passed successfully!' : 'Some test cases failed.'),
        stdout: res?.stdout || '',
        stderr: res?.stderr || '',
        challengeId: challenge.id
      };

      sessionStorage.setItem('buggyman-last-submission', JSON.stringify(submissionState));
      if (res?.success) {
        try {
          sessionStorage.removeItem(`buggyman-timer-${challenge.id}`);
        } catch {}
      }

      if (typeof setUser === 'function' && res?.success && !String(res?.aiSummary || '').toLowerCase().includes('already solved')) {
        setUser((prev) => {
          if (!prev) return prev;
          const currentScore = prev.totalScore ?? prev.total_score ?? 0;
          const currentSolved = prev.challengesSolved ?? prev.challenges_solved ?? 0;
          return {
            ...prev,
            totalScore: currentScore + (res?.score || 0),
            challengesSolved: currentSolved + 1
          };
        });
      }

      if (addToast) addToast(res?.success ? 'Challenge solved successfully!' : 'Some test cases failed.', res?.success ? 'success' : 'warning');
      
      navigate('/result', {
        state: submissionState
      });
    } catch (err) {
      if (addToast) addToast(err?.message || 'Failed to submit solution.', 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const remainingSecs = secs % 60;
    return `${mins}m ${remainingSecs < 10 ? '0' : ''}${remainingSecs}s`;
  };

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-950">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-950 px-6">
        <div className="max-w-md rounded-2xl border border-slate-800 bg-slate-900/90 p-8 text-center space-y-4">
          <h2 className="text-xl font-heading font-semibold text-slate-100">Unable to load challenge</h2>
          <p className="text-sm text-slate-400">{errorMessage}</p>
          <div className="flex justify-center gap-3">
            <button onClick={() => navigate('/challenges')} className="button-secondary px-4 py-2 text-xs">
              Back to challenges
            </button>
          </div>
        </div>
      </div>
    );
  }

  const techBadge = challenge?.technology || 'JavaScript';

  return (
    <div className="h-screen flex flex-col bg-slate-950 overflow-hidden font-sans select-none">
      {/* 1. TOP HEADER: Authentic LeetCode Navigation Bar */}
      <div className="h-12 bg-slate-900/95 border-b border-slate-800 flex items-center justify-between px-3 shrink-0 text-slate-200">
        {/* Left: Problem List & Prev/Next Chevrons */}
        <div className="flex items-center gap-2">
          {/* Logo */}
          <div 
            onClick={() => navigate('/challenges')}
            className="flex items-center gap-2 cursor-pointer pr-2 border-r border-slate-800 mr-1"
            title="BuggyMan Dashboard"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-sm">
              <span className="font-heading font-bold text-white text-xs">BM</span>
            </div>
          </div>

          {/* Problem List Button */}
          <button
            onClick={() => {
              if (challenge?.arenaKey === 'sql' || challenge?.arena === 'SQL Lab') {
                navigate('/sql-challenges');
              } else if (challenge?.arenaKey === 'frontend' || challenge?.arena === 'Frontend Studio') {
                navigate('/design-challenges');
              } else {
                navigate('/challenges');
              }
            }}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg transition-all"
            title="Return to Challenge List"
          >
            <Menu className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">Problem List</span>
          </button>

          {/* Prev Chevron */}
          <button
            onClick={() => navigate(`/challenge/${prevId}`)}
            disabled={currentId <= 1}
            className="p-1 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-30"
            title="Previous Problem"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {/* Next Chevron */}
          <button
            onClick={() => navigate(`/challenge/${nextId}`)}
            disabled={currentId >= 120}
            className="p-1 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-30"
            title="Next Problem"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          {/* Shuffle / Random Challenge */}
          <button
            onClick={handleRandomChallenge}
            className="p-1 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors"
            title="Pick Random Problem"
          >
            <Shuffle className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Center: LeetCode Run & Submit Buttons */}
        <div className="flex items-center gap-2">
          {/* Run Button */}
          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-slate-200 transition-all shadow-sm disabled:opacity-50"
            title="Run Code"
          >
            {isRunning ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-slate-200 text-slate-200" />
            )}
            <span>Run</span>
          </button>

          {/* Submit Button (LeetCode Green) */}
          <button
            onClick={handleSubmit}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-sm hover:shadow-glow-emerald disabled:opacity-50"
            title="Submit Solution"
          >
            {isRunning ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-white" />
            ) : (
              <Cloud className="w-3.5 h-3.5 text-white" />
            )}
            <span>Submit</span>
          </button>
        </div>

        {/* Right: Reset, Timer, Points, Theme & Profile */}
        <div className="flex items-center gap-2.5">
          {/* Ask AI Hint Toggle */}
          <button
            onClick={() => setShowHintPanel(!showHintPanel)}
            className={`hidden md:flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-lg border transition-all ${
              showHintPanel
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-glow-cyan'
                : 'bg-slate-950 text-slate-400 hover:text-slate-200 border-slate-800 hover:bg-slate-800'
            }`}
            title="Ask AI Assistant"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI Hint</span>
          </button>

          {/* Reset Workspace */}
          <button
            onClick={handleResetProject}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
            title="Reset code files to original state"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          {/* Timer */}
          <div className="flex items-center gap-1 px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-300">
            <TimerIcon className="w-3.5 h-3.5 text-slate-400" />
            <span>{formatTime(timeElapsed)}</span>
          </div>

          {/* XP / Score Badge */}
          <div className="hidden lg:flex items-center gap-1 px-2.5 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs font-semibold text-amber-300">
            <Coins className="w-3.5 h-3.5 text-amber-400" />
            <span>{challenge?.points || 100} XP</span>
          </div>

          {/* Theme Toggle */}
          <button 
            onClick={toggleTheme}
            className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-800 rounded-lg transition-colors"
            title="Toggle Theme"
          >
            {theme === 'dark' ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5" />}
          </button>

          {/* User Profile */}
          <button
            onClick={() => navigate('/profile')}
            className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200 hover:border-cyan-400 transition-colors"
            title={user?.display_name || user?.username || 'Profile'}
          >
            {user?.avatar ? (
              <img src={user.avatar} alt="Avatar" className="w-full h-full rounded-full object-cover" />
            ) : (
              <UserIcon className="w-3.5 h-3.5 text-slate-400" />
            )}
          </button>
        </div>
      </div>

      {/* 2. MAIN SPLIT WORKSPACE */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: LeetCode Style Problem Statement Panel */}
        <ProblemStatementPanel 
          challenge={challenge} 
          files={files} 
          activeFile={activeFile} 
          onSelectFile={handleSelectFile} 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          addToast={addToast}
          submissions={submissions}
        />

        {/* Right Side: Code Editor & Output Panel */}
        <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
          {/* Editor Header: LeetCode </> Code Tab & Language Selector */}
          <div className="h-9 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-3 select-none shrink-0">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 text-slate-100 shadow-sm">
                <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Code</span>
              </div>

              {/* Multi-file selector pills if multiple files */}
              {files.length > 1 && (
                <div className="flex items-center gap-1 pl-2 border-l border-slate-800">
                  {files.map(f => (
                    <button
                      key={f.name}
                      onClick={() => handleSelectFile(f)}
                      className={`px-2.5 py-0.5 text-xs font-mono rounded transition-all ${
                        f.name === activeFile?.name
                          ? 'bg-cyan-500/15 text-cyan-300 font-semibold border border-cyan-500/30'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                      }`}
                    >
                      {f.name}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Language indicator & status */}
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="font-mono text-[11px] bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-slate-300">
                {techBadge}
              </span>
              <span className="text-[11px] text-slate-500 hidden sm:inline">Auto</span>
            </div>
          </div>

          {/* Monaco Frame */}
          <div className="flex-1 min-h-[300px] relative flex flex-col w-full overflow-hidden">
            <CodeEditor 
              file={activeFile} 
              onChange={handleCodeChange}
              theme={theme}
            />
          </div>

          {/* LeetCode Style Bottom Output Panel */}
          <OutputPanel 
            challenge={challenge}
            testCases={challenge?.testCases || []} 
            runOutput={runOutput} 
            isRunning={isRunning} 
            compileError={compileError}
            files={files}
            technology={challenge?.technology}
            userCode={activeFile?.content || ''}
            lastRunResult={lastRunResult}
          />
        </div>

        {/* AI Helper Sidebar Drawer */}
        {showHintPanel && (
          <AIHintPanel 
            challenge={challenge} 
            userCode={activeFile?.content || ''}
            testResults={challenge?.testCases || []}
            addToast={addToast}
            user={user}
            setUser={setUser}
          />
        )}
      </div>
    </div>
  );
}
