import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Play, 
  Send, 
  RotateCcw, 
  Sparkles, 
  Timer as TimerIcon, 
  ArrowLeft,
  Sun,
  Moon
} from 'lucide-react';
import ProblemStatementPanel from './ProblemStatementPanel';
import CodeEditor from './CodeEditor';
import AIHintPanel from './AIHintPanel';
import OutputPanel from './OutputPanel';
import LoadingSpinner from '../../components/LoadingSpinner';
import { challengeService } from '../../services/challengeService';

const normalizeFiles = (rawFiles = []) => {
  if (!Array.isArray(rawFiles)) return [];

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
  if (!challengeId) return { files: defaultFiles, activeFile: defaultFiles[0] || null };

  try {
    const raw = sessionStorage.getItem(getWorkspaceStorageKey(challengeId));
    if (!raw) return { files: defaultFiles, activeFile: defaultFiles[0] || null };

    const parsed = JSON.parse(raw);
    const persistedFiles = normalizeFiles(parsed.files || defaultFiles);
    const activeFile = persistedFiles.find((file) => file.name === parsed.activeFileName) || persistedFiles[0] || null;
    return { files: persistedFiles, activeFile };
  } catch (error) {
    return { files: defaultFiles, activeFile: defaultFiles[0] || null };
  }
};

export default function EditorPage({ addToast, theme, toggleTheme, setUser }) {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [challenge, setChallenge] = useState(null);
  const [files, setFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [activeTab, setActiveTab] = useState('problem');
  const [isRunning, setIsRunning] = useState(false);
  const [runOutput, setRunOutput] = useState('');
  const [compileError, setCompileError] = useState('');
  const [showHintPanel, setShowHintPanel] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  // Timer counting up in seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    async function fetchChallenge() {
      setLoading(true);
      setErrorMessage('');
      setRunOutput('');
      setCompileError('');

      try {
        const data = await challengeService.getChallengeById(id || '1');
        const defaultFiles = normalizeFiles(data?.files || []);
        const persisted = readPersistedWorkspace(data?.id || id, defaultFiles);

        setChallenge(data);
        setFiles(persisted.files);
        setActiveFile(persisted.activeFile);
        setActiveTab('problem');
      } catch (err) {
        setErrorMessage(err?.message || 'Unable to load this challenge right now.');
        addToast('Error loading challenge files.', 'error');
      } finally {
        setLoading(false);
      }
    }

    fetchChallenge();
  }, [id, addToast]);

  useEffect(() => {
    if (!challenge?.id || files.length === 0) return;

    const workspaceState = {
      files: files.map((file) => ({ ...file })),
      activeFileName: activeFile?.name || files[0]?.name || null
    };
    sessionStorage.setItem(getWorkspaceStorageKey(challenge.id), JSON.stringify(workspaceState));
  }, [challenge?.id, files, activeFile]);

  const handleSelectFile = (file) => {
    setFiles((prev) => prev.map((f) => (f.name === activeFile?.name ? { ...f, content: activeFile.content } : f)));
    setActiveFile(file);
  };

  const handleCodeChange = (val) => {
    if (activeFile) {
      setActiveFile((prev) => ({ ...(prev || {}), content: val }));
      setFiles((prev) => prev.map((f) => (f.name === activeFile.name ? { ...f, content: val } : f)));
    }
  };

  const handleResetProject = () => {
    if (window.confirm('Are you sure you want to reset the current challenge code back to default?')) {
      const defaultFiles = normalizeFiles(challenge?.files || []);
      setFiles(defaultFiles);
      setActiveFile(defaultFiles[0] || null);
      setRunOutput('');
      setCompileError('');
      if (challenge?.id) {
        sessionStorage.removeItem(getWorkspaceStorageKey(challenge.id));
      }
      addToast('Workspace files reverted.', 'info');
    }
  };

  const handleRunCode = async () => {
    if (!challenge?.id) return;
    setIsRunning(true);
    setRunOutput('');
    setCompileError('');

    try {
      const primaryFile = files.find((f) => f.name === activeFile?.name) || activeFile || files[0];
      const res = await challengeService.runChallenge(challenge.id, primaryFile?.content || '', files);

      if (res.testCases) {
        setChallenge((prev) => ({ ...prev, testCases: res.testCases }));
      }

      let consoleLogs = res.stdout || '';
      if (res.aiSummary) {
        consoleLogs = `[EVALUATOR SUMMARY]\n${res.aiSummary}\n\n` + consoleLogs;
      }
      setRunOutput(consoleLogs || 'Execution completed.');
      
      if (res.stderr || res.error) {
        setCompileError(res.stderr || res.error);
      }

      addToast(res.success ? 'Run completed: all tests passed!' : 'Run finished with test/execution failures.', res.success ? 'success' : 'warning');
    } catch (err) {
      setCompileError(err?.message || 'Execution error');
      addToast('Run failed to connect to evaluator.', 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!challenge?.id) {
      addToast('This challenge is not ready to submit yet.', 'error');
      return;
    }

    setIsRunning(true);
    try {
      const primaryFile = files.find((f) => f.name === activeFile?.name) || activeFile || files[0];
      const res = await challengeService.submitChallenge(challenge.id, primaryFile?.content || '', files);
      
      const submissionState = {
        success: res.success,
        score: res.score,
        timeTaken: formatTime(timeElapsed),
        bugsFixed: res.bugsFixed,
        remainingIssues: res.remainingIssues,
        testCases: res.testCases,
        aiSummary: res.aiSummary,
        stdout: res.stdout,
        stderr: res.stderr,
        challengeId: challenge.id
      };

      sessionStorage.setItem('buggyman-last-submission', JSON.stringify(submissionState));

      if (typeof setUser === 'function' && res.success && !String(res.aiSummary || '').toLowerCase().includes('already solved')) {
        setUser((prev) => {
          if (!prev) return prev;
          const currentScore = prev.totalScore ?? prev.total_score ?? 0;
          const currentSolved = prev.challengesSolved ?? prev.challenges_solved ?? 0;
          return {
            ...prev,
            totalScore: currentScore + (res.score || 0),
            challengesSolved: currentSolved + 1
          };
        });
      }

      addToast(res.success ? 'Challenge solved successfully!' : 'Some test cases failed.', res.success ? 'success' : 'warning');
      
      navigate('/result', {
        state: submissionState
      });
    } catch (err) {
      addToast(err?.message || 'Failed to submit solution.', 'error');
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

  return (
    <div className="h-screen flex flex-col bg-slate-950 overflow-hidden">
      {/* Editor Top Bar */}
      <div className="h-14 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-4 select-none shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate('/challenges')}
            className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-4.5 h-4.5" />
          </button>
          <div>
            <h2 className="text-sm font-heading font-semibold text-slate-100">{challenge?.title}</h2>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{challenge?.technology} • {challenge?.difficulty}</p>
          </div>
        </div>

        {/* Timer */}
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs font-bold text-slate-300">
          <TimerIcon className="w-3.5 h-3.5 text-cyan-400" />
          <span>{formatTime(timeElapsed)}</span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2.5">
          <button 
            onClick={toggleTheme}
            className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          </button>

          <button
            onClick={handleResetProject}
            className="button-secondary px-3.5 py-2 text-xs"
            title="Reset code files to original state"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Workspace</span>
          </button>

          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="button-secondary px-3.5 py-2 text-xs border-cyan-500/30 text-cyan-400 bg-cyan-950/20 hover:bg-cyan-950/40 disabled:opacity-50"
          >
            {isRunning ? <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" /> : <Play className="w-3.5 h-3.5 fill-cyan-400" />}
            <span>{isRunning ? 'Running...' : 'Run Code'}</span>
          </button>

          <button
            onClick={handleSubmit}
            disabled={isRunning}
            className="button-primary px-4 py-2 text-xs disabled:opacity-50"
          >
            {isRunning ? <Loader2 className="w-3.5 h-3.5 animate-spin text-white" /> : <Send className="w-3.5 h-3.5" />}
            <span>{isRunning ? 'Evaluating...' : 'Submit Solution'}</span>
          </button>

          <button
            onClick={() => setShowHintPanel(!showHintPanel)}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl border transition-all ${
              showHintPanel 
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-glow-cyan'
                : 'bg-slate-950 hover:bg-slate-800 border-slate-800 text-slate-300'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Ask AI Hint</span>
          </button>
        </div>
      </div>

      {/* Editor central split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side Panel: Problem Statement & File Explorer */}
        <ProblemStatementPanel 
          challenge={challenge} 
          files={files} 
          activeFile={activeFile} 
          onSelectFile={handleSelectFile} 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          addToast={addToast}
        />

        {/* Core Editor & output panel container */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* File Tabs selector */}
          <div className="h-9 bg-slate-950/90 border-b border-slate-800/80 flex items-center px-2 select-none gap-1 overflow-x-auto">
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

          {/* Monaco Frame */}
          <div className="flex-1 min-h-0">
            <CodeEditor 
              file={activeFile} 
              onChange={handleCodeChange}
              theme={theme}
            />
          </div>

          {/* Terminal output tab panel */}
          <OutputPanel 
            testCases={challenge?.testCases || []} 
            runOutput={runOutput} 
            isRunning={isRunning} 
            compileError={compileError}
            files={files}
            technology={challenge?.technology}
          />
        </div>

        {/* AI helper sidebar */}
        {showHintPanel && (
          <AIHintPanel 
            challenge={challenge} 
            addToast={addToast}
          />
        )}
      </div>
    </div>
  );
}
