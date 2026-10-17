import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, Loader2, Bug } from 'lucide-react';
import { authService } from '../../services/authService';
import OAuthButtons from '../../components/OAuthButtons';

export default function Login({ setUser, addToast }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateForm = () => {
    if (!email.trim()) {
      setError('Email or username is required');
      return false;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

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

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center relative px-4 bg-grid-pattern overflow-hidden">
      {/* Glow Effect */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-indigo/10 blur-3xl rounded-full pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-brand-indigo to-brand-violet shadow-glow-indigo mb-4">
            <Bug className="w-8 h-8 text-white animate-pulse-glow" />
          </div>
          <h2 className="font-heading font-bold text-3xl text-slate-100">Welcome Back</h2>
          <p className="text-slate-400 text-sm mt-1.5">Log in to continue solving challenges</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel rounded-2xl p-8 border border-slate-800 shadow-2xl space-y-6">
          {/* SSO OAuth Buttons (Google, GitHub) */}
          <OAuthButtons
            setUser={setUser}
            addToast={addToast}
            rememberMe={rememberMe}
            subtitle="Or sign in with email"
          />

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="p-3.5 bg-rose-500/10 border border-brand-rose/25 text-brand-rose text-xs font-semibold rounded-xl animate-fade-in">
                {error}
              </div>
            )}

            {/* Email/Username Field */}
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-400">College Email or Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4.5 h-4.5" />
                </div>
                <input
                  type="text"
                  placeholder="name@college.edu or username"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 focus:border-brand-indigo focus:ring-1 focus:ring-brand-indigo text-slate-100 rounded-xl outline-none transition-all placeholder:text-slate-600"
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
                  className="w-full pl-10 pr-10 py-2.5 bg-slate-950/60 border border-slate-800 focus:border-brand-indigo focus:ring-1 focus:ring-brand-indigo text-slate-100 rounded-xl outline-none transition-all placeholder:text-slate-600"
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
              className="button-primary w-full py-3"
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
