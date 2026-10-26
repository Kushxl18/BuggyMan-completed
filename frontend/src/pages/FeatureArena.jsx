import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { 
  ArrowLeft, 
  Play, 
  CheckCircle, 
  RotateCcw, 
  FolderTree, 
  FileCode, 
  FilePlus, 
  Trash2, 
  HelpCircle, 
  Sparkles, 
  Bot, 
  Terminal as TerminalIcon, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Send, 
  ChevronDown, 
  ChevronUp, 
  Lock, 
  Clock, 
  Trophy, 
  Zap, 
  X,
  FileText,
  ShieldCheck,
  CheckSquare,
  Square
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { challengeService } from '../services/challengeService';

export default function FeatureArena({ user, setUser, addToast, theme = 'dark', toggleTheme }) {
  const { id } = useParams();
  const navigate = useNavigate();

  // Challenge & Workspace State
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [files, setFiles] = useState([]);
  const [activeFileName, setActiveFileName] = useState('');
  const [openTabs, setOpenTabs] = useState([]);
  const [modifiedFiles, setModifiedFiles] = useState(new Set());

  // Execution & Evaluation State
  const [isExecuting, setIsExecuting] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [activeBottomTab, setActiveBottomTab] = useState('tests'); // 'tests', 'terminal', 'review'
  const [isBottomPanelOpen, setIsBottomPanelOpen] = useState(true);

  // Right Panel Tabs: 'spec', 'assistant', 'hints'
  const [activeRightTab, setActiveRightTab] = useState('spec');
  const [checkedCriteria, setCheckedCriteria] = useState({});

  // AI Assistant Chat State
  const [assistantPrompt, setAssistantPrompt] = useState('');
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [assistantMessages, setAssistantMessages] = useState([]);

  // Hints State
  const [unlockedHints, setUnlockedHints] = useState({});
  const [unlockingHintLevel, setUnlockingHintLevel] = useState(null);

  // New File Modal
  const [isNewFileModalOpen, setIsNewFileModalOpen] = useState(false);
  const [newFileName, setNewFileName] = useState('');

  // Results Modal on Submit
  const [showResultModal, setShowResultModal] = useState(false);

  // Load Challenge
  useEffect(() => {
    async function loadWorkspace() {
      try {
        setLoading(true);
        const data = await challengeService.getFeatureChallengeById(id);
        if (!data || !data.id) {
          throw new Error('Feature challenge not found');
        }
        setChallenge(data);

        // Normalize initial files
        const initial = (data.files || []).map(f => ({
          name: f.name || 'file.txt',
          content: f.content || '',
          readonly: Boolean(f.readonly),
          is_entrypoint: Boolean(f.is_entrypoint)
        }));

        setFiles(initial);

        // Determine default active file (entrypoint or first file)
        const entry = initial.find(f => f.is_entrypoint) || initial[0];
        if (entry) {
          setActiveFileName(entry.name);
          setOpenTabs([entry.name]);
        }

        // Initialize assistant welcome message
        setAssistantMessages([
          {
            sender: 'ai',
            text: `Hello! I am your AI Codebase Assistant for **${data.title}**. You can ask me about file architecture, how to structure the implementation, or clarifying acceptance criteria.`
          }
        ]);
      } catch (err) {
        if (addToast) addToast(err.message || 'Failed to load challenge workspace', 'error');
        navigate('/feature-challenges');
      } finally {
        setLoading(false);
      }
    }
    loadWorkspace();
  }, [id, navigate, addToast]);

  const activeFile = files.find(f => f.name === activeFileName) || files[0];

  // Helper: Detect language for Monaco editor
  const getLanguage = (fileName = '') => {
    const ext = fileName.split('.').pop().toLowerCase();
    switch (ext) {
      case 'py': return 'python';
      case 'js': return 'javascript';
      case 'jsx': return 'javascript';
      case 'ts': return 'typescript';
      case 'tsx': return 'typescript';
      case 'json': return 'json';
      case 'css': return 'css';
      case 'html': return 'html';
      case 'sql': return 'sql';
      case 'md': return 'markdown';
      default: return 'plaintext';
    }
  };

  // Switch Active File
  const handleSelectFile = (fileName) => {
    setActiveFileName(fileName);
    if (!openTabs.includes(fileName)) {
      setOpenTabs(prev => [...prev, fileName]);
    }
  };

  // Close Tab
  const handleCloseTab = (e, tabName) => {
    e.stopPropagation();
    const remaining = openTabs.filter(t => t !== tabName);
    setOpenTabs(remaining);
    if (activeFileName === tabName) {
      setActiveFileName(remaining[remaining.length - 1] || '');
    }
  };

  // Update Code Content
  const handleCodeChange = (newContent) => {
    if (!activeFile || activeFile.readonly) return;
    setFiles(prev => prev.map(f => {
      if (f.name === activeFileName) {
        return { ...f, content: newContent };
      }
      return f;
    }));
    setModifiedFiles(prev => new Set(prev).add(activeFileName));
  };

  // Create New File
  const handleCreateFile = (e) => {
    e.preventDefault();
    const trimmed = newFileName.trim().replace(/\\/g, '/').replace(/^\/+/, '');
    if (!trimmed) return;

    if (files.some(f => f.name.toLowerCase() === trimmed.toLowerCase())) {
      if (addToast) addToast('A file with this path already exists.', 'warning');
      return;
    }

    const newFileObj = {
      name: trimmed,
      content: '',
      readonly: false,
      is_entrypoint: false
    };

    setFiles(prev => [...prev, newFileObj]);
    setModifiedFiles(prev => new Set(prev).add(trimmed));
    setActiveFileName(trimmed);
    setOpenTabs(prev => [...prev, trimmed]);
    setNewFileName('');
    setIsNewFileModalOpen(false);
    if (addToast) addToast(`Created ${trimmed}`, 'success');
  };

  // Delete User-Created File
  const handleDeleteFile = (e, fileName) => {
    e.stopPropagation();
    const target = files.find(f => f.name === fileName);
    if (!target || target.readonly) {
      if (addToast) addToast('Protected template files cannot be deleted.', 'warning');
      return;
    }

    if (!window.confirm(`Delete "${fileName}"? This cannot be undone.`)) return;

    setFiles(prev => prev.filter(f => f.name !== fileName));
    setOpenTabs(prev => prev.filter(t => t !== fileName));
    setModifiedFiles(prev => {
      const next = new Set(prev);
      next.delete(fileName);
      return next;
    });

    if (activeFileName === fileName) {
      const remaining = files.filter(f => f.name !== fileName);
      setActiveFileName(remaining[0]?.name || '');
    }
    if (addToast) addToast(`Deleted ${fileName}`, 'info');
  };

  // Reset Files to Original State
  const handleResetWorkspace = () => {
    if (!window.confirm('Reset all files back to the initial challenge state? Any unsaved edits will be lost.')) return;
    if (challenge && challenge.files) {
      const resetList = challenge.files.map(f => ({
        name: f.name,
        content: f.content,
        readonly: Boolean(f.readonly),
        is_entrypoint: Boolean(f.is_entrypoint)
      }));
      setFiles(resetList);
      setModifiedFiles(new Set());
      const entry = resetList.find(f => f.is_entrypoint) || resetList[0];
      if (entry) {
        setActiveFileName(entry.name);
        setOpenTabs([entry.name]);
      }
      if (addToast) addToast('Workspace reset to initial state.', 'info');
    }
  };

  // Run Tests (Visible Test Suite)
  const handleRunTests = async () => {
    try {
      setIsExecuting(true);
      setIsBottomPanelOpen(true);
      setActiveBottomTab('tests');
      const res = await challengeService.runFeatureChallenge(id, files);
      setEvalResult(res);
      if (addToast) {
        if (res.success) {
          addToast('Feature assertions passed!', 'success');
        } else {
          addToast('Some assertions failed. Check details below.', 'warning');
        }
      }
    } catch (err) {
      if (addToast) addToast(err.message || 'Execution error', 'error');
    } finally {
      setIsExecuting(false);
    }
  };

  // Submit Completed Feature
  const handleSubmitFeature = async () => {
    try {
      setIsSubmitting(true);
      setIsBottomPanelOpen(true);
      setActiveBottomTab('tests');
      const res = await challengeService.submitFeatureChallenge(id, files);
      setEvalResult(res);
      setShowResultModal(true);

      if (res.xpAwarded > 0 && setUser && user) {
        setUser(prev => ({
          ...prev,
          totalScore: (prev.totalScore || 0) + res.xpAwarded,
          challengesSolved: (prev.challengesSolved || 0) + 1,
          bugbytesBalance: (prev.bugbytesBalance || 0) + res.bugbytesAwarded
        }));
      }

      if (addToast) {
        if (res.success) {
          addToast(`Feature Shipped! +${res.xpAwarded} XP, +${res.bugbytesAwarded} BB`, 'success');
        } else {
          addToast('Submission completed with errors. Review breakdown below.', 'warning');
        }
      }
    } catch (err) {
      if (addToast) addToast(err.message || 'Submission error', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Unlock Progressive Hint
  const handleUnlockHint = async (level) => {
    try {
      setUnlockingHintLevel(level);
      const res = await challengeService.unlockFeatureHint(id, level);
      setUnlockedHints(prev => ({ ...prev, [level]: res.hint }));
      if (setUser && res.remainingBugBytes !== undefined) {
        setUser(prev => ({ ...prev, bugbytesBalance: res.remainingBugBytes }));
      }
      if (addToast) addToast(res.message || 'Hint unlocked!', 'success');
    } catch (err) {
      if (addToast) addToast(err.message || 'Failed to unlock hint', 'error');
    } finally {
      setUnlockingHintLevel(null);
    }
  };

  // Send AI Codebase Assistant Query
  const handleSendAssistant = async (e) => {
    if (e) e.preventDefault();
    const prompt = assistantPrompt.trim();
    if (!prompt || assistantLoading) return;

    setAssistantMessages(prev => [...prev, { sender: 'user', text: prompt }]);
    setAssistantPrompt('');
    setAssistantLoading(true);

    try {
      const res = await challengeService.askCodebaseAssistant(id, prompt, files);
      setAssistantMessages(prev => [...prev, { sender: 'ai', text: res.reply }]);
    } catch (err) {
      setAssistantMessages(prev => [...prev, { 
        sender: 'ai', 
        text: 'Sorry, I encountered an issue retrieving context. Please try asking again.' 
      }]);
    } finally {
      setAssistantLoading(false);
    }
  };

  // Criteria toggle
  const toggleCriteria = (index) => {
    setCheckedCriteria(prev => ({ ...prev, [index]: !prev[index] }));
  };

  if (loading || !challenge) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-950">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const breakdown = evalResult?.scoreBreakdown || evalResult?.score_breakdown || {};

  return (
    <div className="h-screen flex flex-col bg-slate-50 dark:bg-[#0D1117] text-slate-900 dark:text-slate-100 overflow-hidden font-sans select-none">
      {/* 1. TOP WORKSPACE NAVIGATION BAR */}
      <header className="h-12 border-b border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] flex items-center justify-between px-3 shrink-0 z-30">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            to="/feature-challenges"
            className="flex items-center gap-1.5 px-2 py-1 rounded text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Back to Feature Challenges"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Back</span>
          </Link>

          <div className="w-px h-5 bg-slate-200 dark:bg-[#30363D]" />

          {/* Title & Badges */}
          <div className="flex items-center gap-2 min-w-0 truncate">
            <h1 className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
              {challenge.title}
            </h1>
            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono uppercase font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 shrink-0">
              {challenge.difficulty}
            </span>
            <span className="hidden md:inline-block px-1.5 py-0.2 rounded text-[10px] font-mono text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 shrink-0">
              {challenge.technology}
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleResetWorkspace}
            className="p-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
            title="Reset Workspace to Initial State"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={handleRunTests}
            disabled={isExecuting || isSubmitting}
            className="button-secondary text-xs flex items-center gap-1.5 py-1 px-3 disabled:opacity-50"
            title="Run visible feature tests"
          >
            <Play className={`w-3.5 h-3.5 text-blue-400 ${isExecuting ? 'animate-spin' : ''}`} />
            <span>{isExecuting ? 'Running...' : 'Run Tests'}</span>
          </button>

          <button
            onClick={handleSubmitFeature}
            disabled={isExecuting || isSubmitting}
            className="button-primary text-xs flex items-center gap-1.5 py-1 px-3 disabled:opacity-50"
            title="Submit feature for full evaluation"
          >
            <CheckCircle className={`w-3.5 h-3.5 ${isSubmitting ? 'animate-spin' : ''}`} />
            <span>{isSubmitting ? 'Evaluating...' : 'Submit Feature'}</span>
          </button>
        </div>
      </header>

      {/* 2. THREE-PANEL CORE WORKSPACE (Explorer | Editor | Spec/Assistant) */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* LEFT PANEL: Project File Explorer */}
        <aside className="w-56 border-r border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] flex flex-col shrink-0">
          <div className="p-2.5 border-b border-slate-200 dark:border-[#30363D] flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800 dark:text-slate-300">
              <FolderTree className="w-3.5 h-3.5 text-blue-400" />
              <span>Project Repository</span>
            </div>
            <button
              onClick={() => setIsNewFileModalOpen(true)}
              className="p-1 rounded text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Create New File"
            >
              <FilePlus className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* File Tree List */}
          <div className="flex-1 overflow-y-auto p-1.5 space-y-0.5 text-xs">
            {files.map((file) => {
              const isActive = file.name === activeFileName;
              const isModified = modifiedFiles.has(file.name);

              return (
                <div
                  key={file.name}
                  onClick={() => handleSelectFile(file.name)}
                  className={`flex items-center justify-between px-2 py-1.5 rounded cursor-pointer group transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-slate-800 text-blue-600 dark:text-blue-400 font-medium'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0 truncate">
                    <FileCode className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                    <span className="truncate">{file.name}</span>
                    {isModified && (
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" title="Modified" />
                    )}
                  </div>

                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {file.readonly ? (
                      <Lock className="w-3 h-3 text-slate-500" title="Read-only file" />
                    ) : (
                      <button
                        onClick={(e) => handleDeleteFile(e, file.name)}
                        className="text-slate-500 hover:text-rose-400 p-0.5"
                        title="Delete file"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Explorer Footer */}
          <div className="p-2 border-t border-slate-200 dark:border-[#30363D] text-[10px] text-slate-500 flex items-center justify-between font-mono">
            <span>{files.length} files</span>
            <span>{modifiedFiles.size} modified</span>
          </div>
        </aside>

        {/* CENTER PANEL: Monaco Code Editor with Multi-Tabs */}
        <main className="flex-1 flex flex-col min-w-0 bg-white dark:bg-[#0D1117] border-r border-slate-200 dark:border-[#30363D]">
          {/* Open Tabs Bar */}
          <div className="h-9 border-b border-slate-200 dark:border-[#30363D] bg-slate-50 dark:bg-[#161B22] flex items-center overflow-x-auto px-1 shrink-0">
            {openTabs.map((tabName) => {
              const isActive = tabName === activeFileName;
              const isModified = modifiedFiles.has(tabName);

              return (
                <div
                  key={tabName}
                  onClick={() => setActiveFileName(tabName)}
                  className={`h-full flex items-center gap-2 px-3 text-xs cursor-pointer border-r border-slate-200 dark:border-[#30363D] transition-colors shrink-0 ${
                    isActive
                      ? 'bg-white dark:bg-[#0D1117] text-blue-600 dark:text-blue-400 border-t-2 border-t-blue-500 font-medium'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/40'
                  }`}
                >
                  <span>{tabName.split('/').pop()}</span>
                  {isModified && <span className="text-amber-400 text-xs leading-none">*</span>}
                  <button
                    onClick={(e) => handleCloseTab(e, tabName)}
                    className="p-0.5 hover:text-rose-400 text-slate-500 rounded"
                    title="Close Tab"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              );
            })}
          </div>

          {/* Monaco Editor Canvas */}
          <div className="flex-1 relative">
            {activeFile ? (
              <Editor
                height="100%"
                theme={theme === 'dark' ? 'vs-dark' : 'vs'}
                language={getLanguage(activeFile.name)}
                value={activeFile.content}
                onChange={handleCodeChange}
                options={{
                  fontSize: 13,
                  fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace',
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  tabSize: 2,
                  readOnly: Boolean(activeFile.readonly),
                  automaticLayout: true,
                  lineNumbers: 'on',
                  cursorBlinking: 'smooth'
                }}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-500">
                Select a file from the explorer to begin editing.
              </div>
            )}
          </div>

          {/* BOTTOM PANEL: Collapsible Output & Test Execution Drawer */}
          <div className={`border-t border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] transition-all flex flex-col ${
            isBottomPanelOpen ? 'h-64' : 'h-8'
          }`}>
            {/* Drawer Tabs Bar */}
            <div className="h-8 border-b border-slate-200 dark:border-[#30363D] bg-slate-50 dark:bg-[#161B22] flex items-center justify-between px-3 shrink-0">
              <div className="flex items-center gap-2 text-xs">
                <button
                  onClick={() => { setActiveBottomTab('tests'); setIsBottomPanelOpen(true); }}
                  className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                    activeBottomTab === 'tests' && isBottomPanelOpen
                      ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Test Results</span>
                  {evalResult && (
                    <span className="text-[10px] px-1.5 rounded-full bg-slate-700 text-slate-200 font-mono">
                      {evalResult.score}/100
                    </span>
                  )}
                </button>

                <button
                  onClick={() => { setActiveBottomTab('terminal'); setIsBottomPanelOpen(true); }}
                  className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                    activeBottomTab === 'terminal' && isBottomPanelOpen
                      ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <TerminalIcon className="w-3.5 h-3.5" />
                  <span>Terminal Logs</span>
                </button>

                <button
                  onClick={() => { setActiveBottomTab('review'); setIsBottomPanelOpen(true); }}
                  className={`px-2.5 py-1 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                    activeBottomTab === 'review' && isBottomPanelOpen
                      ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span>Architecture Review</span>
                </button>
              </div>

              <button
                onClick={() => setIsBottomPanelOpen(prev => !prev)}
                className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 p-1"
                title={isBottomPanelOpen ? "Minimize Panel" : "Expand Panel"}
              >
                {isBottomPanelOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Drawer Content */}
            {isBottomPanelOpen && (
              <div className="flex-1 p-3 overflow-y-auto font-mono text-xs text-slate-800 dark:text-slate-300">
                {activeBottomTab === 'tests' && (
                  <div className="space-y-3 font-sans">
                    {!evalResult ? (
                      <p className="text-slate-500 font-mono text-xs">
                        No test results yet. Click "Run Tests" or "Submit Feature" to evaluate your implementation.
                      </p>
                    ) : (
                      <>
                        {/* Score Breakdown Pills */}
                        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 font-mono text-xs">
                          <div className="p-2 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                            <span className="text-[10px] text-slate-500 block">FEATURE (40%)</span>
                            <span className="font-bold text-slate-900 dark:text-slate-100">{breakdown.feature_score ?? 0}/{breakdown.feature_max ?? 40}</span>
                          </div>
                          <div className="p-2 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                            <span className="text-[10px] text-slate-500 block">HIDDEN (25%)</span>
                            <span className="font-bold text-slate-900 dark:text-slate-100">{breakdown.hidden_score ?? 0}/{breakdown.hidden_max ?? 25}</span>
                          </div>
                          <div className="p-2 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                            <span className="text-[10px] text-slate-500 block">REGRESSION (15%)</span>
                            <span className="font-bold text-slate-900 dark:text-slate-100">{breakdown.regression_score ?? 0}/{breakdown.regression_max ?? 15}</span>
                          </div>
                          <div className="p-2 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                            <span className="text-[10px] text-slate-500 block">QUALITY (10%)</span>
                            <span className="font-bold text-slate-900 dark:text-slate-100">{breakdown.quality_score ?? 0}/{breakdown.quality_max ?? 10}</span>
                          </div>
                          <div className="p-2 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800">
                            <span className="text-[10px] text-slate-500 block">SECURITY (10%)</span>
                            <span className="font-bold text-slate-900 dark:text-slate-100">{breakdown.security_score ?? 0}/{breakdown.security_max ?? 10}</span>
                          </div>
                        </div>

                        {/* Test Cases List */}
                        <div className="space-y-1.5 pt-2">
                          {(evalResult.testResults || evalResult.test_results || []).map((t, idx) => (
                            <div 
                              key={idx}
                              className={`p-2 rounded border flex items-center justify-between text-xs font-mono ${
                                t.passed
                                  ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-300'
                                  : 'bg-rose-500/5 border-rose-500/20 text-rose-300'
                              }`}
                            >
                              <div className="flex items-center gap-2">
                                {t.passed ? (
                                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                                ) : (
                                  <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                                )}
                                <span className="font-medium">{t.name}</span>
                                <span className="text-[10px] text-slate-500 uppercase px-1 rounded bg-slate-800/80">
                                  {t.category}
                                </span>
                              </div>
                              <span className="text-[11px] text-slate-400 truncate max-w-sm">
                                {t.message}
                              </span>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                )}

                {activeBottomTab === 'terminal' && (
                  <pre className="whitespace-pre-wrap leading-relaxed text-slate-300">
                    {evalResult?.stdout || evalResult?.stderr || 'Execution output and console logs will stream here.'}
                  </pre>
                )}

                {activeBottomTab === 'review' && (
                  <div className="space-y-2 font-sans text-xs leading-relaxed text-slate-300">
                    <p className="font-medium text-slate-200">
                      {evalResult?.aiReview || evalResult?.ai_review || 'Submit your implementation to generate an automated architecture code review.'}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </main>

        {/* RIGHT PANEL: Feature Spec | AI Assistant | Progressive Hints */}
        <aside className="w-80 lg:w-96 border-l border-slate-200 dark:border-[#30363D] bg-white dark:bg-[#161B22] flex flex-col shrink-0">
          {/* Tab Navigation */}
          <div className="h-9 border-b border-slate-200 dark:border-[#30363D] bg-slate-50 dark:bg-[#161B22] flex items-center px-2 gap-1 shrink-0 text-xs font-medium">
            <button
              onClick={() => setActiveRightTab('spec')}
              className={`flex-1 py-1.5 text-center rounded transition-colors ${
                activeRightTab === 'spec'
                  ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 font-semibold shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              Specification
            </button>
            <button
              onClick={() => setActiveRightTab('assistant')}
              className={`flex-1 py-1.5 text-center rounded transition-colors flex items-center justify-center gap-1 ${
                activeRightTab === 'assistant'
                  ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 font-semibold shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Assistant</span>
            </button>
            <button
              onClick={() => setActiveRightTab('hints')}
              className={`flex-1 py-1.5 text-center rounded transition-colors flex items-center justify-center gap-1 ${
                activeRightTab === 'hints'
                  ? 'bg-white dark:bg-slate-800 text-blue-600 dark:text-blue-400 font-semibold shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Hints</span>
            </button>
          </div>

          {/* TAB 1: Specification & Acceptance Checklist */}
          {activeRightTab === 'spec' && (
            <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
              <div>
                <h2 className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-1.5">
                  Feature Description
                </h2>
                <p className="text-slate-700 dark:text-slate-300 leading-normal">{challenge.description}</p>
              </div>

              {/* Functional Requirements */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Requirements
                </h3>
                <div className="space-y-2">
                  {(challenge.requirements || []).map((req) => (
                    <div key={req.id} className="p-2.5 rounded bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80">
                      <span className="font-semibold text-slate-800 dark:text-slate-200 block mb-0.5">{req.title}</span>
                      <span className="text-slate-600 dark:text-slate-400 text-[11px] leading-normal">{req.description}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Interactive Acceptance Criteria */}
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Acceptance Criteria
                </h3>
                <div className="space-y-1.5">
                  {(challenge.acceptanceCriteria || challenge.acceptance_criteria || []).map((crit, idx) => {
                    const isChecked = checkedCriteria[idx];

                    return (
                      <div
                        key={idx}
                        onClick={() => toggleCriteria(idx)}
                        className={`flex items-start gap-2 p-2 rounded cursor-pointer border transition-colors ${
                          isChecked
                            ? 'bg-emerald-500/5 border-emerald-500/20 text-emerald-300'
                            : 'bg-slate-50 dark:bg-slate-900/40 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                        }`}
                      >
                        {isChecked ? (
                          <CheckSquare className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <Square className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
                        )}
                        <span className={`text-[11px] leading-normal ${isChecked ? 'line-through opacity-80' : ''}`}>
                          {crit}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: AI Codebase Assistant */}
          {activeRightTab === 'assistant' && (
            <div className="flex-1 flex flex-col min-h-0 bg-white dark:bg-[#161B22]">
              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3 text-xs leading-relaxed">
                {assistantMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`p-2.5 rounded-md ${
                      msg.sender === 'user'
                        ? 'bg-blue-600/20 text-blue-200 ml-4 border border-blue-500/30'
                        : 'bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-300 mr-2 border border-slate-200 dark:border-slate-800'
                    }`}
                  >
                    <span className="text-[10px] font-bold block mb-1 text-slate-400 font-mono">
                      {msg.sender === 'user' ? 'YOU' : 'AI CODEBASE ASSISTANT'}
                    </span>
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  </div>
                ))}
                {assistantLoading && (
                  <div className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs text-slate-400">
                    <LoadingSpinner size="sm" />
                    <span>Analyzing repository files...</span>
                  </div>
                )}
              </div>

              {/* Quick Prompts */}
              <div className="px-3 py-1.5 border-t border-slate-200 dark:border-[#30363D] flex items-center gap-1.5 overflow-x-auto text-[10px]">
                <button
                  onClick={() => { setAssistantPrompt("Where should I start in this codebase?"); }}
                  className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-transparent shrink-0"
                >
                  Where to start?
                </button>
                <button
                  onClick={() => { setAssistantPrompt("How do I structure the test assertions?"); }}
                  className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-transparent shrink-0"
                >
                  Test advice
                </button>
                <button
                  onClick={() => { setAssistantPrompt("Explain the acceptance criteria in simple terms."); }}
                  className="px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-transparent shrink-0"
                >
                  Explain criteria
                </button>
              </div>

              {/* Input Form */}
              <form onSubmit={handleSendAssistant} className="p-2 border-t border-slate-200 dark:border-[#30363D] flex items-center gap-2">
                <input
                  type="text"
                  value={assistantPrompt}
                  onChange={(e) => setAssistantPrompt(e.target.value)}
                  placeholder="Ask about repo structure..."
                  disabled={assistantLoading}
                  className="flex-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={assistantLoading || !assistantPrompt.trim()}
                  className="button-primary p-1.5 disabled:opacity-50"
                  title="Send message"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          )}

          {/* TAB 3: Progressive Hints */}
          {activeRightTab === 'hints' && (
            <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
              <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                Unlock tiered progressive guidance without giving away the complete solution. Hints cost BugBytes.
              </div>

              <div className="space-y-3">
                {[
                  { level: 1, cost: 5, title: 'Level 1: Architectural Nudge' },
                  { level: 2, cost: 10, title: 'Level 2: Implementation Guidance' },
                  { level: 3, cost: 15, title: 'Level 3: Algorithm & Pseudo-code' }
                ].map((tier) => {
                  const unlocked = unlockedHints[tier.level];
                  const isUnlocking = unlockingHintLevel === tier.level;

                  return (
                    <div key={tier.level} className="p-3 rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-800 dark:text-slate-200">{tier.title}</span>
                        <span className="text-[10px] font-mono text-amber-400">-{tier.cost} BB</span>
                      </div>

                      {unlocked ? (
                        <p className="text-slate-700 dark:text-slate-800 dark:text-slate-300 leading-normal text-[11px] p-2 rounded bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                          {unlocked.content}
                        </p>
                      ) : (
                        <button
                          onClick={() => handleUnlockHint(tier.level)}
                          disabled={isUnlocking}
                          className="button-secondary text-xs w-full py-1.5 flex items-center justify-center gap-1.5"
                        >
                          <Lock className="w-3 h-3 text-amber-400" />
                          <span>{isUnlocking ? 'Unlocking...' : `Unlock for ${tier.cost} BugBytes`}</span>
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </aside>
      </div>

      {/* 3. MODAL: CREATE NEW FILE */}
      {isNewFileModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-white dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] rounded-md p-5 max-w-sm w-full space-y-4">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <FilePlus className="w-4 h-4 text-blue-400" />
              <span>Create New File</span>
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Enter relative file path (e.g. <code className="text-slate-300">src/utils/helpers.py</code>):
            </p>
            <form onSubmit={handleCreateFile} className="space-y-4">
              <input
                type="text"
                autoFocus
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                placeholder="app/services/cache.py"
                className="w-full px-3 py-1.5 text-xs rounded border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:border-blue-500 font-mono"
              />
              <div className="flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsNewFileModalOpen(false)}
                  className="button-secondary text-xs py-1 px-3"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!newFileName.trim()}
                  className="button-primary text-xs py-1 px-3 disabled:opacity-50"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 4. MODAL: SUBMISSION RESULTS OVERVIEW */}
      {showResultModal && evalResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 animate-fade-in">
          <div className="bg-white dark:bg-[#161B22] border border-slate-200 dark:border-[#30363D] rounded-md p-6 max-w-lg w-full space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {evalResult.success ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-amber-400" />
                )}
                <div>
                  <h3 className="text-base font-semibold text-slate-900 dark:text-slate-100">
                    {evalResult.success ? 'Feature Shipped Successfully!' : 'Feature Evaluation Incomplete'}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    {evalResult.success ? 'All requirements & regression checks passed.' : 'Some criteria or test cases require adjustments.'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowResultModal(false)}
                className="text-slate-500 hover:text-slate-300 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Score & Rewards Banner */}
            <div className="grid grid-cols-3 gap-3 p-3 rounded bg-slate-900/60 border border-slate-800 text-center font-mono">
              <div>
                <span className="text-[10px] text-slate-500 block">TOTAL SCORE</span>
                <span className="text-xl font-bold text-slate-900 dark:text-slate-100">{evalResult.score}/100</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">XP REWARD</span>
                <span className="text-xl font-bold text-blue-400">+{evalResult.xpAwarded || 0}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">BUGBYTES</span>
                <span className="text-xl font-bold text-amber-400">+{evalResult.bugbytesAwarded || 0}</span>
              </div>
            </div>

            {/* Breakdown Bars */}
            <div className="space-y-2 text-xs font-mono">
              <span className="text-slate-400 text-[11px] font-sans font-semibold">Evaluation Breakdown:</span>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200">
                  Feature: {breakdown.feature_score ?? 0}/{breakdown.feature_max ?? 40}
                </div>
                <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200">
                  Hidden Tests: {breakdown.hidden_score ?? 0}/{breakdown.hidden_max ?? 25}
                </div>
                <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200">
                  Regression: {breakdown.regression_score ?? 0}/{breakdown.regression_max ?? 15}
                </div>
                <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200">
                  Quality & Lint: {breakdown.quality_score ?? 0}/{breakdown.quality_max ?? 10}
                </div>
                <div className="p-2 rounded bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 col-span-2">
                  Security & Edge Cases: {breakdown.security_score ?? 0}/{breakdown.security_max ?? 10}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200 dark:border-slate-800">
              <button
                onClick={() => setShowResultModal(false)}
                className="button-secondary text-xs py-1.5 px-4"
              >
                Continue Editing
              </button>
              <button
                onClick={() => navigate('/feature-challenges')}
                className="button-primary text-xs py-1.5 px-4"
              >
                Back to Catalog
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
