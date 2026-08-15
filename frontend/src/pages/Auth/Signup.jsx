import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, User, Sparkles, Loader2, ArrowRight, ArrowLeft } from 'lucide-react';
import { authService } from '../../services/authService';

const avatarOptions = [
  'https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=200',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200',
  'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200',
  'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200',
  'https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=200',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'
];

const interestOptions = [
  'Bug Hunting',
  'Web Security',
  'CTF',
  'Reverse Engineering',
  'Malware',
  'Networking',
  'OSINT',
  'Programming'
];

const accentOptions = ['blue', 'purple', 'green', 'orange', 'red'];
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

  const [account, setAccount] = useState({ username: '', email: '', password: '', confirmPassword: '', showPassword: false });
  const [profile, setProfile] = useState({ displayName: '', bio: '', country: '', timezone: '', avatar: '' });
  const [personalization, setPersonalization] = useState({ theme: 'dark', accentColor: 'blue', interests: [], notificationsConfig: { achievements: true, challenges: true, system: true } });
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

  const handleNext = () => {
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
    }
    if (step === 2 && !profile.displayName.trim()) {
      setError('Display name is required.');
      return;
    }
    setStep(step + 1);
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
        password: account.password,
        displayName: profile.displayName.trim(),
        bio: profile.bio.trim(),
        country: profile.country.trim(),
        timezone: profile.timezone.trim(),
        avatar: previewAvatar || profile.avatar || avatarOptions[0],
        theme: personalization.theme,
        accentColor: personalization.accentColor,
        interests: personalization.interests,
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

  const toggleInterest = (interest) => {
    setPersonalization((prev) => {
      const selected = prev.interests.includes(interest)
        ? prev.interests.filter((item) => item !== interest)
        : [...prev.interests, interest];
      return { ...prev, interests: selected };
    });
  };

  const toggleNotification = (key) => {
    setPersonalization((prev) => ({
      ...prev,
      notificationsConfig: {
        ...prev.notificationsConfig,
        [key]: !prev.notificationsConfig[key]
      }
    }));
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
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Create your account</p>
                <h1 className="mt-3 text-3xl font-heading font-bold text-white">Buggyman Onboarding</h1>
              </div>
            </div>

            <p className="text-sm leading-relaxed text-slate-400 mb-8">A premium, animated signup experience with profile setup, theme personalization, and built-in avatar choices.</p>

            <div className="space-y-4">
              {['Account', 'Profile', 'Personalization', 'Finish'].map((label, index) => (
                <div key={label} className="flex items-center gap-4">
                  <div className={`h-10 w-10 rounded-full flex items-center justify-center text-xs font-bold ${step === index + 1 ? 'bg-cyan-400 text-slate-950' : 'bg-slate-800 text-slate-500'}`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Step {index + 1}</p>
                    <p className="font-semibold text-slate-100">{label}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-8 lg:p-10">
            <div className="flex items-center justify-between mb-8">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Step {step} of 4</p>
                <h2 className="mt-2 text-2xl font-heading font-bold text-slate-100">{step === 1 ? 'Account details' : step === 2 ? 'Profile setup' : step === 3 ? 'Personalize experience' : 'Finish & create account'}</h2>
              </div>
              <span className="text-xs text-slate-400">Your information is safe and encrypted.</span>
            </div>

            {error && (
              <div className="rounded-3xl bg-rose-500/10 border border-rose-500/20 text-rose-200 px-4 py-3 mb-6 text-sm">
                {error}
              </div>
            )}

            {step === 1 && (
              <div className="space-y-6">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Username</span>
                    <input
                      value={account.username}
                      onChange={(e) => setAccount((prev) => ({ ...prev, username: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="bugbuster"
                    />
                  </label>
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Email</span>
                    <input
                      type="email"
                      value={account.email}
                      onChange={(e) => setAccount((prev) => ({ ...prev, email: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="name@college.edu"
                    />
                  </label>
                </div>

                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Password</span>
                    <div className="relative mt-2">
                      <input
                        type={account.showPassword ? 'text' : 'password'}
                        value={account.password}
                        onChange={(e) => setAccount((prev) => ({ ...prev, password: e.target.value }))}
                        className="w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 pr-12 text-slate-100 outline-none focus:border-cyan-400"
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        onClick={() => setAccount((prev) => ({ ...prev, showPassword: !prev.showPassword }))}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500"
                      >
                        {account.showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </label>
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Confirm Password</span>
                    <input
                      type="password"
                      value={account.confirmPassword}
                      onChange={(e) => setAccount((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="••••••••"
                    />
                  </label>
                </div>

                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-4 grid gap-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 uppercase tracking-[0.24em]">
                    <span>Password strength</span>
                    <span className="font-semibold text-slate-100">{strengthLabel}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div className={`h-full ${strengthColor} transition-all`} style={{ width: `${(passwordStrength / 4) * 100}%` }} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-500">
                    <span className={account.password.length >= 8 ? 'text-slate-100' : ''}>8+ characters</span>
                    <span className={/[A-Z]/.test(account.password) ? 'text-slate-100' : ''}>Uppercase</span>
                    <span className={/[0-9]/.test(account.password) ? 'text-slate-100' : ''}>Number</span>
                    <span className={/[^A-Za-z0-9]/.test(account.password) ? 'text-slate-100' : ''}>Special char</span>
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-6">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Display Name</span>
                    <input
                      value={profile.displayName}
                      onChange={(e) => setProfile((prev) => ({ ...prev, displayName: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="Bug Hunter"
                    />
                  </label>
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Country</span>
                    <input
                      list="country-options"
                      value={profile.country}
                      onChange={(e) => {
                        const country = e.target.value;
                        const timezone = inferTimezone(country);
                        setProfile((prev) => ({ ...prev, country, timezone: timezone || prev.timezone }));
                      }}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="United States"
                    />
                    <datalist id="country-options">
                      {countryList.map((country) => (
                        <option key={country} value={country} />
                      ))}
                    </datalist>
                    <p className="mt-2 text-[11px] text-slate-500">Pick from the list or type your country name.</p>
                  </label>
                </div>

                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Time Zone</span>
                    <input
                      value={profile.timezone}
                      onChange={(e) => setProfile((prev) => ({ ...prev, timezone: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                      placeholder="America/New_York"
                    />
                    <p className="mt-2 text-[11px] text-slate-500">Automatically fills when country is selected.</p>
                  </label>
                  <label className="block text-sm text-slate-300 col-span-full">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Bio</span>
                    <textarea
                      value={profile.bio}
                      onChange={(e) => setProfile((prev) => ({ ...prev, bio: e.target.value }))}
                      className="mt-2 w-full min-h-[120px] rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400 resize-none"
                      placeholder="A short bio about your debugging superpowers."
                    />
                  </label>
                </div>

                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Avatar selection</p>
                      <p className="text-sm text-slate-400 mt-1">Upload your own image or choose from curated profile icons.</p>
                    </div>
                    <span className="text-[11px] text-slate-400">Zoom {Math.round(zoom * 100)}%</span>
                  </div>

                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
                    <div className="relative w-full lg:w-40 h-40 rounded-3xl overflow-hidden border border-slate-800 bg-slate-950">
                      <img
                        src={previewAvatar || profile.avatar || avatarOptions[0]}
                        alt="Avatar preview"
                        className="h-full w-full object-cover"
                        style={{ transform: `scale(${zoom})` }}
                      />
                    </div>
                    <div className="flex-1 space-y-4">
                      <label className="block text-sm text-slate-300">
                        <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Upload avatar</span>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleAvatarUpload}
                          className="mt-2 w-full text-slate-300"
                        />
                      </label>
                      <div>
                        <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Choose built-in avatar</span>
                        <div className="mt-3 grid grid-cols-3 gap-3">
                          {avatarOptions.map((url) => (
                            <button
                              type="button"
                              key={url}
                              onClick={() => {
                                setPreviewAvatar('');
                                setProfile((prev) => ({ ...prev, avatar: url }));
                              }}
                              className={`h-16 rounded-3xl overflow-hidden border ${profile.avatar === url && !previewAvatar ? 'border-cyan-400' : 'border-slate-800'}`}>
                              <img src={url} alt="avatar" className="h-full w-full object-cover" />
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xs text-slate-400 uppercase tracking-[0.24em]">Zoom</span>
                        <input
                          type="range"
                          min="1"
                          max="1.8"
                          step="0.05"
                          value={zoom}
                          onChange={(e) => setZoom(parseFloat(e.target.value))}
                          className="w-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-6">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Theme</span>
                    <select
                      value={personalization.theme}
                      onChange={(e) => setPersonalization((prev) => ({ ...prev, theme: e.target.value }))}
                      className="mt-2 w-full rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-400"
                    >
                      {themeOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block text-sm text-slate-300">
                    <span className="text-xs uppercase tracking-[0.3em] text-slate-500">Accent color</span>
                    <div className="mt-2 flex items-center gap-2">
                      {accentOptions.map((color) => (
                        <button
                          key={color}
                          type="button"
                          onClick={() => setPersonalization((prev) => ({ ...prev, accentColor: color }))}
                          className={`h-10 w-10 rounded-full border-2 ${personalization.accentColor === color ? 'border-white shadow-lg' : 'border-slate-800'}`}
                          style={{ backgroundColor: color === 'blue' ? '#2563eb' : color === 'purple' ? '#8b5cf6' : color === 'green' ? '#22c55e' : color === 'orange' ? '#f97316' : '#ef4444' }}
                        />
                      ))}
                    </div>
                  </label>
                </div>

                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500 mb-3">Interests</p>
                  <div className="grid grid-cols-2 gap-3">
                    {interestOptions.map((interest) => (
                      <button
                        key={interest}
                        type="button"
                        onClick={() => toggleInterest(interest)}
                        className={`rounded-3xl border px-4 py-3 text-left text-sm transition-all ${personalization.interests.includes(interest) ? 'border-cyan-400 bg-cyan-500/10 text-slate-100' : 'border-slate-800 bg-slate-950 text-slate-300 hover:border-slate-700'}`}>
                        {interest}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500 mb-3">Notification preferences</p>
                  <div className="grid gap-3 text-sm text-slate-300">
                    {Object.entries(personalization.notificationsConfig).map(([key, value]) => (
                      <label key={key} className="flex items-center gap-3 rounded-3xl border border-slate-800 bg-slate-950 px-4 py-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={() => toggleNotification(key)}
                          className="h-4 w-4 rounded border-slate-700 text-cyan-500 bg-slate-950"
                        />
                        <span className="capitalize">{key.replace('-', ' ')} notifications</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-6">
                <div className="grid gap-5 sm:grid-cols-2">
                  <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Account</p>
                    <p className="mt-3 text-slate-100 font-semibold">{account.username}</p>
                    <p className="text-slate-400 text-sm mt-2">{account.email}</p>
                  </div>
                  <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Profile</p>
                    <p className="mt-3 text-slate-100 font-semibold">{profile.displayName}</p>
                    <p className="text-slate-400 text-sm mt-2">{profile.country || 'Country'} • {profile.timezone || 'Time zone'}</p>
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-800 bg-slate-950/60 p-5">
                  <div className="flex items-center gap-4">
                    <div className="h-16 w-16 rounded-3xl overflow-hidden bg-slate-800">
                      <img src={previewAvatar || profile.avatar || avatarOptions[0]} alt="Profile" className="h-full w-full object-cover" />
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Theme / Accent</p>
                      <p className="mt-2 text-slate-100">{personalization.theme} / {personalization.accentColor}</p>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-slate-400">
                    {personalization.interests.slice(0, 4).map((interest) => (
                      <span key={interest} className="rounded-full border border-slate-700 px-3 py-1 bg-slate-950/80">{interest}</span>
                    ))}
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
              <Link to="/login" className="text-brand-indigo hover:text-slate-100">Sign in</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
