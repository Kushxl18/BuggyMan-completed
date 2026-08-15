import React, { useState } from 'react';
import { 
  FileText, 
  Target, 
  CheckCircle2, 
  Clock, 
  Award, 
  AlertCircle, 
  FolderOpen,
  FileCode,
  Flag,
  Send,
  X
} from 'lucide-react';
import { challengeService } from '../../services/challengeService';

export default function ProblemStatementPanel({ 
  challenge, 
  files = [], 
  activeFile, 
  onSelectFile, 
  activeTab = 'problem', 
  setActiveTab,
  addToast
}) {
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportType, setReportType] = useState('broken_challenge');
  const [reportDescription, setReportDescription] = useState('');
  const [submittingReport, setSubmittingReport] = useState(false);

  if (!challenge) return null;

  const handleSendReport = async (e) => {
    e.preventDefault();
    if (!reportDescription.trim()) return;
    setSubmittingReport(true);
    try {
      await challengeService.submitReport(challenge.id, {
        reportType,
        description: reportDescription
      });
      if (addToast) addToast('Issue report submitted successfully! Thank you.', 'success');
      setShowReportModal(false);
      setReportDescription('');
    } catch (err) {
      if (addToast) addToast(err.message || 'Failed to submit report', 'error');
    } finally {
      setSubmittingReport(false);
    }
  };

  return (
    <div className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col h-full select-none text-slate-100 relative">
      {/* Top Sidebar Header Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-950/80 p-1">
        <button
          onClick={() => setActiveTab('problem')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'problem'
              ? 'bg-slate-900 text-cyan-400 border border-slate-800/80 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Problem</span>
        </button>

        <button
          onClick={() => setActiveTab('files')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
            activeTab === 'files'
              ? 'bg-slate-900 text-cyan-400 border border-slate-800/80 shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FolderOpen className="w-3.5 h-3.5" />
          <span>Files ({files.length})</span>
        </button>
      </div>

      {/* Tab 1: Problem Statement View */}
      {activeTab === 'problem' && (
        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          {/* Header Metadata */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className={`badge ${
                challenge.difficulty === 'Easy' ? 'badge-emerald' : challenge.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
              }`}>
                {challenge.difficulty || 'Easy'}
              </span>
              <span className="text-[10px] font-bold text-slate-500 uppercase">{challenge.technology || 'React'}</span>
            </div>

            <h2 className="font-heading font-bold text-lg text-slate-100 leading-tight">
              {challenge.title}
            </h2>

            <div className="flex items-center gap-4 text-[11px] font-semibold text-slate-400 border-y border-slate-800/80 py-2">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>{challenge.timeEstimate || challenge.time_estimate || '15 mins'}</span>
              </div>
              <div className="flex items-center gap-1.5 text-cyan-400">
                <Award className="w-3.5 h-3.5 text-cyan-400" />
                <span>{challenge.points || 100} XP</span>
              </div>
            </div>
          </div>

          {/* Detailed Problem Statement */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-cyan-400" />
              <span>Problem Statement</span>
            </h3>
            <div className="text-xs text-slate-300 leading-relaxed bg-slate-950/50 border border-slate-800 p-3.5 rounded-xl space-y-2 font-sans">
              <p>{challenge.description || 'No description provided for this challenge yet.'}</p>
            </div>
          </div>

          {/* Suspected Component / Location */}
          {challenge.suspectedComponent && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Suspected Component</span>
              </h3>
              <div className="text-xs font-mono text-amber-300 bg-amber-500/10 border border-amber-500/20 p-2.5 rounded-xl">
                {challenge.suspectedComponent}
              </div>
            </div>
          )}

          {/* Test Cases Requirements */}
          {Array.isArray(challenge.testCases) && challenge.testCases.length > 0 && (
            <div className="space-y-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Test Cases ({challenge.testCases.length})</span>
              </h3>
              <div className="space-y-2">
                {challenge.testCases.map((tc, idx) => (
                  <div key={tc.id || idx} className="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center justify-between font-medium text-slate-200">
                      <span>{tc.name}</span>
                    </div>
                    {tc.expected && (
                      <p className="text-[10px] text-slate-400 font-mono">
                        Expected: <span className="text-emerald-400">{tc.expected}</span>
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Report Challenge Button */}
          <div className="pt-3 border-t border-slate-800">
            <button
              onClick={() => setShowReportModal(true)}
              className="flex items-center justify-center gap-2 w-full py-2 px-3 text-[11px] font-semibold text-slate-400 hover:text-amber-400 bg-slate-950/40 hover:bg-amber-500/10 border border-slate-800 hover:border-amber-500/30 rounded-xl transition-all"
            >
              <Flag className="w-3.5 h-3.5 text-amber-400" />
              <span>Report An Issue</span>
            </button>
          </div>
        </div>
      )}

      {/* Tab 2: File Explorer View */}
      {activeTab === 'files' && (
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          <div className="px-2 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Files in Workspace
          </div>
          {files.map((file) => {
            const isActive = file.name === activeFile?.name;
            return (
              <button
                key={file.name}
                onClick={() => onSelectFile(file)}
                className={`flex items-center gap-2.5 w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/15 border-l-2 border-blue-500 text-slate-100 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <FileCode className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span className="truncate">{file.name}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-400">
                <Flag className="w-5 h-5" />
                <h3 className="text-base font-bold text-slate-100">Report Challenge Issue</h3>
              </div>
              <button onClick={() => setShowReportModal(false)} className="text-slate-400 hover:text-slate-200 p-1 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSendReport} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Issue Category</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:border-amber-500 focus:outline-none"
                >
                  <option value="broken_challenge">Broken Challenge / Crash</option>
                  <option value="wrong_test">Incorrect Test Case Assertion</option>
                  <option value="incorrect_question">Unclear Problem Description</option>
                  <option value="evaluation_problem">Evaluation Engine Failure</option>
                  <option value="other">Other Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Issue Description</label>
                <textarea
                  rows={4}
                  value={reportDescription}
                  onChange={(e) => setReportDescription(e.target.value)}
                  placeholder="Describe what went wrong or which test case failed incorrectly..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:border-amber-500 focus:outline-none resize-none"
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingReport || !reportDescription.trim()}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-lg transition-all"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{submittingReport ? 'Submitting...' : 'Submit Report'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
