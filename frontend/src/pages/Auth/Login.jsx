import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, User, Mail, KeyRound, Loader2, Bug, ShieldCheck, ArrowRight } from 'lucide-react';
import { authService } from '../../services/authService';
import { isValidEmail, getEmailValidationError } from '../../utils/validators';

export default function Login({ setUser, addToast }) {
  const navigate = useNavigate();
  const [authMode, setAuthMode] = useState('password'); // 'password' | 'otp'
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [devOtpHint, setDevOtpHint] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setInterval(() => {
        setResendCooldown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const trimmedIdentifier = identifier.trim();
    if (!trimmedIdentifier) {
      setError('Please enter your username or email');
      return;
    }

    if (trimmedIdentifier.includes('@')) {
      const emailErr = getEmailValidationError(trimmedIdentifier);
      if (emailErr) {
        setError(emailErr);
        return;
      }
    }
    if (!password) {
      setError('Please enter your password');
      return;
    }

    setLoading(true);
    try {
      const response = await authService.login(identifier.trim(), password, rememberMe);
      setUser(response.user);
      addToast('Login successful! Welcome back.', 'success');
      const isNew = Boolean(response.isNewUser || !response.user?.onboarding_completed);
      if (isNew) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Invalid username or password. Please try again.');
      addToast('Authentication failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSendOtp = async (e) => {
    if (e) e.preventDefault();
    setError('');
    const trimmedIdentifier = identifier.trim();
    if (!trimmedIdentifier) {
      setError('Please enter your email address');
      return;
    }
    if (trimmedIdentifier.includes('@')) {
      const emailErr = getEmailValidationError(trimmedIdentifier);
      if (emailErr) {
        setError(emailErr);
        return;
      }
    }

    setLoading(true);
    try {
      const res = await authService.sendOtp(trimmedIdentifier, 'login');
      setOtpSent(true);
      setResendCooldown(60);
      if (res?.otpCode) {
        setDevOtpHint(res.otpCode);
      }
      addToast(`Verification code sent to ${trimmedIdentifier}`, 'info');
    } catch (err) {
      setError(err.message || 'Failed to send verification code. Please check that your email is valid.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const cleanOtp = otp.trim();
    if (!cleanOtp || cleanOtp.length !== 6 || !/^\d{6}$/.test(cleanOtp)) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    setLoading(true);
    try {
      const response = await authService.verifyOtpLogin(identifier.trim(), cleanOtp, rememberMe);
      setUser(response.user);
      addToast('Authenticated with OTP successfully!', 'success');
      const isNew = Boolean(response.isNewUser || !response.user?.onboarding_completed);
      if (isNew) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Invalid or expired verification code.');
      addToast('OTP verification failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-main)] flex items-center justify-center relative px-4 bg-grid-pattern overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-indigo/10 blur-3xl rounded-full pointer-events-none" />

      <div className="w-full max-w-md relative z-10 py-8">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-brand-indigo to-brand-violet shadow-glow-indigo mb-4">
            <Bug className="w-8 h-8 text-white animate-pulse-glow" />
          </div>
          <h2 className="font-heading font-bold text-3xl text-[var(--text-primary)]">Welcome Back</h2>
          <p className="text-[var(--text-secondary)] text-sm mt-1.5">Sign in to your BuggyMan account</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel rounded-2xl p-8 border border-[var(--border-color)] shadow-2xl space-y-6">
          {/* Mode Switcher preserved for future activation
          <div className="grid grid-cols-2 p-1 rounded-2xl bg-[var(--bg-main)] border border-[var(--border-color)] text-xs font-semibold">
            <button
              type="button"
              onClick={() => { setAuthMode('password'); setError(''); }}
              className={`py-2.5 rounded-xl transition-all ${authMode === 'password' ? 'bg-[var(--brand-cyan)] text-white shadow-md' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}`}
            >
              Password Login
            </button>
            <button
              type="button"
              onClick={() => { setAuthMode('otp'); setError(''); }}
              className={`py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5 ${authMode === 'otp' ? 'bg-[var(--brand-cyan)] text-white font-bold shadow-md' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}`}
            >
              <KeyRound className="w-3.5 h-3.5" />
              <span>Email OTP Login</span>
            </button>
          </div>
          */}

          {error && (
            <div className="p-3.5 bg-rose-500/10 border border-brand-rose/25 text-brand-rose text-xs font-semibold rounded-xl animate-fade-in">
              {error}
            </div>
          )}

          {authMode === 'password' ? (
            <form onSubmit={handlePasswordSubmit} className="space-y-5">
              {/* Username / Email Field */}
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                  Username or Email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[var(--text-muted)]">
                    <User className="w-4.5 h-4.5" />
                  </div>
                  <input
                    type="text"
                    placeholder="Enter your username or email"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-[var(--bg-main)] border border-[var(--border-color)] focus:border-[var(--brand-cyan)] focus:ring-1 focus:ring-[var(--brand-cyan-bg)] text-[var(--text-primary)] rounded-xl outline-none transition-all placeholder:text-[var(--text-muted)] text-sm"
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                    Password
                  </label>
                  <Link
                    to="/forgot-password"
                    className="text-xs font-semibold text-[var(--brand-cyan)] hover:text-[var(--brand-cyan-hover)] transition-colors"
                  >
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[var(--text-muted)]">
                    <Lock className="w-4.5 h-4.5" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-10 py-3 bg-[var(--bg-main)] border border-[var(--border-color)] focus:border-[var(--brand-cyan)] focus:ring-1 focus:ring-[var(--brand-cyan-bg)] text-[var(--text-primary)] rounded-xl outline-none transition-all placeholder:text-[var(--text-muted)] text-sm"
                    autoComplete="current-password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
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
                  className="w-4 h-4 rounded border-[var(--border-color)] text-[var(--brand-cyan)] focus:ring-[var(--brand-cyan)] bg-[var(--bg-main)] accent-[var(--brand-cyan)]"
                />
                <label htmlFor="remember-me" className="ml-2.5 text-xs font-semibold text-[var(--text-secondary)] cursor-pointer select-none">
                  Remember my login session
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="button-primary w-full py-3.5 font-semibold shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4.5 h-4.5 animate-spin" />
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In with Password</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          ) : (
            /* Email OTP Login Mode */
            <form onSubmit={otpSent ? handleOtpSubmit : handleSendOtp} className="space-y-5">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                    Email Address
                  </label>
                  {otpSent && (
                    <button
                      type="button"
                      onClick={() => { setOtpSent(false); setOtp(''); }}
                      className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                    >
                      Change Email
                    </button>
                  )}
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[var(--text-muted)]">
                    <Mail className="w-4.5 h-4.5" />
                  </div>
                  <input
                    type="email"
                    placeholder="Enter your email address"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    disabled={otpSent}
                    className="w-full pl-10 pr-4 py-3 bg-[var(--bg-main)] border border-[var(--border-color)] focus:border-[var(--brand-cyan)] focus:ring-1 focus:ring-[var(--brand-cyan-bg)] text-[var(--text-primary)] rounded-xl outline-none transition-all placeholder:text-[var(--text-muted)] text-sm disabled:opacity-60"
                    required
                  />
                </div>
              </div>

              {otpSent && (
                <div className="space-y-3">
                  <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                    6-Digit Verification Code
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[var(--text-muted)]">
                      <KeyRound className="w-4.5 h-4.5 text-cyan-400" />
                    </div>
                    <input
                      type="text"
                      inputMode="numeric"
                      maxLength={6}
                      placeholder="••••••"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))}
                      className="w-full pl-10 pr-4 py-3 text-center font-mono text-lg tracking-[0.4em] bg-[var(--bg-main)] border border-[var(--brand-cyan)] focus:border-[var(--brand-cyan)] text-[var(--brand-cyan)] rounded-xl outline-none"
                      autoFocus
                      required
                    />
                  </div>



                  <div className="flex items-center justify-between text-xs pt-1">
                    <span className="text-[var(--text-secondary)]">Didn't receive the email code?</span>
                    {resendCooldown > 0 ? (
                      <span className="text-[var(--text-muted)] font-mono">Resend in {resendCooldown}s</span>
                    ) : (
                      <button
                        type="button"
                        onClick={handleSendOtp}
                        disabled={loading}
                        className="text-cyan-400 hover:text-cyan-300 font-semibold"
                      >
                        Resend Code
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Submit / Action Button */}
              {!otpSent ? (
                <button
                  type="submit"
                  disabled={loading}
                  className="button-primary w-full py-3.5 font-semibold bg-[var(--brand-cyan)] hover:bg-[var(--brand-cyan-hover)] text-white flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4.5 h-4.5 animate-spin" />
                      <span>Sending Verification Code...</span>
                    </>
                  ) : (
                    <>
                      <span>Send 6-Digit Verification Code</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading || otp.trim().length !== 6}
                  className="button-primary w-full py-3.5 font-semibold bg-[var(--brand-cyan)] hover:bg-[var(--brand-cyan-hover)] text-white flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4.5 h-4.5 animate-spin" />
                      <span>Verifying & Signing In...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck className="w-4.5 h-4.5" />
                      <span>Verify & Sign In</span>
                    </>
                  )}
                </button>
              )}
            </form>
          )}

          {/* Direct to Registration */}
          <div className="text-center mt-6 pt-6 border-t border-[var(--border-color)]">
            <p className="text-xs text-[var(--text-secondary)] font-medium">
              Don't have an account?{' '}
              <Link to="/register" className="font-semibold text-[var(--brand-cyan)] hover:text-[var(--brand-cyan-hover)] transition-colors">
                Create new account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
