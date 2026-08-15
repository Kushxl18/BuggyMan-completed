import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Code2, 
  Activity, 
  Cpu, 
  Trash2, 
  Plus, 
  Edit, 
  Eye, 
  ShieldAlert, 
  FileCode,
  X,
  Loader2
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { challengeService } from '../services/challengeService';

export default function AdminDashboard({ addToast }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('challenges'); // challenges, submissions
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);

  // Challenge Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState('Easy');
  const [technology, setTechnology] = useState('React');
  const [category, setCategory] = useState('State Management');
  const [timeEstimate, setTimeEstimate] = useState('10 mins');
  const [points, setPoints] = useState('100');
  const [fileName, setFileName] = useState('App.jsx');
  const [fileContent, setFileContent] = useState('');
  const [bugSignature, setBugSignature] = useState('');
  const [suspectedComponent, setSuspectedComponent] = useState('');
  const [aiSuggestions, setAiSuggestions] = useState('');

  // Simulated submissions database
  const [submissions, setSubmissions] = useState([
    { id: 101, user: 'Alex Rivera', challenge: 'Fix React State Updates', time: '10 mins ago', status: 'Success', points: 100 },
    { id: 102, user: 'Sam Chen', challenge: 'Django API Serializer validation', time: '1 hour ago', status: 'Failed', points: 0 },
    { id: 103, user: 'Devon Smith', challenge: 'Fix Todo Item Toggle', time: '3 hours ago', status: 'Success', points: 150 }
  ]);

  useEffect(() => {
    async function loadAdminData() {
      try {
        setLoading(true);
        const data = await challengeService.getAdminStats();
        setStats(data);
      } catch (err) {
        addToast('Error loading admin control board stats.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, [addToast]);

  const handleCreateChallenge = async (e) => {
    e.preventDefault();
    if (!title || !description || !fileContent || !bugSignature) {
      addToast('Please fill out essential fields.', 'warning');
      return;
    }

    setSubmitLoading(true);
    try {
      const payload = {
        title,
        description,
        difficulty,
        technology,
        category,
        timeEstimate,
        points,
        files: [{ name: fileName, content: fileContent }],
        bugSignature,
        suspectedComponent,
        aiSuggestions: aiSuggestions.split('\n').filter(Boolean)
      };

      const created = await challengeService.createChallenge(payload);
      
      setStats(prev => ({
        ...prev,
        totalChallenges: prev.totalChallenges + 1,
        challenges: [...prev.challenges, created]
      }));

      setIsAddOpen(false);
      addToast('New challenge and buggy template injected successfully!', 'success');
      
      setTitle('');
      setDescription('');
      setFileContent('');
      setBugSignature('');
      setSuspectedComponent('');
      setAiSuggestions('');
    } catch (err) {
      addToast('Failed to deploy challenge.', 'error');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleDeleteChallenge = (id) => {
    if (window.confirm('Are you sure you want to delete this challenge?')) {
      setStats(prev => ({
        ...prev,
        totalChallenges: prev.totalChallenges - 1,
        challenges: prev.challenges.filter(c => c.id !== id)
      }));
      addToast('Challenge template removed.', 'info');
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-cyan-500" />
          <span>Admin Dashboard</span>
        </h1>
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Configure challenge parameters, deploy code templates, and inspect developer submissions.</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Users */}
        <div className="glass-card p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 rounded-xl">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total Enrolled</span>
            <p className="text-xl font-heading font-extrabold text-slate-800 dark:text-[#F0F2F4]">{stats.totalUsers}</p>
          </div>
        </div>

        {/* Challenges */}
        <div className="glass-card p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 rounded-xl">
            <Code2 className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total Challenges</span>
            <p className="text-xl font-heading font-extrabold text-slate-800 dark:text-[#F0F2F4]">{stats.totalChallenges}</p>
          </div>
        </div>

        {/* Active */}
        <div className="glass-card p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded-xl">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Active Ranks</span>
            <p className="text-xl font-heading font-extrabold text-slate-800 dark:text-[#F0F2F4]">{stats.activeUsersNow}</p>
          </div>
        </div>

        {/* AI Calls */}
        <div className="glass-card p-5 rounded-xl flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded-xl">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">AI Hint Tokens</span>
            <p className="text-xl font-heading font-extrabold text-slate-800 dark:text-[#F0F2F4]">{stats.aiUsageCount} Calls</p>
          </div>
        </div>
      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-200 dark:border-[#292E33]">
        <button
          onClick={() => setActiveTab('challenges')}
          className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
            activeTab === 'challenges'
              ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400 bg-slate-100 dark:bg-[#1B1F23]'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
          }`}
        >
          Manage Challenges ({stats.challenges.length})
        </button>
        <button
          onClick={() => setActiveTab('submissions')}
          className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
            activeTab === 'submissions'
              ? 'border-cyan-500 text-cyan-600 dark:text-cyan-400 bg-slate-100 dark:bg-[#1B1F23]'
              : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
          }`}
        >
          Recent Submissions ({submissions.length})
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'challenges' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Active Coding Challenges</h3>
            <button
              onClick={() => setIsAddOpen(true)}
              className="button-primary text-xs py-2 px-3"
            >
              <Plus className="w-4 h-4" />
              <span>Add Challenge</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stats.challenges.map(chal => (
              <div key={chal.id} className="glass-panel p-5 rounded-xl border border-slate-200 dark:border-[#292E33] flex flex-col justify-between transition-all">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="badge badge-cyan">{chal.technology}</span>
                    <span className="text-[10px] text-slate-500 uppercase font-bold">{chal.difficulty}</span>
                  </div>
                  <h4 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">{chal.title}</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2">{chal.description}</p>
                </div>
                
                <div className="flex justify-end gap-2 border-t border-slate-200 dark:border-[#292E33] pt-3.5 mt-4">
                  <button 
                    onClick={() => addToast('Editing challenges is disabled in demo mode.', 'info')}
                    className="p-2 bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-lg text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
                  >
                    <Edit className="w-3.5 h-3.5" />
                  </button>
                  <button 
                    onClick={() => handleDeleteChallenge(chal.id)}
                    className="p-2 bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-lg text-rose-500 hover:text-rose-600 transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'submissions' && (
        <div className="glass-panel rounded-xl border border-slate-200 dark:border-[#292E33] overflow-hidden">
          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-100 dark:bg-[#1B1F23] border-b border-slate-200 dark:border-[#292E33] text-slate-600 dark:text-slate-400 font-bold uppercase">
                  <th className="p-4">Submission ID</th>
                  <th className="p-4">Student</th>
                  <th className="p-4">Challenge</th>
                  <th className="p-4">Time Evaluated</th>
                  <th className="p-4 text-center">Status</th>
                  <th className="p-4 text-right pr-6">XP Gained</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-[#292E33] text-slate-700 dark:text-slate-300">
                {submissions.map(sub => (
                  <tr key={sub.id} className="hover:bg-slate-50 dark:hover:bg-[#1B1F23]">
                    <td className="p-4 font-mono font-bold text-slate-500">#SUB-{sub.id}</td>
                    <td className="p-4 font-semibold text-slate-800 dark:text-[#F0F2F4]">{sub.user}</td>
                    <td className="p-4 text-slate-600 dark:text-slate-400">{sub.challenge}</td>
                    <td className="p-4 text-slate-500">{sub.time}</td>
                    <td className="p-4 text-center">
                      <span className={`badge ${
                        sub.status === 'Success' ? 'badge-emerald' : 'badge-rose'
                      }`}>
                        {sub.status}
                      </span>
                    </td>
                    <td className="p-4 text-right pr-6 font-bold text-slate-800 dark:text-[#F0F2F4]">{sub.points} XP</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MODAL: Add Challenge */}
      {isAddOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 backdrop-blur-sm" onClick={() => setIsAddOpen(false)} />
          <div className="relative w-full max-w-2xl glass-panel rounded-xl p-6 border border-slate-200 dark:border-[#292E33] shadow-2xl z-10 animate-slide-up max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-5 border-b border-slate-200 dark:border-[#292E33] pb-3">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
                <FileCode className="w-5 h-5 text-cyan-500" />
                <span>Inject New Challenge & Bugs</span>
              </h3>
              <button onClick={() => setIsAddOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateChallenge} className="space-y-4 text-xs text-slate-700 dark:text-slate-300">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Challenge Title</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                    placeholder="e.g. Fix Promise Rejection"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Points XP</label>
                  <input
                    type="number"
                    value={points}
                    onChange={(e) => setPoints(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                    placeholder="100"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                  >
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Technology</label>
                  <select
                    value={technology}
                    onChange={(e) => setTechnology(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                  >
                    <option value="React">React</option>
                    <option value="Django">Django</option>
                    <option value="NodeJS">NodeJS</option>
                    <option value="CSS">CSS</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Est. Time</label>
                  <input
                    type="text"
                    value={timeEstimate}
                    onChange={(e) => setTimeEstimate(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                    placeholder="15 mins"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Challenge Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows="2"
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none resize-none"
                  placeholder="Summarize the bug criteria..."
                  required
                />
              </div>

              {/* Buggy Template Injector */}
              <div className="border border-slate-200 dark:border-[#292E33] p-4 rounded-lg bg-slate-50 dark:bg-[#1B1F23] space-y-3">
                <h4 className="font-heading font-bold text-slate-800 dark:text-[#F0F2F4] text-[10px] uppercase tracking-wider">Code Template & Bug Injection</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-slate-500 uppercase">Filename</label>
                    <input
                      type="text"
                      value={fileName}
                      onChange={(e) => setFileName(e.target.value)}
                      className="w-full bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                      required
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-bold text-slate-500 uppercase">Buggy Code Signature</label>
                    <input
                      type="text"
                      value={bugSignature}
                      onChange={(e) => setBugSignature(e.target.value)}
                      className="w-full bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none font-mono text-[10px]"
                      placeholder="e.g. data.value = value"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Template Code Contents</label>
                  <textarea
                    value={fileContent}
                    onChange={(e) => setFileContent(e.target.value)}
                    rows="4"
                    className="w-full bg-white dark:bg-[#15181B] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none resize-none font-mono text-[10px]"
                    placeholder="Write template boilerplate..."
                    required
                  />
                </div>
              </div>

              {/* AI helper info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Suspected Component</label>
                  <input
                    type="text"
                    value={suspectedComponent}
                    onChange={(e) => setSuspectedComponent(e.target.value)}
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none"
                    placeholder="Counter handleIncrement"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">AI Suggestions (One suggestion per line)</label>
                  <textarea
                    value={aiSuggestions}
                    onChange={(e) => setAiSuggestions(e.target.value)}
                    rows="2"
                    className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-2 outline-none resize-none"
                    placeholder="Provide updater functions..."
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 border-t border-slate-200 dark:border-[#292E33] pt-3 mt-4">
                <button type="button" onClick={() => setIsAddOpen(false)} className="button-secondary text-xs py-2 px-4">
                  Cancel
                </button>
                <button type="submit" disabled={submitLoading} className="button-primary text-xs py-2 px-4">
                  {submitLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Deploy Challenge</span>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
