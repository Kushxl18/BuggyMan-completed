import React, { useState, useEffect } from 'react';
import { Loader2, ExternalLink, HelpCircle, X, ShieldAlert, KeyRound, Copy, Check } from 'lucide-react';
import { authService } from '../services/authService';

// Authentic Provider SVG Brand Icons with explicit pixel bounds to prevent layout explosions
export const GoogleIcon = ({ className = 'w-5 h-5 shrink-0' }) => (
  <svg
    className={className}
    width="20"
    height="20"
    viewBox="0 0 24 24"
    style={{ minWidth: 20, minHeight: 20, maxWidth: 20, maxHeight: 20 }}
  >
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

export const GitHubIcon = ({ className = 'w-5 h-5 shrink-0 text-white' }) => (
  <svg
    className={className}
    width="20"
    height="20"
    fill="currentColor"
    viewBox="0 0 24 24"
    style={{ minWidth: 20, minHeight: 20, maxWidth: 20, maxHeight: 20 }}
  >
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"
    />
  </svg>
);

const PROVIDER_METADATA = {
  google: {
    name: 'Google',
    docsUrl: 'https://console.cloud.google.com/apis/credentials',
    docGuide: 'Google Cloud Console -> APIs & Services -> Credentials -> Create OAuth Client ID',
    envKeys: ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
  },
  github: {
    name: 'GitHub',
    docsUrl: 'https://github.com/settings/developers',
    docGuide: 'GitHub -> Settings -> Developer Settings -> OAuth Apps -> New OAuth App',
    envKeys: ['GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET']
  }
};

export default function OAuthButtons({ setUser, addToast, rememberMe = true, subtitle = 'Or continue with email' }) {
  const [loadingProvider, setLoadingProvider] = useState(null);
  const [config, setConfig] = useState(null);
  const [setupModalProvider, setSetupModalProvider] = useState(null);
  const [copiedKey, setCopiedKey] = useState(null);

  // Fetch OAuth public config (registered client IDs, scopes, redirect URI)
  useEffect(() => {
    let isMounted = true;
    const fetchConfig = async () => {
      try {
        const data = await authService.getOAuthConfig();
        if (isMounted && data) {
          setConfig(data);
        }
      } catch (err) {
        console.warn('OAuth configuration endpoint unreachable; using client defaults', err);
      }
    };
    fetchConfig();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleOAuthClick = async (providerKey) => {
    setLoadingProvider(providerKey);

    try {
      // 1. Refresh or read latest config
      let currentConfig = config;
      if (!currentConfig) {
        try {
          currentConfig = await authService.getOAuthConfig();
          setConfig(currentConfig);
        } catch {
          // ignore error and proceed
        }
      }

      const providerInfo = currentConfig?.providers?.[providerKey];
      const redirectUri = `${window.location.origin}/auth/callback`;

      // 2. If client ID is NOT configured in .env, open the Setup Guide Modal
      if (!providerInfo || !providerInfo.clientId || !providerInfo.configured) {
        setLoadingProvider(null);
        setSetupModalProvider(providerKey);
        return;
      }

      // 3. Generate CSRF state token
      const stateToken = `${providerKey}:${Math.random().toString(36).substring(2)}${Date.now().toString(36)}`;
      sessionStorage.setItem('buggyman_oauth_provider', providerKey);
      sessionStorage.setItem('buggyman_oauth_state', stateToken);

      // 4. Construct production OAuth 2.0 Authorization URL
      let authUrl = '';
      if (providerKey === 'google') {
        const params = new URLSearchParams({
          client_id: providerInfo.clientId,
          redirect_uri: redirectUri,
          response_type: 'code',
          scope: providerInfo.scope || 'openid email profile',
          state: stateToken,
          access_type: 'offline',
          prompt: 'select_account'
        });
        authUrl = `${providerInfo.authUrl || 'https://accounts.google.com/o/oauth2/v2/auth'}?${params.toString()}`;
      } else if (providerKey === 'github') {
        const params = new URLSearchParams({
          client_id: providerInfo.clientId,
          redirect_uri: redirectUri,
          scope: providerInfo.scope || 'read:user user:email',
          state: stateToken
        });
        authUrl = `${providerInfo.authUrl || 'https://github.com/login/oauth/authorize'}?${params.toString()}`;
      }

      if (authUrl) {
        window.location.href = authUrl;
      } else {
        throw new Error('Unable to generate authorization URL');
      }
    } catch (err) {
      setLoadingProvider(null);
      if (addToast) {
        addToast(err?.message || 'Failed to initialize OAuth redirection', 'error');
      }
    }
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleSandboxSimulatedLogin = async (providerKey) => {
    setLoadingProvider(providerKey);
    try {
      const response = await authService.handleOAuthCallback({
        provider: providerKey,
        code: `sandbox_code_${Date.now()}`,
        redirect_uri: `${window.location.origin}/auth/callback`
      });

      if (typeof setUser === 'function' && response.user) {
        setUser(response.user);
      }

      const pName = providerKey.charAt(0).toUpperCase() + providerKey.slice(1);
      if (addToast) {
        addToast(`Signed in via ${pName} Developer Sandbox!`, 'success');
      }
      const isNew = Boolean(response.isNewUser || !response.user?.onboarding_completed);
      window.location.href = isNew ? '/onboarding' : '/dashboard';
    } catch (err) {
      if (addToast) {
        addToast(err?.message || 'Sandbox authentication error', 'error');
      }
    } finally {
      setLoadingProvider(null);
    }
  };

  const activeMeta = setupModalProvider ? PROVIDER_METADATA[setupModalProvider] : null;
  const redirectCallbackUrl = `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/auth/callback`;

  return (
    <div className="w-full space-y-4">
      {/* OAuth Provider Action Buttons (Google, GitHub) */}
      <div className="grid grid-cols-2 gap-2.5">
        {/* Google SSO Button */}
        <button
          type="button"
          onClick={() => handleOAuthClick('google')}
          disabled={loadingProvider !== null}
          className="h-10 px-3 flex items-center justify-center gap-2 rounded-xl border border-slate-800 bg-slate-900/70 hover:bg-slate-800 hover:border-slate-700 text-slate-200 text-xs font-semibold transition-all shadow-sm active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed group overflow-hidden"
          title="Sign in with Google"
        >
          {loadingProvider === 'google' ? (
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
          ) : (
            <GoogleIcon className="w-5 h-5 shrink-0 group-hover:scale-105 transition-transform" />
          )}
          <span className="hidden sm:inline truncate">Google</span>
        </button>

        {/* GitHub SSO Button */}
        <button
          type="button"
          onClick={() => handleOAuthClick('github')}
          disabled={loadingProvider !== null}
          className="h-10 px-3 flex items-center justify-center gap-2 rounded-xl border border-slate-800 bg-slate-900/70 hover:bg-slate-800 hover:border-slate-700 text-slate-200 text-xs font-semibold transition-all shadow-sm active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed group overflow-hidden"
          title="Sign in with GitHub"
        >
          {loadingProvider === 'github' ? (
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
          ) : (
            <GitHubIcon className="w-5 h-5 shrink-0 group-hover:scale-105 transition-transform" />
          )}
          <span className="hidden sm:inline truncate">GitHub</span>
        </button>
      </div>

      {/* Modern Divider */}
      <div className="relative flex items-center justify-center">
        <div className="border-t border-slate-800/80 w-full" />
        <span className="bg-slate-900/90 border border-slate-800/60 px-3 py-1 rounded-full text-[11px] font-medium text-slate-400 tracking-wide absolute uppercase">
          {subtitle}
        </span>
      </div>

      {/* Production OAuth Setup Modal (Displayed if credentials are unconfigured in .env) */}
      {setupModalProvider && activeMeta && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 relative space-y-5 animate-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-slate-800/90 border border-slate-700/60 flex items-center justify-center shrink-0">
                  {setupModalProvider === 'google' && <GoogleIcon className="w-5 h-5" />}
                  {setupModalProvider === 'github' && <GitHubIcon className="w-5 h-5" />}
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                    {activeMeta.name} OAuth Setup
                  </h3>
                  <p className="text-xs text-slate-400">Configure client credentials in your environment</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSetupModalProvider(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Guide Body */}
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs flex items-start gap-2.5">
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-amber-300">Live OAuth credentials missing in backend/.env</p>
                <p className="text-amber-200/80 text-[11px] mt-0.5 leading-relaxed">
                  To authenticate users directly with {activeMeta.name}, register an OAuth application and supply your Client ID & Secret in <code className="text-amber-300 bg-amber-950/40 px-1 py-0.5 rounded">backend/.env</code>.
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider block mb-1">
                  1. Authorized Redirect URI (register in {activeMeta.name})
                </span>
                <div className="flex items-center gap-2 bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                  <code className="text-cyan-400 font-mono text-[11px] flex-1 truncate">{redirectCallbackUrl}</code>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(redirectCallbackUrl, 'redirect')}
                    className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors shrink-0"
                    title="Copy redirect URI"
                  >
                    {copiedKey === 'redirect' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <span className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider block mb-1">
                  2. Add to backend/.env
                </span>
                <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1">
                  {activeMeta.envKeys.map((key) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-emerald-400">{key}=<span className="text-slate-500">&lt;your_{key.toLowerCase()}&gt;</span></span>
                      <button
                        type="button"
                        onClick={() => copyToClipboard(`${key}=`, key)}
                        className="p-0.5 text-slate-500 hover:text-slate-300"
                        title="Copy variable"
                      >
                        {copiedKey === key ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-2 flex flex-col sm:flex-row items-center gap-2">
              <a
                href={activeMeta.docsUrl}
                target="_blank"
                rel="noreferrer"
                className="w-full sm:flex-1 py-2 px-3 rounded-xl border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>Open {activeMeta.name} Console</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <button
                type="button"
                onClick={() => handleSandboxSimulatedLogin(setupModalProvider)}
                disabled={loadingProvider !== null}
                className="w-full sm:flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all shadow-md active:scale-95"
              >
                {loadingProvider ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <KeyRound className="w-3.5 h-3.5" />
                )}
                <span>Test via Dev Sandbox</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
