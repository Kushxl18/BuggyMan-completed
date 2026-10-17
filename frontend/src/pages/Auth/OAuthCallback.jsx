import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Loader2, AlertCircle, CheckCircle2, ShieldCheck, ArrowRight, RefreshCw } from 'lucide-react';
import { authService } from '../../services/authService';

export const GoogleBrandIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} width="20" height="20" viewBox="0 0 24 24" style={{ minWidth: 20, minHeight: 20 }}>
    <path
      fill="#4285F4"
      d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
    />
    <path
      fill="#34A853"
      d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
    />
    <path
      fill="#FBBC05"
      d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.04 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
    />
    <path
      fill="#EA4335"
      d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
    />
  </svg>
);

export const GitHubBrandIcon = ({ className = 'w-5 h-5' }) => (
  <svg className={className} width="20" height="20" fill="currentColor" viewBox="0 0 24 24" style={{ minWidth: 20, minHeight: 20 }}>
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
    />
  </svg>
);

export default function OAuthCallback({ setUser, addToast }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [statusText, setStatusText] = useState('Verifying authentication credentials...');
  const [errorMsg, setErrorMsg] = useState(null);
  const [processing, setProcessing] = useState(true);
  const [success, setSuccess] = useState(false);
  const [detectedProvider, setDetectedProvider] = useState('provider');

  const processedRef = useRef(false);

  useEffect(() => {
    // Guard against React 18 strict mode double-invoking
    if (processedRef.current) return;
    processedRef.current = true;

    const exchangeCode = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      // Check for errors returned directly by OAuth provider (e.g. user cancelled)
      if (error) {
        setProcessing(false);
        const displayErr = errorDescription || error;
        setErrorMsg(displayErr);
        if (addToast) {
          addToast(`Sign-in was cancelled or denied: ${displayErr}`, 'error');
        }
        return;
      }

      if (!code) {
        setProcessing(false);
        setErrorMsg('No authorization code was found in the OAuth redirect URL.');
        if (addToast) {
          addToast('Authorization code missing. Please try signing in again.', 'error');
        }
        return;
      }

      // Determine provider from state parameter or sessionStorage
      let provider = '';
      if (state && state.includes(':')) {
        provider = state.split(':')[0].toLowerCase();
      }
      if (!provider) {
        provider = sessionStorage.getItem('buggyman_oauth_provider') || localStorage.getItem('buggyman_oauth_provider') || '';
      }
      if (!provider) {
        provider = 'google'; // sensible fallback
      }

      setDetectedProvider(provider);

      // Verify CSRF state if stored
      const savedState = sessionStorage.getItem('buggyman_oauth_state');
      if (savedState && state && savedState !== state) {
        console.warn('OAuth state mismatch warning. Proceeding with caution.');
      }

      const redirectUri = `${window.location.origin}/auth/callback`;
      setStatusText(`Exchanging credentials with ${provider.charAt(0).toUpperCase() + provider.slice(1)}...`);

      try {
        const response = await authService.handleOAuthCallback({
          provider,
          code,
          redirect_uri: redirectUri
        });

        setSuccess(true);
        setStatusText('Authentication successful! Launching your workspace...');

        if (typeof setUser === 'function' && response.user) {
          setUser(response.user);
        }

        const providerLabel = provider.charAt(0).toUpperCase() + provider.slice(1);
        if (addToast) {
          addToast(
            response.isNewUser
              ? `Welcome to BuggyMan! Your account was registered via ${providerLabel}.`
              : `Welcome back, ${response.user?.name || response.user?.username || 'Developer'}! Signed in via ${providerLabel}.`,
            'success'
          );
        }

        // Clean up session storage
        sessionStorage.removeItem('buggyman_oauth_provider');
        sessionStorage.removeItem('buggyman_oauth_state');

        // Smooth redirect: new users go to Onboarding, returning users go to Dashboard
        setTimeout(() => {
          const isNew = Boolean(response.isNewUser || !response.user?.onboarding_completed);
          if (isNew) {
            navigate('/onboarding', { replace: true });
          } else {
            navigate('/dashboard', { replace: true });
          }
        }, 1200);
      } catch (err) {
        setProcessing(false);
        const message = err?.message || 'Failed to complete OAuth authentication. Please check server configuration.';
        setErrorMsg(message);
        if (addToast) {
          addToast(message, 'error');
        }
      }
    };

    exchangeCode();
  }, [searchParams, navigate, setUser, addToast]);

  const renderIcon = () => {
    switch (detectedProvider) {
      case 'google':
        return <GoogleBrandIcon className="w-8 h-8" />;
      case 'github':
        return <GitHubBrandIcon className="w-8 h-8 text-white" />;
      default:
        return <ShieldCheck className="w-8 h-8 text-cyan-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative overflow-hidden select-none">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/80 border border-slate-800/80 rounded-2xl p-8 backdrop-blur-xl shadow-2xl relative z-10 text-center">
        {/* Brand Header */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-white text-lg shadow-lg shadow-cyan-500/20">
            B
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
            BuggyMan
          </span>
        </div>

        {/* Status card body */}
        {processing && !errorMsg && !success && (
          <div className="space-y-6 py-4">
            <div className="relative mx-auto w-16 h-16 flex items-center justify-center">
              <div className="absolute inset-0 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center shadow-inner">
                {renderIcon()}
              </div>
              <div className="absolute -inset-1 rounded-2xl border-2 border-cyan-400/30 border-t-cyan-400 animate-spin" />
            </div>

            <div>
              <h2 className="text-lg font-semibold text-slate-100 mb-1.5">Authenticating with SSO</h2>
              <p className="text-xs text-slate-400 max-w-xs mx-auto leading-relaxed">{statusText}</p>
            </div>

            <div className="flex items-center justify-center gap-2 text-[11px] text-slate-500">
              <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>TLS 1.3 / OAuth 2.0 Secure Handshake</span>
            </div>
          </div>
        )}

        {success && (
          <div className="space-y-6 py-4 animate-in fade-in zoom-in-95 duration-300">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <h2 className="text-lg font-semibold text-slate-100 mb-1.5">Connected Successfully</h2>
              <p className="text-xs text-emerald-400/90 max-w-xs mx-auto leading-relaxed">{statusText}</p>
            </div>

            <div className="w-full bg-slate-800/60 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-400 h-full w-full animate-pulse" />
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="space-y-6 py-2 animate-in fade-in duration-200 text-left">
            <div className="flex items-center gap-3 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300">
              <AlertCircle className="w-6 h-6 shrink-0 text-rose-400" />
              <div>
                <p className="text-xs font-semibold text-rose-200">OAuth Authentication Failed</p>
                <p className="text-[11px] text-rose-300/80 mt-0.5 break-words">{errorMsg}</p>
              </div>
            </div>

            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
              <p className="font-medium text-slate-300">Troubleshooting:</p>
              <ul className="list-disc list-inside space-y-0.5 text-slate-400 text-[10.5px]">
                <li>Verify your provider credentials (client ID & secret) in <code className="text-cyan-400">backend/.env</code>.</li>
                <li>Ensure the redirect URI matches <code className="text-cyan-400">{window.location.origin}/auth/callback</code> in your OAuth app console.</li>
              </ul>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <Link
                to="/login"
                className="flex-1 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium text-center transition-colors"
              >
                Back to Sign In
              </Link>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="py-2.5 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
