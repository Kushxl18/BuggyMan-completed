import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Shield, Key, CheckCircle2, Loader2 } from 'lucide-react';
import { authService } from '../../services/authService';

const stepLabels = ['Verify Email', 'Reset Password'];

export default function ForgotPassword({ addToast }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [sentOtp, setSentOtp] = useState('');
  const [error, setError] = useState('');

  const handleRequestCode = async (e) => {
    e.preventDefault();
    setError('');
    if (!email.trim()) {
      setError('Please enter your registered email.');
      return;
    }
    setLoading(true);
    try {
      const resp = await authService.forgotPasswordRequest(email.trim());
      setSentOtp(resp.otp || '');
      setStep(2);
      addToast('Verification code sent. Check your inbox.', 'success');
    } catch (err) {
      setError(err.message || 'Failed to send verification code.');
      addToast('Request failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    if (!otp.trim()) {
      setError('Verification code is required.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await authService.forgotPasswordReset(email.trim(), otp.trim(), password);
      addToast('Password reset successful. Please log in.', 'success');
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Failed to reset password.');
      addToast('Reset failed.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full bg-slate-900/95 border border-slate-800 rounded-3xl shadow-2xl backdrop-blur-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 via-indigo-700 to-slate-900 p-6 text-white">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6" />
            <div>
              <h1 className="text-xl font-heading font-bold">Forgot Password</h1>
              <p className="text-xs text-slate-200 mt-1">Recover access with a secure verification code.</p>
            </div>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-2 text-[11px] uppercase tracking-[0.24em] text-slate-300">
            {stepLabels.map((label, index) => (
              <div key={label} className={`rounded-2xl px-3 py-2 text-center ${step === index + 1 ? 'bg-white/15 font-bold text-white' : 'bg-white/5 text-slate-400'}`}>
                {label}
              </div>
            ))}
          </div>
        </div>

        <div className="p-8 space-y-6">
          {error && (
            <div className="rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-200 px-4 py-3 text-sm">
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleRequestCode} className="space-y-5">
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.2em] text-slate-400">Registered Email</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
                    <Mail className="w-4 h-4" />
                  </span>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@college.edu"
                    className="w-full pl-11 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl outline-none text-slate-100 placeholder:text-slate-600 focus:border-blue-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="button-primary w-full py-3 flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Send Verification Code</span>}
              </button>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-5">
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.2em] text-slate-400">Verification Code</label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="123456"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl outline-none text-slate-100 placeholder:text-slate-600"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.2em] text-slate-400">New Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl outline-none text-slate-100 placeholder:text-slate-600"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs uppercase tracking-[0.2em] text-slate-400">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl outline-none text-slate-100 placeholder:text-slate-600"
                />
              </div>
              {sentOtp && (
                <div className="rounded-2xl bg-slate-800/80 p-4 border border-slate-700 text-slate-300 text-sm">
                  <p>Sandbox OTP (visible for local testing):</p>
                  <p className="font-semibold text-slate-100">{sentOtp}</p>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="button-primary w-full py-3 flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <span>Reset Password</span>}
              </button>
            </form>
          )}

          <div className="text-center text-xs text-slate-500 space-y-2">
            <p>
              Remembered your password?{' '}
              <Link to="/login" className="text-brand-indigo hover:text-slate-100">Sign in</Link>
            </p>
            {step === 2 && (
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-slate-400 hover:text-slate-200 text-xs"
              >
                Go back to request a new code
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
