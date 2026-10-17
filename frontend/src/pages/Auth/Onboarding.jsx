import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Target,
  Brain,
  ShieldAlert,
  Loader2,
  GraduationCap,
  Palette,
  Check,
  Compass
} from 'lucide-react';
import { authService } from '../../services/authService';

const AVATAR_OPTIONS = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150',
  'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150',
  'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150'
];

const SKILL_CATEGORIES = [
  'Backend',
  'SQL',
  'Frontend',
  'APIs',
  'Security',
  'Testing',
  'DevOps',
  'Algorithms'
];

const INTEREST_OPTIONS = [
  'Frontend Development',
  'Backend Systems & Microservices',
  'Database Optimization & SQL',
  'Artificial Intelligence & ML',
  'Application Security & Pentesting',
  'Cloud Architecture & DevOps',
  'Mobile Engineering',
  'Open Source & Tooling'
];

const ACCENT_COLORS = [
  { name: 'blue', label: 'Cyan / Blue', bg: 'bg-cyan-500' },
  { name: 'purple', label: 'Purple / Violet', bg: 'bg-purple-500' },
  { name: 'emerald', label: 'Emerald Green', bg: 'bg-emerald-500' },
  { name: 'amber', label: 'Amber Gold', bg: 'bg-amber-500' }
];

export default function Onboarding({ user, setUser, addToast }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form State initialized with any existing user data
  const [formData, setFormData] = useState({
    displayName: user?.name || user?.display_name || user?.username || '',
    college: user?.college || '',
    bio: user?.bio || '',
    avatar: user?.avatar || AVATAR_OPTIONS[0],
    country: user?.country || 'United States',
    strengths: user?.strengths && user.strengths.length > 0 ? user.strengths : ['Backend', 'SQL'],
    weaknesses: user?.weaknesses && user.weaknesses.length > 0 ? user.weaknesses : ['Frontend'],
    interests: user?.interests && user.interests.length > 0 ? user.interests : ['Backend Systems & Microservices', 'Database Optimization & SQL'],
    theme: user?.theme || 'dark',
    accentColor: user?.accent_color || 'blue'
  });

  const toggleStrength = (skill) => {
    setFormData((prev) => {
      const exists = prev.strengths.includes(skill);
      const updated = exists ? prev.strengths.filter((s) => s !== skill) : [...prev.strengths, skill];
      // Automatically remove from weaknesses if selected as strength
      const cleanWeaknesses = prev.weaknesses.filter((w) => w !== skill);
      return { ...prev, strengths: updated, weaknesses: cleanWeaknesses };
    });
  };

  const toggleWeakness = (skill) => {
    setFormData((prev) => {
      const exists = prev.weaknesses.includes(skill);
      const updated = exists ? prev.weaknesses.filter((w) => w !== skill) : [...prev.weaknesses, skill];
      // Automatically remove from strengths if selected as weakness
      const cleanStrengths = prev.strengths.filter((s) => s !== skill);
      return { ...prev, weaknesses: updated, strengths: cleanStrengths };
    });
  };

  const toggleInterest = (interest) => {
    setFormData((prev) => {
      const exists = prev.interests.includes(interest);
      const updated = exists ? prev.interests.filter((i) => i !== interest) : [...prev.interests, interest];
      return { ...prev, interests: updated };
    });
  };

  const handleFinishOnboarding = async (skipAll = false) => {
    setLoading(true);
    try {
      const payload = skipAll
        ? {
            onboarding_completed: true,
            display_name: formData.displayName || user?.username || 'Developer',
            strengths: ['Backend', 'SQL'],
            weaknesses: ['Frontend'],
            interests: ['Backend Systems & Microservices']
          }
        : {
            display_name: formData.displayName.trim() || user?.username || 'Developer',
            college: formData.college.trim() || 'Tech Institute',
            bio: formData.bio.trim() || 'Software Engineer and bug hunter on BuggyMan.',
            avatar: formData.avatar,
            country: formData.country,
            strengths: formData.strengths,
            weaknesses: formData.weaknesses,
            interests: formData.interests,
            theme: formData.theme,
            accent_color: formData.accentColor,
            onboarding_completed: true
          };

      const updatedUser = await authService.updateProfile(payload);

      if (typeof setUser === 'function') {
        setUser(updatedUser);
      }

      if (addToast) {
        addToast(
          skipAll
            ? 'Welcome to BuggyMan! You can complete your skill profile anytime in Settings.'
            : 'Profile setup complete! Welcome to BuggyMan Workspace.',
          'success'
        );
      }

      navigate('/dashboard', { replace: true });
    } catch (err) {
      if (addToast) {
        addToast(err?.message || 'Failed to save onboarding profile. Please try again.', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 sm:p-6 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Outer Card */}
      <div className="w-full max-w-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl p-6 sm:p-8 relative z-10 flex flex-col">
        {/* Header Navigation & Step Indicator */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-5 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-cyan-500/20">
              B
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-100">Welcome to BuggyMan</h1>
              <p className="text-xs text-slate-400">Let's personalize your debugging experience (Step {step} of 3)</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => handleFinishOnboarding(true)}
            disabled={loading}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors underline underline-offset-4"
          >
            Skip for now
          </button>
        </div>

        {/* Step Progress Pill */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          <div className={`h-1.5 rounded-full transition-all duration-300 ${step >= 1 ? 'bg-cyan-500' : 'bg-slate-800'}`} />
          <div className={`h-1.5 rounded-full transition-all duration-300 ${step >= 2 ? 'bg-cyan-500' : 'bg-slate-800'}`} />
          <div className={`h-1.5 rounded-full transition-all duration-300 ${step >= 3 ? 'bg-cyan-500' : 'bg-slate-800'}`} />
        </div>

        {/* ================================================================== */}
        {/* STEP 1: Basic Profile (Display Name, College, Avatar)              */}
        {/* ================================================================== */}
        {step === 1 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-cyan-400" />
                Tell us about yourself
              </h2>
              <p className="text-xs text-slate-400 mt-1">This information will be displayed on the leaderboards and PvP matches.</p>
            </div>

            {/* Display Name & College */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Display Name</label>
                <input
                  type="text"
                  placeholder="e.g. Alex Rivera"
                  value={formData.displayName}
                  onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">College / Institution</label>
                <input
                  type="text"
                  placeholder="e.g. Stanford University"
                  value={formData.college}
                  onChange={(e) => setFormData({ ...formData, college: e.target.value })}
                  className="w-full px-3.5 py-2.5 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            {/* Avatar Selection */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Choose an Avatar</label>
              <div className="flex flex-wrap items-center gap-3">
                {AVATAR_OPTIONS.map((imgUrl, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setFormData({ ...formData, avatar: imgUrl })}
                    className={`relative rounded-2xl p-1 transition-all ${
                      formData.avatar === imgUrl ? 'ring-2 ring-cyan-400 scale-105' : 'opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={imgUrl} alt="Avatar Option" className="w-12 h-12 rounded-xl object-cover" />
                    {formData.avatar === imgUrl && (
                      <div className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-cyan-500 rounded-full flex items-center justify-center text-slate-950">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Bio */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Short Bio</label>
              <textarea
                rows={2}
                placeholder="Software engineer eager to master debugging algorithms and database performance."
                value={formData.bio}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                className="w-full px-3.5 py-2 bg-slate-950/70 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-500 transition-colors resize-none"
              />
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* STEP 2: Skill Profiler (Strengths & Weaknesses)                    */}
        {/* ================================================================== */}
        {step === 2 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Brain className="w-5 h-5 text-cyan-400" />
                Customize Your Skill Profile
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                BuggyMan's AI Challenge Generator uses these tags to recommend debugging bugs tailored to your level.
              </p>
            </div>

            {/* Strengths */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Your Strengths (Areas you feel confident in)
                </label>
                <span className="text-[11px] text-slate-500">{formData.strengths.length} selected</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {SKILL_CATEGORIES.map((cat) => {
                  const isSelected = formData.strengths.includes(cat);
                  return (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => toggleStrength(cat)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                        isSelected
                          ? 'bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 shadow-sm'
                          : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                      }`}
                    >
                      {cat}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Weaknesses */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-amber-400 flex items-center gap-1.5 uppercase tracking-wider">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  Areas to Improve (We'll provide more practice hints here)
                </label>
                <span className="text-[11px] text-slate-500">{formData.weaknesses.length} selected</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {SKILL_CATEGORIES.map((cat) => {
                  const isSelected = formData.weaknesses.includes(cat);
                  return (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => toggleWeakness(cat)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                        isSelected
                          ? 'bg-amber-500/20 border border-amber-500/40 text-amber-300 shadow-sm'
                          : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                      }`}
                    >
                      {cat}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* STEP 3: Interests & Workspace Customization                        */}
        {/* ================================================================== */}
        {step === 3 && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div>
              <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                <Compass className="w-5 h-5 text-cyan-400" />
                Interests & Workspace Preferences
              </h2>
              <p className="text-xs text-slate-400 mt-1">Select the topics and tracks you are interested in exploring.</p>
            </div>

            {/* Interests Grid */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Focus Tracks</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {INTEREST_OPTIONS.map((interest) => {
                  const isSelected = formData.interests.includes(interest);
                  return (
                    <button
                      key={interest}
                      type="button"
                      onClick={() => toggleInterest(interest)}
                      className={`p-2.5 rounded-xl text-xs font-medium text-left flex items-center justify-between border transition-all ${
                        isSelected
                          ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-200'
                          : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <span className="truncate">{interest}</span>
                      {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Accent Color Selection */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Palette className="w-3.5 h-3.5 text-cyan-400" />
                Workspace Accent Color
              </label>
              <div className="flex items-center gap-3">
                {ACCENT_COLORS.map((acc) => (
                  <button
                    key={acc.name}
                    type="button"
                    onClick={() => setFormData({ ...formData, accentColor: acc.name })}
                    className={`flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-medium transition-all ${
                      formData.accentColor === acc.name
                        ? 'border-slate-600 bg-slate-800 text-slate-100'
                        : 'border-slate-800/80 bg-slate-950 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <span className={`w-3.5 h-3.5 rounded-full ${acc.bg}`} />
                    <span>{acc.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="mt-8 pt-5 border-t border-slate-800/80 flex items-center justify-between">
          {step > 1 ? (
            <button
              type="button"
              onClick={() => setStep((prev) => prev - 1)}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              type="button"
              onClick={() => setStep((prev) => prev + 1)}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold flex items-center gap-1.5 transition-all shadow-md active:scale-95 ml-auto"
            >
              <span>Continue</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => handleFinishOnboarding(false)}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold flex items-center gap-2 transition-all shadow-lg shadow-cyan-500/20 active:scale-95 ml-auto disabled:opacity-60"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Launching Workspace...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Complete Setup & Enter Workspace</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
