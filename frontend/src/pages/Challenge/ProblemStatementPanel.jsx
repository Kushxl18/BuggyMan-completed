import React, { useState, useEffect } from 'react';
import { 
  FileText, 
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
  Loader2,
  Clock
} from 'lucide-react';
import { challengeService } from '../../services/challengeService';
import ProblemStatementFormatter from '../../components/ProblemStatementFormatter';

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

  // Report Modal State
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportType, setReportType] = useState('broken_challenge');
  const [reportDescription, setReportDescription] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  useEffect(() => {
    if (activeTab) setCurrentTab(activeTab);
  }, [activeTab]);

  // Load actual persistent engagement on challenge mount
  useEffect(() => {
    if (!challenge?.id) return;

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

  // Consistent Title formatting matching the authoritative challenge metadata
  const rawTitle = challenge.title || 'Challenge';
  const cleanTitle = challenge.canonicalTitle || challenge.canonical_title || rawTitle.replace(/^\[.*?\]\s*/, '').replace(/^\d+\.\s*/, '').trim();
  const displayTitle = challenge.displayTitle || challenge.display_title || (challenge.displayNumber ? `${challenge.displayNumber}. ${cleanTitle}` : cleanTitle);

  // Derive genuine topics from challenge metadata
  const topics = challenge.topics && challenge.topics.length > 0 
    ? challenge.topics 
    : [challenge.technology || 'Engineering', challenge.category || 'Debugging'];

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

  const difficultyColor = 
    challenge.difficulty === 'Easy' 
      ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' 
      : challenge.difficulty === 'Medium' 
      ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' 
      : 'text-rose-400 bg-rose-500/10 border-rose-500/20';

  const displayedSubmissions = realSubmissions.length > 0 ? realSubmissions : submissions;

  return (
    <div className="w-[450px] lg:w-[480px] xl:w-[520px] bg-[var(--bg-card)] border-r border-[var(--border-color)] flex flex-col h-full select-none text-[var(--text-primary)] shrink-0 relative overflow-hidden font-sans">
      {/* 1. LeetCode Style Tab Strip */}
      <div className="h-10 bg-[var(--bg-main)] border-b border-[var(--border-color)] flex items-center justify-between px-2 shrink-0">
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
          <button
            onClick={() => handleTabChange('description')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'description'
                ? 'bg-[var(--bg-hover)] text-[var(--brand-cyan)] shadow-sm'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
            }`}
          >
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
            <span>Description</span>
          </button>

          <button
            onClick={() => handleTabChange('submissions')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              currentTab === 'submissions'
                ? 'bg-[var(--bg-hover)] text-[var(--color-success)] shadow-sm'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
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
                  ? 'bg-[var(--bg-hover)] text-[var(--brand-cyan)] shadow-sm'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
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

            {/* Concise LeetCode Style Problem Statement (Problem Statement, Examples, Constraints) */}
            <div className="pt-2">
              <ProblemStatementFormatter
                description={challenge.description}
                title={challenge.title}
                technology={challenge.technology}
                category={challenge.category}
                testCases={challenge.testCases || challenge.test_cases || []}
                files={files}
              />
            </div>
          </div>
        )}

        {/* TAB 2: SUBMISSIONS */}
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
            <div className="flex items-center gap-2 pb-2 border-b border-[var(--border-color)]">
              <FolderOpen className="w-4 h-4 text-cyan-400" />
              <h3 className="font-bold text-sm text-[var(--text-primary)]">Workspace Files ({files.length})</h3>
            </div>

            <div className="space-y-1">
              {files.map((file) => (
                <button
                  key={file.name}
                  onClick={() => onSelectFile && onSelectFile(file)}
                  className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-mono transition-all ${
                    file.name === activeFile?.name
                      ? 'bg-[var(--brand-cyan-bg)] border-[var(--brand-cyan)] text-[var(--brand-cyan)]'
                      : 'bg-[var(--bg-main)] border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
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
