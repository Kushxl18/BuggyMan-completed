import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { 
  Trophy, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  RotateCcw, 
  ArrowRight,
  Sparkles,
  Award,
  Terminal,
  History,
  FileCode,
  ChevronDown,
  ChevronUp,
  Home,
  Tag,
  AlertOctagon
} from 'lucide-react';
import { challengeService } from '../services/challengeService';
import TestCasesSection from '../components/TestCasesSection';

const getStoredSubmission = () => {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.sessionStorage.getItem('buggyman-last-submission');
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
};

export default function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const state = location.state || getStoredSubmission() || {
    success: true,
    score: 100,
    timeTaken: '0m 05s',
    bugsFixed: 1,
    remainingIssues: 0,
    testCases: [
      { id: 1, name: 'Sample Execution Test', input: 'main()', expected: 'Clean exit', actual: 'Clean exit', passed: true }
    ],
    aiSummary: 'Excellent fix! All test cases passed successfully.',
    stdout: 'Execution finished without errors.',
    stderr: '',
    challengeId: '1',
    attemptNumber: 1,
    alreadySolved: false
  };

  const { 
    success, 
    score, 
    timeTaken, 
    bugsFixed, 
    remainingIssues, 
    testCases, 
    aiSummary, 
    stdout,
    stderr,
    challengeId, 
    attemptNumber, 
    alreadySolved 
  } = state;

  const [activeTab, setActiveTab] = useState('tests'); // 'tests' | 'terminal' | 'history' | 'explanation'
  const [challengeInfo, setChallengeInfo] = useState(null);
  const [attemptHistory, setAttemptHistory] = useState([]);
  const [expandedTestId, setExpandedTestId] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const normalizedTestCases = Array.isArray(testCases) ? testCases : [];
  const passedCount = normalizedTestCases.filter(t => t.passed).length;
  const totalCount = normalizedTestCases.length;

  const handleFetchExplanation = async () => {
    if (!challengeId) return;
    try {
      setLoadingExplanation(true);
      const res = await challengeService.explainSolution(challengeId, {
        submittedCode: state.code || ''
      });
      if (res) {
        setExplanation(res);
      }
    } catch (err) {
      console.error('Failed to fetch solution explanation:', err);
    } finally {
      setLoadingExplanation(false);
    }
  };

  useEffect(() => {
    if (!challengeId) return;

    async function fetchResultContext() {
      try {
        const chal = await challengeService.getChallengeById(challengeId);
        setChallengeInfo(chal);
      } catch (err) {
        // Silently handle if challenge not found
      }

      setLoadingHistory(true);
      try {
        const historyData = await challengeService.getChallengeSubmissions(challengeId);
        if (historyData && Array.isArray(historyData.submissions)) {
          setAttemptHistory(historyData.submissions);
        }
      } catch (err) {
        // Silently handle if unauthenticated or error
      } finally {
        setLoadingHistory(false);
      }
    }

    fetchResultContext();
  }, [challengeId]);

  const toggleExpandTest = (id) => {
    setExpandedTestId(prev => (prev === id ? null : id));
  };

  return (
    <div className="theme-adaptive-page max-w-3xl mx-auto py-8 space-y-8 animate-fade-in px-4">
      
      {/* Top Header & Banner */}
      <div className={`p-8 rounded-3xl border text-center space-y-4 relative overflow-hidden ${
        success 
          ? 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-brand-emerald/30 shadow-glow-emerald' 
          : 'bg-rose-50 dark:bg-rose-950/20 border-rose-200 dark:border-brand-rose/30 shadow-glow-rose'
      }`}>
        <div className={`absolute top-0 right-0 p-8 opacity-10 font-heading text-8xl font-black ${
          success ? 'text-brand-emerald' : 'text-brand-rose'
        }`}>
          {success ? 'SUCCESS' : 'FAILED'}
        </div>

        <div className="relative z-10 flex flex-col items-center gap-3">
          {/* Metadata Row */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {attemptNumber && (
              <span className="px-3 py-1 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-full text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider shadow-sm">
                Attempt #{attemptNumber}
              </span>
            )}
            {challengeInfo?.technology && (
              <span className="px-3 py-1 bg-indigo-50 dark:bg-indigo-950/80 border border-indigo-200 dark:border-indigo-500/30 rounded-full text-[10px] font-bold text-indigo-700 dark:text-cyan-400 uppercase tracking-wider shadow-sm">
                {challengeInfo.technology}
              </span>
            )}
            {challengeInfo?.difficulty && (
              <span className="px-3 py-1 bg-amber-50 dark:bg-slate-900/80 border border-amber-200 dark:border-slate-800 rounded-full text-[10px] font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider shadow-sm">
                {challengeInfo.difficulty}
              </span>
            )}
          </div>

          <div className={`p-4 rounded-full ${success ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
            {success ? (
              <CheckCircle2 className="w-16 h-16 text-brand-emerald animate-pulse-glow" />
            ) : (
              <XCircle className="w-16 h-16 text-brand-rose" />
            )}
          </div>

          <h1 className="font-heading font-extrabold text-3xl text-slate-900 dark:text-slate-100">
            {challengeInfo?.title ? challengeInfo.title : (success ? 'Challenge Completed!' : 'Test Failures Detected')}
          </h1>

          <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto">
            {success 
              ? (alreadySolved ? 'Solution verified successfully. No duplicate XP awarded.' : 'Awesome work! All tests executed correctly without issues.') 
              : 'The project compiled with remaining bugs. Review test details and logs below.'}
          </p>
        </div>
      </div>

      {/* Metrics Row Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* XP Awarded */}
        <div className="glass-card p-4 rounded-2xl text-center space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">XP Awarded</span>
          <div className="inline-flex items-center justify-center gap-1.5 text-brand-indigo font-heading font-extrabold text-xl">
            <Award className="w-4.5 h-4.5" />
            <span>{alreadySolved ? '0 XP' : `+${score}`}</span>
          </div>
        </div>

        {/* Time Spent */}
        <div className="glass-card p-4 rounded-2xl text-center space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Time Spent</span>
          <div className="inline-flex items-center justify-center gap-1.5 text-slate-800 dark:text-slate-300 font-heading font-extrabold text-xl">
            <Clock className="w-4.5 h-4.5 text-slate-400" />
            <span>{timeTaken}</span>
          </div>
        </div>

        {/* Tests Passed / Total */}
        <div className="glass-card p-4 rounded-2xl text-center space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Tests Passed</span>
          <p className={`text-xl font-heading font-extrabold ${success ? 'text-brand-emerald' : 'text-brand-rose'}`}>
            {passedCount} / {totalCount || 1}
          </p>
        </div>

        {/* Remaining Issues */}
        <div className="glass-card p-4 rounded-2xl text-center space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Remaining Bugs</span>
          <p className={`text-xl font-heading font-extrabold ${remainingIssues > 0 ? 'text-brand-rose' : 'text-slate-400'}`}>
            {remainingIssues}
          </p>
        </div>
      </div>

      {/* Main Content Tabs Menu */}
      <div className="glass-card rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 flex items-center px-4 overflow-x-auto">
          <button
            onClick={() => setActiveTab('tests')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'tests'
                ? 'border-brand-indigo text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-900/60'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 text-brand-emerald" />
            <span>Test Case Breakdown ({passedCount}/{totalCount || 1})</span>
          </button>

          <button
            onClick={() => setActiveTab('terminal')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'terminal'
                ? 'border-brand-indigo text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-900/60'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>Terminal Logs</span>
          </button>

          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'history'
                ? 'border-brand-indigo text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-900/60'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <History className="w-4 h-4 text-amber-400" />
            <span>Attempt History ({attemptHistory.length})</span>
          </button>

          <button
            onClick={() => { setActiveTab('explanation'); if (!explanation) handleFetchExplanation(); }}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'explanation'
                ? 'border-amber-500 text-amber-700 dark:text-amber-300 bg-white dark:bg-slate-900/60'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-300'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-300 animate-pulse-glow" />
            <span>AI Solution Explanation</span>
          </button>
        </div>

        {/* Tab View Contents */}
        <div className="p-6">
          
          {/* TAB 1: Test Cases Breakdown */}
          {activeTab === 'tests' && (
            <TestCasesSection 
              testCases={normalizedTestCases} 
              challengeTitle={challengeInfo?.title} 
              technology={challengeInfo?.technology} 
              showHeader={false} 
            />
          )}

          {/* TAB 2: Terminal Execution Logs */}
          {activeTab === 'terminal' && (
            <div className="space-y-4">
              <div>
                <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-cyan-400" />
                  <span>Standard Execution Output (stdout)</span>
                </h4>
                <div className="p-4 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-900 font-mono text-xs text-slate-800 dark:text-slate-300 leading-relaxed max-h-60 overflow-y-auto">
                  {stdout ? (
                    <pre className="whitespace-pre-wrap">{stdout}</pre>
                  ) : (
                    <p className="text-slate-500 italic">No standard output recorded.</p>
                  )}
                </div>
              </div>

              {stderr && (
                <div>
                  <h4 className="text-xs font-bold text-rose-400 mb-2 flex items-center gap-2">
                    <AlertOctagon className="w-4 h-4 text-rose-400" />
                    <span>Error Output / Traceback (stderr)</span>
                  </h4>
                  <div className="p-4 bg-rose-50 dark:bg-rose-950/30 rounded-xl border border-rose-200 dark:border-rose-500/30 font-mono text-xs text-rose-800 dark:text-rose-300 leading-relaxed max-h-60 overflow-y-auto">
                    <pre className="whitespace-pre-wrap">{stderr}</pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Attempt History */}
          {activeTab === 'history' && (
            <div className="space-y-3">
              {loadingHistory ? (
                <p className="text-xs text-slate-500 italic text-center py-4">Loading attempt history...</p>
              ) : attemptHistory.length > 0 ? (
                attemptHistory.map((att) => (
                  <div 
                    key={att.id}
                    className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-900 text-xs"
                  >
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-slate-600 dark:text-slate-400">Attempt #{att.attemptNumber}</span>
                      {att.success ? (
                        <span className="flex items-center gap-1 text-brand-emerald font-semibold">
                          <CheckCircle2 className="w-4 h-4" /> Passed
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-brand-rose font-semibold">
                          <XCircle className="w-4 h-4" /> Failed
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-slate-400">
                      <span>Score: <strong className="text-slate-900 dark:text-slate-200">+{att.score} XP</strong></span>
                      <span>Time: <strong className="text-slate-900 dark:text-slate-200">{att.executionTime ? `${att.executionTime}s` : 'N/A'}</strong></span>
                      <span className="text-[10px] text-slate-500">
                        {att.createdAt ? new Date(att.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic text-center py-4">No previous attempts recorded for this challenge.</p>
              )}
            </div>
          )}

          {/* TAB 4: AI Solution Explanation */}
          {activeTab === 'explanation' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-slate-50 dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-300 animate-pulse-glow" />
                  <span className="font-bold text-slate-800 dark:text-slate-200 text-xs uppercase tracking-wider font-sans">AI Solution Post-Mortem & Educational Analysis</span>
                </div>
                <button
                  onClick={handleFetchExplanation}
                  disabled={loadingExplanation}
                  className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
                >
                  {loadingExplanation ? 'Analyzing Solution...' : 'Refresh AI Explanation'}
                </button>
              </div>

              {explanation ? (
                <div className="space-y-4 font-sans text-xs">
                  <div className="bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400">1. What The Bug Was</span>
                    <p className="text-slate-800 dark:text-slate-200 leading-relaxed">{explanation.whatTheBugWas}</p>
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">2. Why It Happened</span>
                    <p className="text-slate-800 dark:text-slate-200 leading-relaxed">{explanation.whyItHappened}</p>
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">3. Why The Fix Works</span>
                    <p className="text-slate-800 dark:text-slate-200 leading-relaxed">{explanation.whyFixWorks}</p>
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">4. Key Engineering Concept</span>
                    <p className="text-slate-800 dark:text-slate-200 leading-relaxed">{explanation.keyConcept}</p>
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-violet-400">5. Alternative Approaches & Design Patterns</span>
                    <p className="text-slate-800 dark:text-slate-200 leading-relaxed">{explanation.alternativeApproaches}</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 font-sans">
                  <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-50 text-amber-300" />
                  <p className="text-xs text-slate-400">Click "Refresh AI Explanation" to generate a detailed post-mortem breakdown of your solution.</p>
                </div>
              )}
            </div>
          )}

        </div>
      </div>

      {/* AI Evaluation Review Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <Sparkles className="w-16 h-16 text-brand-violet" />
        </div>
        <div className="flex items-center gap-2 text-xs font-bold text-brand-violet uppercase tracking-wider font-heading">
          <Sparkles className="w-4.5 h-4.5 text-brand-violet animate-pulse-glow" />
          <span>AI Feedback Evaluation</span>
        </div>
        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-mono bg-slate-50 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/80 p-4 rounded-xl">
          {aiSummary}
        </p>
      </div>

      {/* Navigation Triggers */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <Link 
          to="/dashboard"
          className="button-secondary text-xs px-4 py-2.5"
        >
          <Home className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        <div className="flex items-center gap-3">
          <Link 
            to={`/challenge/${challengeId}`}
            className="button-secondary text-xs px-5 py-2.5 border-cyan-500/30 text-cyan-400"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Retry Workspace</span>
          </Link>
          
          <Link 
            to="/challenges"
            className="button-primary text-xs px-5 py-2.5"
          >
            <span>Next Challenge</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

    </div>
  );
}
