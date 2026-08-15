import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  GraduationCap, 
  BookOpen, 
  Award, 
  Flame, 
  CheckCircle2, 
  Edit3, 
  Key, 
  X, 
  Loader2 
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import ProgressBar from '../components/ProgressBar';
import { authService } from '../services/authService';

export default function UserProfile({ addToast }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Modals state
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isPassOpen, setIsPassOpen] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  // Edit fields
  const [editName, setEditName] = useState('');
  const [editCollege, setEditCollege] = useState('');
  const [editBio, setEditBio] = useState('');
  const [editAvatar, setEditAvatar] = useState('');

  // Password fields
  const [oldPass, setOldPass] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirmNewPass, setConfirmNewPass] = useState('');

  useEffect(() => {
    async function loadProfile() {
      try {
        setLoading(true);
        const res = await authService.getCurrentUser();
        setProfile(res);
        setEditName(res.name);
        setEditCollege(res.college);
        setEditBio(res.bio);
        setEditAvatar(res.avatar);
      } catch (err) {
        addToast('Failed to load user profile.', 'error');
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, [addToast]);

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setModalLoading(true);
    try {
      const updated = await authService.updateProfile({
        display_name: editName,
        college: editCollege,
        bio: editBio,
        avatar: editAvatar
      });
      setProfile(updated);
      setIsEditOpen(false);
      addToast('Profile updated successfully!', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to update profile.', 'error');
    } finally {
      setModalLoading(false);
    }
  };

  const handlePassSubmit = async (e) => {
    e.preventDefault();
    if (!oldPass) {
      addToast('Current password is required.', 'warning');
      return;
    }
    if (newPass.length < 6) {
      addToast('New password must be at least 6 characters.', 'warning');
      return;
    }
    if (newPass !== confirmNewPass) {
      addToast('Passwords do not match.', 'error');
      return;
    }

    setModalLoading(true);
    try {
      const updated = await authService.updateProfile({ password: newPass });
      setProfile(updated);
      setIsPassOpen(false);
      setOldPass('');
      setNewPass('');
      setConfirmNewPass('');
      addToast('Password updated successfully!', 'success');
    } catch (err) {
      addToast(err.message || 'Failed to update password.', 'error');
    } finally {
      setModalLoading(false);
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4]">User Profile</h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Manage your credentials, bio, and review your accomplishments.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Card details */}
        <div className="lg:col-span-1 glass-card p-6 rounded-xl flex flex-col items-center text-center relative overflow-hidden">
          <div className="relative group mb-4">
            <img
              src={profile.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}
              alt={profile.name}
              className="w-24 h-24 rounded-2xl object-cover ring-4 ring-cyan-500/30 group-hover:ring-cyan-500 transition-all duration-200"
            />
          </div>

          <h2 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4]">{profile.name}</h2>
          <p className="text-xs text-slate-500">@{profile.username}</p>

          <p className="text-xs text-slate-600 dark:text-slate-400 mt-4 leading-relaxed italic max-w-xs">
            "{profile.bio || 'No biography written yet.'}"
          </p>

          <div className="w-full space-y-3.5 border-t border-slate-200 dark:border-[#292E33] pt-5 mt-5 text-left text-xs">
            <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-400">
              <Mail className="w-4 h-4 text-cyan-500 shrink-0" />
              <span className="truncate">{profile.email}</span>
            </div>
            <div className="flex items-center gap-2.5 text-slate-600 dark:text-slate-400">
              <GraduationCap className="w-4 h-4 text-cyan-500 shrink-0" />
              <span>{profile.college}</span>
            </div>
          </div>

          <div className="w-full grid grid-cols-2 gap-3 mt-6 pt-2">
            <button
              onClick={() => setIsEditOpen(true)}
              className="button-secondary text-xs py-2 px-3 flex items-center justify-center gap-1.5"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Profile</span>
            </button>
            <button
              onClick={() => setIsPassOpen(true)}
              className="button-secondary text-xs py-2 px-3 flex items-center justify-center gap-1.5"
            >
              <Key className="w-3.5 h-3.5" />
              <span>Password</span>
            </button>
          </div>
        </div>

        {/* Badges and skills lists */}
        <div className="lg:col-span-2 space-y-6">
          {/* Achievements Summary Row */}
          <div className="grid grid-cols-3 gap-4">
            <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total XP</span>
              <div className="inline-flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 font-heading font-extrabold text-xl">
                <Award className="w-5 h-5" />
                <span>{profile.totalScore}</span>
              </div>
            </div>
            <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Solved</span>
              <div className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-heading font-extrabold text-xl">
                <CheckCircle2 className="w-5 h-5" />
                <span>{profile.challengesSolved}</span>
              </div>
            </div>
            <div className="glass-card p-5 rounded-xl text-center space-y-1.5">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Current Streak</span>
              <div className="inline-flex items-center gap-1 text-amber-500 font-heading font-extrabold text-xl">
                <Flame className="w-5 h-5 fill-amber-500 text-amber-500" />
                <span>{profile.streak} Days</span>
              </div>
            </div>
          </div>

          {/* Badges Box */}
          <div className="glass-card p-6 rounded-xl">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4] mb-5">Earned Badges</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {profile.badges?.map((badge) => (
                <div key={badge.name} className="glass-panel p-4 rounded-lg border border-slate-200 dark:border-[#292E33] text-center space-y-2 group transition-all duration-200">
                  <div className="text-3xl text-gradient group-hover:scale-110 transition-transform">
                    {badge.icon}
                  </div>
                  <div>
                    <h4 className="font-heading font-bold text-xs text-slate-800 dark:text-[#F0F2F4]">{badge.name}</h4>
                    <p className="text-[10px] text-slate-500 mt-0.5 leading-relaxed">{badge.desc}</p>
                    <span className="text-[9px] text-cyan-600 dark:text-cyan-400 font-bold block mt-2">{badge.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Skills Breakdown */}
          <div className="glass-card p-6 rounded-xl space-y-5">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4]">Skills Profile</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
              {profile.skills && Object.entries(profile.skills).map(([skill, val]) => (
                <div key={skill} className="space-y-2">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-600 dark:text-slate-400">{skill}</span>
                    <span className="text-slate-800 dark:text-[#F0F2F4]">{val}%</span>
                  </div>
                  <ProgressBar value={val} max={100} color={skill === 'React' ? 'indigo' : skill === 'Django' ? 'emerald' : 'violet'} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* MODAL: Edit Profile */}
      {isEditOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 backdrop-blur-sm" onClick={() => setIsEditOpen(false)} />
          <div className="relative w-full max-w-md glass-panel rounded-xl p-6 border border-slate-200 dark:border-[#292E33] shadow-2xl z-10 animate-slide-up">
            <div className="flex justify-between items-center mb-5">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Edit Profile</h3>
              <button onClick={() => setIsEditOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Full Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">College / Institution</label>
                <input
                  type="text"
                  value={editCollege}
                  onChange={(e) => setEditCollege(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Avatar Image URL</label>
                <input
                  type="url"
                  value={editAvatar}
                  onChange={(e) => setEditAvatar(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Biography</label>
                <textarea
                  value={editBio}
                  onChange={(e) => setEditBio(e.target.value)}
                  rows="3"
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none resize-none"
                />
              </div>

              <div className="flex justify-end gap-3.5 pt-2">
                <button type="button" onClick={() => setIsEditOpen(false)} className="button-secondary text-xs py-2 px-4">
                  Cancel
                </button>
                <button type="submit" disabled={modalLoading} className="button-primary text-xs py-2 px-4">
                  {modalLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Save Changes</span>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Change Password */}
      {isPassOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/40 dark:bg-slate-950/70 backdrop-blur-sm" onClick={() => setIsPassOpen(false)} />
          <div className="relative w-full max-w-md glass-panel rounded-xl p-6 border border-slate-200 dark:border-[#292E33] shadow-2xl z-10 animate-slide-up">
            <div className="flex justify-between items-center mb-5">
              <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4]">Change Password</h3>
              <button onClick={() => setIsPassOpen(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handlePassSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Current Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={oldPass}
                  onChange={(e) => setOldPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">New Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={newPass}
                  onChange={(e) => setNewPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Confirm New Password</label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={confirmNewPass}
                  onChange={(e) => setConfirmNewPass(e.target.value)}
                  className="w-full bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] focus:border-cyan-500 text-slate-800 dark:text-[#F0F2F4] text-xs rounded-lg px-3 py-2 outline-none"
                  required
                />
              </div>

              <div className="flex justify-end gap-3.5 pt-2">
                <button type="button" onClick={() => setIsPassOpen(false)} className="button-secondary text-xs py-2 px-4">
                  Cancel
                </button>
                <button type="submit" disabled={modalLoading} className="button-primary text-xs py-2 px-4">
                  {modalLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Update Password</span>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
