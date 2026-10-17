import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, Phone, KeyRound, User, Sparkles, Loader2, ArrowRight, ArrowLeft, CheckCircle2, Target, BookOpen, ShieldCheck } from 'lucide-react';
import { authService } from '../../services/authService';

const avatarOptions = [
  'https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=200',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
  'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200',
  'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200',
  'https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=200',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'
];

const SKILL_CATEGORIES = [
  'Backend',
  'SQL',
  'Frontend',
  'APIs',
  'Security',
  'Testing',
  'DevOps'
];

const interestOptions = [
  'Frontend Development',
  'Backend Development',
  'Full Stack Engineering',
  'Artificial Intelligence & ML',
  'Database & SQL Optimization',
  'Mobile App Development',
  'Cloud & DevOps',
  'Web Security & Debugging'
];

const themeOptions = ['dark', 'light', 'system'];

const countryTimezones = {
  'United States': 'America/New_York',
  'USA': 'America/New_York',
  'Canada': 'America/Toronto',
  'United Kingdom': 'Europe/London',
  'Germany': 'Europe/Berlin',
  'France': 'Europe/Paris',
  'Spain': 'Europe/Madrid',
  'Italy': 'Europe/Rome',
  'India': 'Asia/Kolkata',
  'Australia': 'Australia/Sydney',
  'Japan': 'Asia/Tokyo',
  'Brazil': 'America/Sao_Paulo',
  'Mexico': 'America/Mexico_City',
  'China': 'Asia/Shanghai',
  'Russia': 'Europe/Moscow',
  'South Africa': 'Africa/Johannesburg',
  'Nigeria': 'Africa/Lagos',
  'Netherlands': 'Europe/Amsterdam',
  'Sweden': 'Europe/Stockholm',
  'Switzerland': 'Europe/Zurich'
};

const countryList = Object.keys(countryTimezones).sort();

const inferTimezone = (country) => {
  const normalized = country.trim().toLowerCase();
  if (!normalized) return '';
  const exactMatch = Object.entries(countryTimezones).find(([key]) => key.toLowerCase() === normalized);
  if (exactMatch) {
    return exactMatch[1];
  }
  const prefixMatch = Object.entries(countryTimezones).find(([key]) => key.toLowerCase().startsWith(normalized));
  return prefixMatch ? prefixMatch[1] : '';
};

export default function Signup({ setUser, addToast }) {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [account, setAccount] = useState({ username: '', email: '', phone: '', password: '', confirmPassword: '', showPassword: false });
  const [profile, setProfile] = useState({ displayName: '', bio: '', country: '', timezone: '', avatar: '' });
  
  // OTP Verification State for Registration
  const [otpSent, setOtpSent] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [detectedOtpCode, setDetectedOtpCode] = useState('');
  const [otpVerified, setOtpVerified] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [personalization, setPersonalization] = useState({ 
    theme: 'dark', 
    accentColor: 'blue', 
    interests: [], 
    strengths: ['Backend', 'SQL'], 
    weaknesses: ['Frontend'], 
    notificationsConfig: { achievements: true, challenges: true, system: true } 
  });
  const [previewAvatar, setPreviewAvatar] = useState('');
  const [zoom, setZoom] = useState(1);

  const passwordStrength = useMemo(() => {
    const pwd = account.password;
    let score = 0;
    if (pwd.length >= 8) score += 1;
    if (/[A-Z]/.test(pwd)) score += 1;
    if (/[0-9]/.test(pwd)) score += 1;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 1;
    return score;
  }, [account.password]);

  const strengthLabel = ['Too weak', 'Fair', 'Good', 'Strong', 'Excellent'][passwordStrength];
  const strengthColor = ['bg-rose-500', 'bg-amber-500', 'bg-emerald-500', 'bg-sky-500', 'bg-fuchsia-500'][passwordStrength];

  const handleSendSignupOtp = async () => {
    setError('');
    const target = (account.email.trim() || account.phone.trim());
    if (!target) {
      setError('Please provide an email or phone number first to send verification code.');
      return;
    }
    setSendingOtp(true);
    try {
      const res = await authService.sendOtp(target, 'register');
      setOtpSent(true);
      if (res.otpCode) {
        setDetectedOtpCode(res.otpCode);
        setOtpCode(res.otpCode); // Pre-fill for frictionless instant verification
      }
      addToast(`OTP code sent to ${target}!`, 'success');
    } catch (err) {
      setError(err.message || 'Failed to send OTP code.');
      addToast('Could not send OTP.', 'error');
    } finally {
      setSendingOtp(false);
    }
  };

  const handleVerifySignupOtp = () => {
    if (!otpCode || otpCode.trim().length !== 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }
    setVerifyingOtp(true);
    setTimeout(() => {
      setOtpVerified(true);
      setVerifyingOtp(false);
      addToast('Email/Phone successfully verified! You can proceed.', 'success');
    }, 400);
  };

  const handleNext = async () => {
    setError('');
    if (step === 1) {
      if (!account.username.trim() || !account.email.trim() || !account.password || !account.confirmPassword) {
        setError('Please complete all account fields.');
        return;
      }
      if (account.password !== account.confirmPassword) {
        setError('Passwords must match.');
        return;
      }
      if (passwordStrength < 4) {
        setError('Choose a stronger password with uppercase, number, and special character.');
        return;
      }
      if (!account.email.includes('@')) {
        setError('Please enter a valid email address.');
        return;
      }

      setLoading(true);
      try {
        await authService.checkAvailability(account.username.trim(), account.email.trim());
      } catch (err) {
        setError(err.message || 'Username or email is already taken.');
        return;
      } finally {
        setLoading(false);
      }
    }
    if (step === 2 && !profile.displayName.trim()) {
      setError('Display name is required.');
      return;
    }
    setStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setError('');
    setStep((prev) => Math.max(1, prev - 1));
  };

  const handleRegister = async () => {
    setError('');
    setLoading(true);
    try {
      const payload = {
        username: account.username.trim(),
        email: account.email.trim(),
        phone: account.phone.trim(),
        password: account.password,
        displayName: profile.displayName.trim(),
        bio: profile.bio.trim(),
        country: profile.country.trim(),
        timezone: profile.timezone.trim(),
        avatar: previewAvatar || profile.avatar || avatarOptions[0],
        theme: personalization.theme,
        accentColor: personalization.accentColor,
        interests: personalization.interests,
        strengths: personalization.strengths,
        weaknesses: personalization.weaknesses,
        notificationsConfig: personalization.notificationsConfig
      };
      const response = await authService.register(payload);
      setUser(response.user);
      addToast('Welcome aboard! Your account has been created.', 'success');
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
      addToast('Registration failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewAvatar(reader.result);
      setProfile((prev) => ({ ...prev, avatar: reader.result }));
    };
    reader.readAsDataURL(file);
  };

  const toggleStrength = (skill) => {
    setPersonalization((prev) => {
      const selected = prev.strengths.includes(skill)
        ? prev.strengths.filter((s) => s !== skill)
        : [...prev.strengths, skill];
      return { ...prev, strengths: selected };
    });
  };

  const toggleWeakness = (skill) => {
    setPersonalization((prev) => {
      const selected = prev.weaknesses.includes(skill)
        ? prev.weaknesses.filter((w) => w !== skill)
        : [...prev.weaknesses, skill];
      return { ...prev, weaknesses: selected };
    });
  };

  const toggleInterest = (interest) => {
    setPersonalization((prev) => {
      const selected = prev.interests.includes(interest)
        ? prev.interests.filter((item) => item !== interest)
        : [...prev.interests, interest];
      return { ...prev, interests: selected };
    });
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-5xl bg-slate-900/95 border border-slate-800 rounded-[32px] shadow-2xl overflow-hidden backdrop-blur-xl">
        <div className="grid grid-cols-1 lg:grid-cols-[350px_1fr]">
          <div className="bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 p-8 text-slate-100">
            <div className="flex items-center gap-3 mb-6">
              <div className="rounded-3xl bg-slate-800/90 p-3 shadow-glow-blue">
                <Sparkles className="w-6 h-6 text-cyan-300" />
              </div>
              <div>
                <h2 className="font-heading text-xl font-bold">BuggyMan</h2>
                <p className="text-xs text-slate-400">Software Engineering Lab</p>
              </div>
            </div>

            <p className="text-sm text-slate-300 mb-8 leading-relaxed">
              Join BuggyMan to squash real software bugs, train with AI diagnostics, and climb leaderboards.
            </p>

            <div className="space-y-4 text-xs font-semibold text-slate-400">
              {['Account Details', 'Profile Info', 'Tell Us About Your Skills', 'Review & Confirm'].map((label, idx) => (
                <div key={label} className={`flex items-center gap-3 ${step === idx + 1 ? 'text-slate-100' : ''}`}>
                  <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs ${step === idx + 1 ? 'bg-cyan-500 text-slate-950 font-bold' : step > idx + 1 ? 'bg-slate-800 text-cyan-400' : 'bg-slate-900 text-slate-600'}`}>
                    {idx + 1}
                  </span>
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-8 lg:p-10 flex flex-col justify-between">
            {error && (
              <div className="mb-6 rounded-3xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-300">
                {error}
              </div>
            )}

            {step === 1 && (
              <div className="space-y-5">
                <div>
                  <h3 className="font-heading text-2xl font-bold text-slate-100">Create your account</h3>
                  <p className="text-xs text-slate-400 mt-1">Start your engineering debugging journey</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Username</label>
                    <div className="relative">
                      <User className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                      <input
                        type="text"
                        placeholder="kushalkumar"
                        value={account.username}
                        onChange={(e) => setAccount((prev) => ({ ...prev, username: e.target.value }))}
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950 py-3 pl-10 pr-4 text-sm text-slate-100 outline-none focus:border-cyan-400"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Email address</label>
                    <div className="relative">
                      <Mail className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                      <input
                        type="email"
                        placeholder="kushal@example.com"
                        value={account.email}
                        onChange={(e) => setAccount((prev) => ({ ...prev, email: e.target.value }))}
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950 py-3 pl-10 pr-4 text-sm text-slate-100 outline-none focus:border-cyan-400"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">
                      Mobile Number <span className="text-[10px] text-slate-500 lowercase">(optional for SMS verification)</span>
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                      <input
                        type="tel"
                        placeholder="+91 98765 43210"
                        value={account.phone}
                        onChange={(e) => setAccount((prev) => ({ ...prev, phone: e.target.value }))}
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950 py-3 pl-10 pr-4 text-sm text-slate-100 outline-none focus:border-cyan-400"
                      />
                    </div>
                  </div>

                  {/* OTP Verification Badge / Trigger */}
                  <div className="p-3.5 rounded-2xl border border-slate-800 bg-slate-950/70 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                        <ShieldCheck className="w-4 h-4 text-cyan-400" />
                        <span>Account Verification (OTP)</span>
                      </div>
                      {otpVerified ? (
                        <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Verified
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={handleSendSignupOtp}
                          disabled={sendingOtp || (!account.email.trim() && !account.phone.trim())}
                          className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 disabled:opacity-40"
                        >
                          {sendingOtp ? 'Sending...' : otpSent ? 'Resend OTP' : 'Send OTP Code'}
                        </button>
                      )}
                    </div>

                    {otpSent && !otpVerified && (
                      <div className="space-y-2 pt-1 animate-fade-in">
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <KeyRound className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                            <input
                              type="text"
                              maxLength={6}
                              placeholder="Enter 6-digit code"
                              value={otpCode}
                              onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                              className="w-full rounded-xl border border-slate-800 bg-slate-900 py-2 pl-9 pr-3 text-xs text-slate-100 outline-none focus:border-cyan-400 tracking-widest font-mono"
                            />
                          </div>
                          <button
                            type="button"
                            onClick={handleVerifySignupOtp}
                            disabled={verifyingOtp || otpCode.length !== 6}
                            className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs disabled:opacity-50 transition-colors"
                          >
                            {verifyingOtp ? 'Verifying...' : 'Verify'}
                          </button>
                        </div>
                        {detectedOtpCode && (
                          <div className="text-[11px] text-cyan-300 flex items-center justify-between">
                            <span>Code received: <strong className="font-mono">{detectedOtpCode}</strong></span>
                            <button
                              type="button"
                              onClick={() => setOtpCode(detectedOtpCode)}
                              className="underline hover:text-white"
                            >
                              Auto-fill
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                        <input
                          type={account.showPassword ? 'text' : 'password'}
                          placeholder="••••••••"
                          value={account.password}
                          onChange={(e) => setAccount((prev) => ({ ...prev, password: e.target.value }))}
                          className="w-full rounded-2xl border border-slate-800 bg-slate-950 py-3 pl-10 pr-10 text-sm text-slate-100 outline-none focus:border-cyan-400"
                          required
                        />
                        <button
                          type="button"
                          onClick={() => setAccount((prev) => ({ ...prev, showPassword: !prev.showPassword }))}
                          className="absolute right-3.5 top-3.5 text-slate-500 hover:text-slate-300"
                        >
                          {account.showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Confirm password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                        <input
                          type={account.showPassword ? 'text' : 'password'}
                          placeholder="••••••••"
                          value={account.confirmPassword}
                          onChange={(e) => setAccount((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                          className="w-full rounded-2xl border border-slate-800 bg-slate-950 py-3 pl-10 pr-4 text-sm text-slate-100 outline-none focus:border-cyan-400"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  {account.password && (
                    <div className="space-y-1.5 pt-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Strength: {strengthLabel}</span>
                        <span className="text-slate-500">{passwordStrength}/4</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                        <div className={`h-full transition-all duration-300 ${strengthColor}`} style={{ width: `${(passwordStrength / 4) * 100}%` }} />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-5">
                <div>
                  <h3 className="font-heading text-2xl font-bold text-slate-100">Personalize your profile</h3>
                  <p className="text-xs text-slate-400 mt-1">Let fellow engineers know who you are</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Display Name</label>
                    <input
                      type="text"
                      placeholder="Kushal Kumar"
                      value={profile.displayName}
                      onChange={(e) => setProfile((prev) => ({ ...prev, displayName: e.target.value }))}
                      className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Bio</label>
                    <textarea
                      rows={2}
                      placeholder="Software engineer passionate about building & debugging complex systems..."
                      value={profile.bio}
                      onChange={(e) => setProfile((prev) => ({ ...prev, bio: e.target.value }))}
                      className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400 resize-none"
                    />
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Country</label>
                      <input
                        type="text"
                        list="country-options"
                        placeholder="United States"
                        value={profile.country}
                        onChange={(e) => {
                          const val = e.target.value;
                          const tz = inferTimezone(val);
                          setProfile((prev) => ({ ...prev, country: val, timezone: tz || prev.timezone }));
                        }}
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
                      />
                      <datalist id="country-options">
                        {countryList.map((c) => (
                          <option key={c} value={c} />
                        ))}
                      </datalist>
                    </div>

                    <div>
                      <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-1.5 font-bold">Timezone</label>
                      <input
                        type="text"
                        placeholder="America/New_York"
                        value={profile.timezone}
                        onChange={(e) => setProfile((prev) => ({ ...prev, timezone: e.target.value }))}
                        className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs uppercase tracking-[0.2em] text-slate-400 mb-2 font-bold">Choose Avatar</label>
                    <div className="grid grid-cols-6 gap-2">
                      {avatarOptions.map((url) => (
                        <button
                          type="button"
                          key={url}
                          onClick={() => {
                            setPreviewAvatar('');
                            setProfile((prev) => ({ ...prev, avatar: url }));
                          }}
                          className={`h-12 rounded-2xl overflow-hidden border transition-all ${profile.avatar === url && !previewAvatar ? 'border-cyan-400 ring-2 ring-cyan-400/40' : 'border-slate-800 opacity-70 hover:opacity-100'}`}
                        >
                          <img src={url} alt="avatar" className="h-full w-full object-cover" />
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6">
                <div>
                  <h3 className="font-heading text-2xl font-bold text-slate-100">Tell us about your skills</h3>
                  <p className="text-xs text-slate-400 mt-1">Select your strengths and areas you want to improve to personalize recommendations</p>
                </div>

                {/* VISIBLE STRENGTHS SELECTION UI */}
                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Strengths (Select your strong skills)</span>
                    </p>
                    <span className="text-[10px] text-slate-500">{personalization.strengths.length} selected</span>
                  </div>
                  <div className="flex flex-wrap gap-2.5">
                    {SKILL_CATEGORIES.map((skill) => {
                      const isSelected = personalization.strengths.includes(skill);
                      return (
                        <button
                          key={`str-${skill}`}
                          type="button"
                          onClick={() => toggleStrength(skill)}
                          className={`px-4 py-2.5 rounded-2xl border text-xs font-semibold transition-all flex items-center gap-2 ${
                            isSelected
                              ? 'border-emerald-500 bg-emerald-500/20 text-emerald-200 shadow-glow-emerald/10'
                              : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                          }`}
                        >
                          <CheckCircle2 className={`w-4 h-4 ${isSelected ? 'text-emerald-400' : 'text-slate-600'}`} />
                          <span>{skill}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* VISIBLE WEAKNESSES / AREAS TO IMPROVE SELECTION UI */}
                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-rose-400 flex items-center gap-1.5">
                      <Target className="w-4 h-4 text-rose-400" />
                      <span>Areas you want to improve (Select target skills)</span>
                    </p>
                    <span className="text-[10px] text-slate-500">{personalization.weaknesses.length} selected</span>
                  </div>
                  <div className="flex flex-wrap gap-2.5">
                    {SKILL_CATEGORIES.map((skill) => {
                      const isSelected = personalization.weaknesses.includes(skill);
                      return (
                        <button
                          key={`wk-${skill}`}
                          type="button"
                          onClick={() => toggleWeakness(skill)}
                          className={`px-4 py-2.5 rounded-2xl border text-xs font-semibold transition-all flex items-center gap-2 ${
                            isSelected
                              ? 'border-rose-500 bg-rose-500/20 text-rose-200 shadow-glow-rose/10'
                              : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                          }`}
                        >
                          <Target className={`w-4 h-4 ${isSelected ? 'text-rose-400' : 'text-slate-600'}`} />
                          <span>{skill}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Theme Preference */}
                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-4 flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">UI Theme</span>
                  <select
                    value={personalization.theme}
                    onChange={(e) => setPersonalization((prev) => ({ ...prev, theme: e.target.value }))}
                    className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2 text-xs text-slate-100 outline-none focus:border-cyan-400"
                  >
                    {themeOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-5">
                <div>
                  <h3 className="font-heading text-2xl font-bold text-slate-100">Review & confirm</h3>
                  <p className="text-xs text-slate-400 mt-1">Verify your account profile before registering</p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-4">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">Account</p>
                    <p className="mt-2 text-slate-100 font-bold text-sm">{account.username}</p>
                    <p className="text-slate-400 text-xs mt-1">{account.email}</p>
                  </div>
                  <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-4">
                    <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold">Profile</p>
                    <p className="mt-2 text-slate-100 font-bold text-sm">{profile.displayName}</p>
                    <p className="text-slate-400 text-xs mt-1">{profile.country || 'Country'} • {profile.timezone || 'UTC'}</p>
                  </div>
                </div>

                {/* Selected Strengths & Weaknesses Confirmation Summary */}
                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5 space-y-3">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.2em] text-emerald-400 font-bold mb-1.5">Selected Strengths</p>
                    <div className="flex flex-wrap gap-1.5">
                      {personalization.strengths.map((s) => (
                        <span key={s} className="px-2.5 py-1 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[11px] font-semibold">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-[0.2em] text-rose-400 font-bold mb-1.5">Areas to Improve</p>
                    <div className="flex flex-wrap gap-1.5">
                      {personalization.weaknesses.map((w) => (
                        <span key={w} className="px-2.5 py-1 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[11px] font-semibold">
                          {w}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mt-8">
              <button
                type="button"
                onClick={handleBack}
                disabled={step === 1 || loading}
                className="button-secondary w-full sm:w-auto py-3 flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
              <div className="flex gap-3 w-full sm:w-auto">
                {step < 4 ? (
                  <button
                    type="button"
                    onClick={handleNext}
                    disabled={loading}
                    className="button-primary w-full sm:w-auto py-3 flex items-center justify-center gap-2"
                  >
                    <span>Continue</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleRegister}
                    disabled={loading}
                    className="button-primary w-full sm:w-auto py-3 flex items-center justify-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4.5 h-4.5 animate-spin" /> : <span>Create Account</span>}
                  </button>
                )}
              </div>
            </div>

            <div className="text-center mt-4 text-xs text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="text-cyan-400 hover:text-slate-100">Sign in</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
