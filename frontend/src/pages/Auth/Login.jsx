import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, Phone, Loader2, Bug, KeyRound, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { authService } from '../../services/authService';

export default function Login({ setUser, addToast }) {
  const navigate = useNavigate();
  const [authMode, setAuthMode] = useState('password'); // 'password' | 'otp'
  
  // Password Mode state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  // OTP Mode state
  const [otpIdentifier, setOtpIdentifier] = useState('');
  const [otpStep, setOtpStep] = useState(1); // 1: enter email/phone, 2: enter 6-digit OTP
  const [otpCode, setOtpCode] = useState('');
  const [detectedOtpCode, setDetectedOtpCode] = useState('');
  const [countdown, setCountdown] = useState(0);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Password submission
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Email or username is required');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    try {
      const response = await authService.login(email, password, rememberMe);
      setUser(response.user);
      addToast('Login successful! Welcome back.', 'success');
      const isNew = Boolean(response.isNewUser || !response.user?.onboarding_completed);
      if (isNew) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Invalid credentials. Please try again.');
      addToast('Authentication failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Start countdown timer for OTP resend
  const startCountdown = () => {
    setCountdown(60);
    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Send OTP handler
  const handleSendOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');

    const target = otpIdentifier.trim();
    if (!target) {
      setError('Please enter your email or phone number.');
      return;
    }

    setLoading(true);
    try {
      const res = await authService.sendOtp(target, 'login');
      if (res.otpCode) {
        setDetectedOtpCode(res.otpCode);
        setOtpCode(res.otpCode); // Pre-fill for instant frictionless one-click verify!
      }
      setOtpStep(2);
      startCountdown();
      addToast(`Verification code sent to ${target}!`, 'success');
    } catch (err) {
      setError(err.message || 'Failed to send verification code. Please check details.');
      addToast('Failed to send OTP code.', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP handler
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError('');

    if (!otpCode.trim() || otpCode.trim().length !== 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    setLoading(true);
    try {
      const res = await authService.verifyOtpLogin(otpIdentifier.trim(), otpCode.trim(), rememberMe);
      if (res.token && res.user) {
        setUser(res.user);
        addToast('Verified successfully! Welcome to BuggyMan.', 'success');
        const isNew = Boolean(res.isNewUser || !res.user?.onboarding_completed);
        navigate(isNew ? '/onboarding' : '/dashboard');
      } else if (res.isNewUser) {
        addToast('Code verified! Complete your profile.', 'info');
        navigate('/register');
      }
    } catch (err) {
      setError(err.message || 'Invalid verification code. Please try again.');
      addToast('Invalid or expired code.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center relative px-4 bg-grid-pattern overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-indigo/10 blur-3xl rounded-full pointer-events-none" />

      <div className="w-full max-w-md relative z-10 py-8">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-brand-indigo to-brand-violet shadow-glow-indigo mb-4">
            <Bug className="w-8 h-8 text-white animate-pulse-glow" />
          </div>
          <h2 className="font-heading font-bold text-3xl text-slate-100">Welcome Back</h2>
          <p className="text-slate-400 text-sm mt-1.5">Sign in to continue solving challenges</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel rounded-2xl p-8 border border-slate-800 shadow-2xl space-y-6">
          {/* Auth Mode Toggle Tabs */}
          <div className="grid grid-cols-2 p-1 bg-slate-900/80 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => {
                setAuthMode('password');
                setError('');
              }}
              className={`py-2 px-3 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                authMode === 'password'
                  ? 'bg-gradient-to-r from-brand-indigo to-brand-violet text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Password</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setAuthMode('otp');
                setError('');
              }}
              className={`py-2 px-3 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                authMode === 'otp'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Email / Phone OTP</span>
            </button>
          </div>

          {error && (
            <div className="p-3.5 bg-rose-500/10 border border-brand-rose/25 text-brand-rose text-xs font-semibold rounded-xl animate-fade-in">
              {error}
            </div>
          )}

          {/* ================= MODE 1: PASSWORD LOGIN ================= */}
          {authMode === 'password' ? (
            <form onSubmit={handlePasswordSubmit} className="space-y-5">
              {/* Email/Username Field */}
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  College Email or Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                    <Mail className="w-4.5 h-4.5" />
                  </div>
                  <input
                    type="text"
                    placeholder="name@college.edu or username"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 focus:border-brand-indigo focus:ring-1 focus:ring-brand-indigo text-slate-100 rounded-xl outline-none transition-all placeholder:text-slate-600 text-sm"
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Password</label>
                  <Link
                    to="/forgot-password"
                    className="text-xs font-semibold text-brand-indigo hover:text-indigo-400 transition-colors"
                  >
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                    <Lock className="w-4.5 h-4.5" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-10 py-2.5 bg-slate-950/60 border border-slate-800 focus:border-brand-indigo focus:ring-1 focus:ring-brand-indigo text-slate-100 rounded-xl outline-none transition-all placeholder:text-slate-600 text-sm"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me Option */}
              <div className="flex items-center">
                <input
                  id="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-800 text-brand-indigo focus:ring-brand-indigo bg-slate-950 accent-brand-indigo"
                />
                <label htmlFor="remember-me" className="ml-2.5 text-xs font-semibold text-slate-400 cursor-pointer select-none">
                  Remember my login session
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="button-primary w-full py-3 font-semibold shadow-lg shadow-indigo-500/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4.5 h-4.5 animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <span>Log In</span>
                )}
              </button>
            </form>
          ) : (
            /* ================= MODE 2: OTP VERIFICATION LOGIN ================= */
            <div className="space-y-5 animate-fade-in">
              {otpStep === 1 ? (
                <form onSubmit={handleSendOtp} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Email or Mobile Number
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                        {otpIdentifier.includes('@') ? (
                          <Mail className="w-4.5 h-4.5 text-cyan-400" />
                        ) : (
                          <Phone className="w-4.5 h-4.5 text-cyan-400" />
                        )}
                      </div>
                      <input
                        type="text"
                        placeholder="you@email.com or +919876543210"
                        value={otpIdentifier}
                        onChange={(e) => setOtpIdentifier(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 text-slate-100 rounded-xl outline-none transition-all placeholder:text-slate-600 text-sm"
                      />
                    </div>
                    <p className="text-[11px] text-slate-500">
                      We'll send a 6-digit one-time code to verify your identity.
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !otpIdentifier.trim()}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4.5 h-4.5 animate-spin" />
                        <span>Sending OTP...</span>
                      </>
                    ) : (
                      <>
                        <span>Send Verification Code</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Enter 6-Digit OTP Code
                      </label>
                      <button
                        type="button"
                        onClick={() => setOtpStep(1)}
                        className="text-xs text-cyan-400 hover:underline"
                      >
                        Change
                      </button>
                    </div>

                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-cyan-400">
                        <KeyRound className="w-4.5 h-4.5" />
                      </div>
                      <input
                        type="text"
                        maxLength={6}
                        placeholder="123456"
                        value={otpCode}
                        onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                        className="w-full pl-10 pr-4 py-3 bg-slate-950/80 border border-cyan-500/40 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-slate-100 tracking-widest text-center text-lg font-mono rounded-xl outline-none"
                      />
                    </div>

                    {detectedOtpCode && (
                      <div className="p-2.5 rounded-lg bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-between text-xs text-cyan-300">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
                          <span>Code delivered: <strong className="font-mono text-cyan-200">{detectedOtpCode}</strong></span>
                        </div>
                        <button
                          type="button"
                          onClick={() => setOtpCode(detectedOtpCode)}
                          className="text-[11px] font-bold underline hover:text-white"
                        >
                          Auto-fill
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Sent to: <span className="text-slate-200">{otpIdentifier}</span></span>
                    {countdown > 0 ? (
                      <span className="text-slate-500">Resend in {countdown}s</span>
                    ) : (
                      <button
                        type="button"
                        onClick={handleSendOtp}
                        className="text-cyan-400 hover:text-cyan-300 font-semibold"
                      >
                        Resend Code
                      </button>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={loading || otpCode.length !== 6}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold flex items-center justify-center gap-2 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4.5 h-4.5 animate-spin" />
                        <span>Verifying...</span>
                      </>
                    ) : (
                      <>
                        <ShieldCheck className="w-4 h-4" />
                        <span>Verify & Sign In</span>
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          )}

          {/* Direct to Registration */}
          <div className="text-center mt-6 pt-6 border-t border-slate-800/80">
            <p className="text-xs text-slate-400 font-medium">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-brand-indigo hover:text-indigo-400 transition-colors">
                Create new account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
