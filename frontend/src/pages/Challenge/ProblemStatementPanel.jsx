import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  BookOpen, 
  Lightbulb, 
  FlaskConical, 
  History, 
  FolderOpen,
  CheckCircle2, 
  XCircle,
  Tag, 
  Briefcase, 
  ThumbsUp, 
  ThumbsDown, 
  Star, 
  Share2, 
  Flag, 
  ChevronDown,
  Sparkles,
  Send,
  X,
  Code2,
  Lock,
  Eye,
  AlertTriangle,
  Loader2,
  Clock
} from 'lucide-react';
import { challengeService } from '../../services/challengeService';
import ProblemStatementFormatter from '../../components/ProblemStatementFormatter';
import TestCasesSection from '../../components/TestCasesSection';

export default function ProblemStatementPanel({ 
  challenge, 
  files = [], 
  activeFile, 
  onSelectFile, 
  activeTab = 'description', 
  setActiveTab,
  addToast,
  submissions = []
}) {
  const [currentTab, setCurrentTab] = useState(activeTab || 'description');
  const [showTopics, setShowTopics] = useState(false);
  const [showCompanies, setShowCompanies] = useState(false);
  
  // Real Engagement State (backed by PostgreSQL)
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [isStarred, setIsStarred] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [dislikeCount, setDislikeCount] = useState(0);
  const [isReacting, setIsReacting] = useState(false);

  // Submissions State
  const [realSubmissions, setRealSubmissions] = useState([]);
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);

  // Solutions Tab State
  const [solutionData, setSolutionData] = useState(null);
  const [solutionRevealed, setSolutionRevealed] = useState(false);
  const [loadingSolution, setLoadingSolution] = useState(false);

  // Report Modal State
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportType, setReportType] = useState('broken_challenge');
  const [reportDescription, setReportDescription] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  // Progressive Hints (Level 1 unlocked by default, 2 and 3 unlocked on click)
  const [unlockedHints, setUnlockedHints] = useState([1]);

  useEffect(() => {
    if (activeTab) setCurrentTab(activeTab);
  }, [activeTab]);

  // Load actual persistent engagement on challenge mount
  useEffect(() => {
    if (!challenge?.id) return;
    setSolutionRevealed(false);
    setSolutionData(null);
    setUnlockedHints([1]);

    challengeService.getEngagement(challenge.id)
      .then(res => {
        setLikeCount(res?.likes || 0);
        setDislikeCount(res?.dislikes || 0);
        setIsLiked(res?.userReaction === 'like');
        setIsDisliked(res?.userReaction === 'dislike');
        setIsStarred(Boolean(res?.isStarred));
      })
      .catch(() => {
        // Fallback to neutral if unauthenticated
        setLikeCount(0);
        setDislikeCount(0);
      });
  }, [challenge?.id]);

  // Load real submission history when submissions tab is activated
  useEffect(() => {
    if (!challenge?.id || currentTab !== 'submissions') return;
    setLoadingSubmissions(true);
    challengeService.getSubmissions(challenge.id)
      .then(res => {
        setRealSubmissions(res?.submissions || []);
      })
      .catch(() => {
        setRealSubmissions(submissions || []);
      })
      .finally(() => {
        setLoadingSubmissions(false);
      });
  }, [challenge?.id, currentTab]);

  const handleTabChange = (tab) => {
    setCurrentTab(tab);
    if (setActiveTab) setActiveTab(tab);
  };

  if (!challenge) return null;

  // Title formatting: "51. Customer Report Excludes Records..."
  const rawTitle = challenge.title || 'Challenge';
  const cleanTitle = rawTitle.replace(/^\[.*?\]\s*/, '').replace(/^\d+\.\s*/, '').trim();
  const displayTitle = `${challenge.id}. ${cleanTitle}`;

  // Derive genuine topics from challenge metadata
  const topics = challenge.topics && challenge.topics.length > 0 
    ? challenge.topics 
    : [challenge.technology || 'Engineering', challenge.category || 'Debugging'];

  // Progressive hints tailored to challenge without answer leaks
  const hints = [
    {
      level: 1,
      title: 'Symptom & Edge Case Observation',
      text: challenge.aiSuggestions && challenge.aiSuggestions[0] 
        ? challenge.aiSuggestions[0] 
        : `Inspect the boundary conditions in ${files[0]?.name || 'the implementation'}. Observe how edge cases (such as NULL, 0, or empty inputs) affect evaluation.`
    },
    {
      level: 2,
      title: 'Underlying Mechanism & Architecture',
      text: challenge.aiSuggestions && challenge.aiSuggestions[1]
        ? challenge.aiSuggestions[1]
        : `Review the execution lifecycle in ${challenge.technology || 'the system'}. Check how state mutations, comparisons, or filter predicates are structured.`
    },
    {
      level: 3,
      title: 'Debugging & Investigation Direction',
      text: challenge.aiSuggestions && challenge.aiSuggestions[2]
        ? challenge.aiSuggestions[2]
        : `Trace the exact control flow for the failing test case. Verify that all records satisfy the required specification before returning output.`
    }
  ];

  // Persistent Reaction Toggle
  const handleToggleReaction = async (reaction) => {
    if (isReacting) return;
    setIsReacting(true);

    try {
      const res = await challengeService.toggleReaction(challenge.id, reaction);
      setLikeCount(res?.likes || 0);
      setDislikeCount(res?.dislikes || 0);
      setIsLiked(res?.userReaction === 'like');
      setIsDisliked(res?.userReaction === 'dislike');
      if (addToast) {
        if (res?.userReaction === reaction) {
          addToast(`Recorded your ${reaction}!`, 'success');
        } else {
          addToast('Reaction removed.', 'info');
        }
      }
    } catch (err) {
      if (err?.message?.includes('401') || err?.message?.toLowerCase().includes('authentication')) {
        if (addToast) addToast('Please sign in to react to challenges.', 'warning');
      } else {
        if (addToast) addToast('Unable to update reaction at this time.', 'error');
      }
    } finally {
      setIsReacting(false);
    }
  };

  // Persistent Star Toggle
  const handleToggleStar = async () => {
    try {
      const res = await challengeService.toggleStar(challenge.id);
      setIsStarred(Boolean(res?.isStarred));
      if (addToast) {
        addToast(res?.isStarred ? 'Added to favorites!' : 'Removed from favorites', 'info');
      }
    } catch (err) {
      if (addToast) addToast('Please sign in to star challenges.', 'warning');
    }
  };

  const handleShare = () => {
    const url = `${window.location.origin}/challenge/${challenge.id}`;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url)
        .then(() => {
          if (addToast) addToast('Challenge link copied to clipboard!', 'success');
        })
        .catch(() => {
          if (addToast) addToast('URL: ' + url, 'info');
        });
    } else {
      if (addToast) addToast('URL: ' + url, 'info');
    }
  };

  const handleSendReport = async (e) => {
    e.preventDefault();
    if (!reportDescription.trim()) return;
    setSubmittingReport(true);
    try {
      await challengeService.submitReport(challenge.id, {
        reportType,
        description: reportDescription
      });
      if (addToast) addToast('Bug report submitted. Thank you!', 'success');
      setShowReportModal(false);
      setReportDescription('');
    } catch (err) {
      if (addToast) addToast(err.message || 'Failed to submit report', 'error');
    } finally {
      setSubmittingReport(false);
    }
  };

  const handleRevealSolution = async () => {
    if (solutionRevealed && solutionData) return;
    setLoadingSolution(true);
    try {
      const res = await challengeService.getSolution(challenge.id);
      setSolutionData(res);
      setSolutionRevealed(true);
      if (addToast) addToast('Official solution unlocked.', 'info');
    } catch (err) {
      if (addToast) addToast('Failed to load reference solution.', 'error');
    } finally {
      setLoadingSolution(false);
    }
  };

  const difficultyColor = 
    challenge.difficulty === 'Easy' 
      ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' 
      : challenge.difficulty === 'Medium' 
      ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' 
      : 'text-rose-400 bg-rose-500/10 border-rose-500/20';

  const displayedSubmissions = realSubmissions.length > 0 ? realSubmissions : submissions;

  return (
    <div className="w-[450px] lg:w-[480px] xl:w-[520px] bg-slate-900 border-r border-slate-800 flex flex-col h-full select-none text-slate-100 shrink-0 relative overflow-hidden font-sans">
      {/* 1. LeetCode Style Tab Strip */}
      <div className="h-10 bg-slate-950/90 border-b border-slate-800 flex items-center justify-between px-2 shrink-0">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
          <button
            onClick={() => handleTabChange('description')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'description'
                ? 'bg-slate-800/90 text-cyan-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
            <span>Description</span>
          </button>

          <button
            onClick={() => handleTabChange('editorial')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'editorial'
                ? 'bg-slate-800/90 text-amber-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-amber-400" />
            <span>Editorial / Hints</span>
          </button>

          <button
            onClick={() => handleTabChange('solutions')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'solutions'
                ? 'bg-slate-800/90 text-indigo-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5 text-indigo-400" />
            <span>Solutions</span>
          </button>

          <button
            onClick={() => handleTabChange('submissions')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'submissions'
                ? 'bg-slate-800/90 text-emerald-400 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            <History className="w-3.5 h-3.5 text-emerald-400" />
            <span>Submissions</span>
          </button>

          {files.length > 1 && (
            <button
              onClick={() => handleTabChange('files')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                currentTab === 'files'
                  ? 'bg-slate-800/90 text-cyan-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              <FolderOpen className="w-3.5 h-3.5" />
              <span>Files ({files.length})</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Main Content Area */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        {/* TAB 1: DESCRIPTION */}
        {currentTab === 'description' && (
          <div className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-3">
                <h1 className="font-heading font-bold text-xl text-slate-100 leading-snug">
                  {displayTitle}
                </h1>
                {challenge.solved && (
                  <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Solved</span>
                  </span>
                )}
              </div>

              {/* Tag Row: Difficulty, Topics, Architecture */}
              <div className="flex flex-wrap items-center gap-2">
                <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full border ${difficultyColor}`}>
                  {challenge.difficulty || 'Easy'}
                </span>

                <button
                  onClick={() => setShowTopics(!showTopics)}
                  className={`flex items-center gap-1.5 px-2.5 py-0.5 text-xs rounded-full border transition-all ${
                    showTopics 
                      ? 'bg-slate-800 border-slate-700 text-cyan-300' 
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Tag className="w-3 h-3 text-cyan-400" />
                  <span>Topics</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${showTopics ? 'rotate-180' : ''}`} />
                </button>

                <button
                  onClick={() => setShowCompanies(!showCompanies)}
                  className={`flex items-center gap-1.5 px-2.5 py-0.5 text-xs rounded-full border transition-all ${
                    showCompanies 
                      ? 'bg-slate-800 border-slate-700 text-amber-300' 
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Briefcase className="w-3.5 h-3.5 text-amber-400" />
                  <span>Scenario Profile</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${showCompanies ? 'rotate-180' : ''}`} />
                </button>
              </div>

              {/* Expandable Topics drawer */}
              {showTopics && (
                <div className="flex flex-wrap gap-1.5 p-2.5 bg-slate-950/80 border border-slate-800 rounded-xl animate-fade-in">
                  {topics.map((t, idx) => (
                    <span key={idx} className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-800/80 text-cyan-300 border border-slate-700/60">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {/* Expandable Company / Scenario drawer */}
              {showCompanies && (
                <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-xs space-y-1 animate-fade-in">
                  <span className="font-semibold text-amber-400 flex items-center gap-1.5">
                    <Briefcase className="w-3.5 h-3.5" />
                    <span>Real-World Engineering Context</span>
                  </span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    Defect scenario inspired by real-world production incidents in {challenge.technology || 'software'} distributed systems.
                  </p>
                </div>
              )}
            </div>

            {/* Human Readable Problem Statement (without answer leakage) */}
            <div className="pt-2">
              <ProblemStatementFormatter
                description={challenge.description}
                title={challenge.title}
                technology={challenge.technology}
                category={challenge.category}
              />
            </div>

            {/* Visible Test Cases Overview */}
            <div className="pt-3 border-t border-slate-800/80">
              <TestCasesSection
                testCases={challenge.testCases || challenge.test_cases || []}
                challengeTitle={challenge.title}
                technology={challenge.technology}
                showHeader={true}
              />
            </div>
          </div>
        )}

        {/* TAB 2: EDITORIAL / HINTS */}
        {currentTab === 'editorial' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <h3 className="font-bold text-sm text-slate-100">Progressive Debugging Hints</h3>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Use progressive hints to guide your investigation without spoiling the defect or solution code.
            </p>

            <div className="space-y-3">
              {hints.map((hint) => {
                const isUnlocked = unlockedHints.includes(hint.level);
                return (
                  <div 
                    key={hint.level} 
                    className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60"
                  >
                    <div 
                      onClick={() => {
                        if (!isUnlocked) {
                          setUnlockedHints(prev => [...prev, hint.level]);
                        }
                      }}
                      className="flex items-center justify-between p-3 cursor-pointer hover:bg-slate-900/80 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold ${
                          isUnlocked ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'
                        }`}>
                          {hint.level}
                        </span>
                        <span className="text-xs font-semibold text-slate-200">{hint.title}</span>
                      </div>
                      {!isUnlocked ? (
                        <span className="text-[11px] text-cyan-400 font-semibold hover:underline">Reveal Hint</span>
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                      )}
                    </div>

                    {isUnlocked && (
                      <div className="p-3 pt-0 text-xs text-slate-300 leading-relaxed border-t border-slate-800/40 mt-1">
                        {hint.text}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 3: SOLUTIONS */}
        {currentTab === 'solutions' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <FlaskConical className="w-4 h-4 text-indigo-400" />
              <h3 className="font-bold text-sm text-slate-100">Official Solution & Root Cause Walkthrough</h3>
            </div>

            {!solutionRevealed ? (
              <div className="p-6 rounded-2xl bg-slate-950/80 border border-slate-800 text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/20 mx-auto flex items-center justify-center">
                  <Lock className="w-6 h-6 text-indigo-400" />
                </div>
                <div className="space-y-1">
                  <h4 className="font-bold text-sm text-slate-200">Reference Solution Guard</h4>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                    Try solving the defect using progressive hints first. Revealing the solution displays the root-cause analysis and reference implementation.
                  </p>
                </div>
                <button
                  onClick={handleRevealSolution}
                  disabled={loadingSolution}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition-all shadow-sm flex items-center gap-2 mx-auto disabled:opacity-50"
                >
                  {loadingSolution ? <Loader2 className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
                  <span>Reveal Reference Solution</span>
                </button>
              </div>
            ) : (
              <div className="space-y-4 animate-fade-in">
                {/* Root Cause Analysis */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    <span>Root Cause Analysis</span>
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {solutionData?.rootCause || 'The defect occurred due to an unhandled boundary condition during input evaluation.'}
                  </p>
                </div>

                {/* Explanation */}
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Fix Explanation</span>
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {solutionData?.explanation || 'The reference fix restores expected behavior by applying defensive validation.'}
                  </p>
                </div>

                {/* Reference Implementation Code */}
                {solutionData?.files && solutionData.files.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Code2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Reference Fix Implementation</span>
                    </h4>
                    {solutionData.files.map((file, idx) => (
                      <div key={idx} className="border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
                        <div className="px-3 py-1.5 bg-slate-900 border-b border-slate-800 text-[11px] font-mono text-slate-300">
                          {file.name}
                        </div>
                        <pre className="p-3 text-[11px] font-mono text-emerald-300 overflow-x-auto leading-relaxed">
                          {file.content}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}

                {/* Prevention Patterns */}
                {solutionData?.prevention && (
                  <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Production Prevention Guidelines</span>
                    </h4>
                    <ul className="space-y-1.5 text-xs text-slate-300 list-disc pl-4">
                      {solutionData.prevention.map((item, idx) => (
                        <li key={idx} className="leading-relaxed">{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SUBMISSIONS */}
        {currentTab === 'submissions' && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <History className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-sm text-slate-100">Submission History</h3>
            </div>

            {loadingSubmissions ? (
              <div className="py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
                <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                <p className="text-xs">Loading submission history...</p>
              </div>
            ) : displayedSubmissions.length > 0 ? (
              <div className="space-y-2">
                {displayedSubmissions.map((sub, idx) => {
                  const isAccepted = sub.success === true;
                  return (
                    <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2.5">
                        {isAccepted ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                        )}
                        <div>
                          <span className={`font-bold ${isAccepted ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isAccepted ? 'Accepted' : 'Wrong Answer'}
                          </span>
                          <p className="text-[10px] text-slate-500">
                            {sub.createdAt ? new Date(sub.createdAt).toLocaleString() : (sub.timestamp || 'Recent attempt')}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-slate-300 flex items-center justify-end gap-1">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{sub.executionTime ? `${Math.round(sub.executionTime * 1000)} ms` : (sub.timeTaken || '10s')}</span>
                        </span>
                        <p className="text-[10px] text-cyan-400 font-semibold">
                          {sub.score ? `+${sub.score} XP` : (isAccepted ? `+${challenge.points || 100} XP` : '0 XP')}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 space-y-2">
                <History className="w-8 h-8 mx-auto opacity-40 text-slate-400" />
                <p className="text-xs">No submissions recorded for this challenge yet.</p>
                <p className="text-[11px] text-slate-600">Click "Run" or "Submit" to test your fix against the evaluator.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 5: MULTI-FILE EXPLORER */}
        {currentTab === 'files' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-800">
              <FolderOpen className="w-4 h-4 text-cyan-400" />
              <h3 className="font-bold text-sm text-slate-100">Workspace Files ({files.length})</h3>
            </div>

            <div className="space-y-1">
              {files.map((file) => (
                <button
                  key={file.name}
                  onClick={() => onSelectFile && onSelectFile(file)}
                  className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-mono transition-all ${
                    file.name === activeFile?.name
                      ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-300'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5" />
                    <span>{file.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 3. LeetCode Style Bottom Action & Reaction Bar (Real Persistent Data) */}
      <div className="h-10 bg-slate-950 border-t border-slate-800 px-4 flex items-center justify-between text-xs text-slate-400 shrink-0">
        <div className="flex items-center gap-3">
          {/* Real Thumbs up */}
          <button 
            onClick={() => handleToggleReaction('like')}
            disabled={isReacting}
            className={`flex items-center gap-1.5 hover:text-slate-200 transition-colors ${isLiked ? 'text-cyan-400 font-semibold' : ''}`}
            title="Like this challenge"
          >
            <ThumbsUp className={`w-3.5 h-3.5 ${isLiked ? 'fill-cyan-400' : ''}`} />
            <span className="text-[11px]">{likeCount}</span>
          </button>

          {/* Real Thumbs down */}
          <button 
            onClick={() => handleToggleReaction('dislike')}
            disabled={isReacting}
            className={`flex items-center gap-1.5 hover:text-slate-200 transition-colors ${isDisliked ? 'text-rose-400 font-semibold' : ''}`}
            title="Dislike"
          >
            <ThumbsDown className={`w-3.5 h-3.5 ${isDisliked ? 'fill-rose-400' : ''}`} />
            <span className="text-[11px]">{dislikeCount}</span>
          </button>

          {/* Real Star / Favorite */}
          <button 
            onClick={handleToggleStar}
            className={`hover:text-amber-400 transition-colors ${isStarred ? 'text-amber-400' : ''}`}
            title="Favorite / Bookmark"
          >
            <Star className={`w-3.5 h-3.5 ${isStarred ? 'fill-amber-400' : ''}`} />
          </button>

          {/* Functional Share */}
          <button 
            onClick={handleShare}
            className="hover:text-slate-200 transition-colors"
            title="Share challenge URL"
          >
            <Share2 className="w-3.5 h-3.5" />
          </button>

          {/* Functional Report Issue */}
          <button 
            onClick={() => setShowReportModal(true)}
            className="hover:text-amber-400 transition-colors"
            title="Report defect or issue"
          >
            <Flag className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Challenge Evaluation Engine Status (Truthful - no fake online count) */}
        <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80" />
          <span>Evaluation Engine Ready</span>
        </div>
      </div>

      {/* Functional Report Issue Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4 animate-scale-up">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <Flag className="w-4 h-4 text-amber-400" />
                <span>Report Challenge Issue</span>
              </h3>
              <button onClick={() => setShowReportModal(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSendReport} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Issue Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="broken_challenge">Broken or Untestable Challenge</option>
                  <option value="bad_instructions">Unclear Instructions</option>
                  <option value="test_case_bug">Incorrect Test Case Assertion</option>
                  <option value="typo">Typo or Formatting Error</option>
                  <option value="other">Other Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
                <textarea
                  value={reportDescription}
                  onChange={(e) => setReportDescription(e.target.value)}
                  placeholder="Describe the issue you encountered..."
                  rows={4}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="button-secondary px-3 py-1.5 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingReport}
                  className="button-primary px-4 py-1.5 text-xs flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{submittingReport ? 'Submitting...' : 'Send Report'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
