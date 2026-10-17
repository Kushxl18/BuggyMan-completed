import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Toast from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';

// Auth Pages
import Login from './pages/Auth/Login';
import Signup from './pages/Auth/Signup';
import ForgotPassword from './pages/Auth/ForgotPassword';
import OAuthCallback from './pages/Auth/OAuthCallback';
import Onboarding from './pages/Auth/Onboarding';

// Core Pages
import Dashboard from './pages/Dashboard';
import ChallengeSelection from './pages/ChallengeSelection';
import SQLChallenges from './pages/SQLChallenges';
import FrontendDesignChallenges from './pages/FrontendDesignChallenges';
import EditorPage from './pages/Challenge/EditorPage';

import ResultPage from './pages/ResultPage';
import Leaderboard from './pages/Leaderboard';
import UserProfile from './pages/UserProfile';
import CareerInsights from './pages/CareerInsights';
import BugBytesStore from './pages/BugBytesStore';
import AdminDashboard from './pages/AdminDashboard';
import Settings from './pages/Settings';
import PvPBattle from './pages/PvPBattle';
import PvPArena from './pages/PvPArena';

import { authService } from './services/authService';

export default function App() {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('buggyman_theme') || 'dark';
  });
  const [toasts, setToasts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Settings state
  const [settings, setSettings] = useState({
    fontSize: 14,
    autoSave: true,
    language: 'JavaScript',
    notifications: {
      achievements: true,
      challenges: true,
      system: true
    }
  });

  // Notifications state
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Achievement Unlocked', message: 'You have earned the "Five Day Streak" badge! Keep it up.', type: 'achievement', read: false, time: '2 hours ago' },
    { id: 2, title: 'New Challenge Out', message: 'A new React custom hook challenge is now available: "Fix useFetch Hook".', type: 'challenge', read: false, time: '5 hours ago' },
    { id: 3, title: 'Weekly Leaderboard Updated', message: 'See your placement on the global weekly rankings.', type: 'system', read: true, time: '1 day ago' }
  ]);

  // Load active session
  useEffect(() => {
    async function loadSession() {
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      if (token) {
        try {
          const u = await authService.getCurrentUser();
          setUser(u);
          if (u?.theme) {
            setTheme(u.theme);
          }
        } catch (err) {
          localStorage.removeItem('token');
          sessionStorage.removeItem('token');
        }
      }
      setLoading(false);
    }
    loadSession();
  }, []);

  // Sync theme when user logs in, registers, or changes profile
  useEffect(() => {
    if (user?.theme) {
      setTheme(user.theme);
      localStorage.setItem('buggyman_theme', user.theme);
    }
  }, [user]);

  // Theme change sync supporting 'dark', 'light', and 'system'
  useEffect(() => {
    const root = window.document.documentElement;
    localStorage.setItem('buggyman_theme', theme);

    const applyTheme = (targetTheme) => {
      let isDark = false;
      if (targetTheme === 'dark') {
        isDark = true;
      } else if (targetTheme === 'light') {
        isDark = false;
      } else if (targetTheme === 'system') {
        isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      }

      if (isDark) {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    };

    applyTheme(theme);

    if (theme === 'system' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e) => {
        if (e.matches) {
          root.classList.add('dark');
        } else {
          root.classList.remove('dark');
        }
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  const toggleTheme = (explicitTheme) => {
    const nextTheme = typeof explicitTheme === 'string' ? explicitTheme : (theme === 'dark' ? 'light' : 'dark');
    setTheme(nextTheme);
    localStorage.setItem('buggyman_theme', nextTheme);
    if (user && authService.updateProfile) {
      authService.updateProfile({ theme: nextTheme }).then(updated => {
        if (updated) setUser(updated);
      }).catch(() => {});
    }
    addToast(`Switched to ${nextTheme} theme`, 'info');
  };

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  if (loading) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-slate-950">
        <div className="w-10 h-10 border-4 border-slate-800 border-t-brand-indigo rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <BrowserRouter>
      {/* Toast Manager container */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>

      <Routes>
        {/* Unauthenticated routes */}
        <Route 
          path="/login" 
          element={!user ? <Login setUser={setUser} addToast={addToast} /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/register" 
          element={!user ? <Signup setUser={setUser} addToast={addToast} /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/forgot-password" 
          element={!user ? <ForgotPassword addToast={addToast} /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/auth/callback" 
          element={<OAuthCallback setUser={setUser} addToast={addToast} />} 
        />
        <Route 
          path="/onboarding" 
          element={user ? <Onboarding user={user} setUser={setUser} addToast={addToast} /> : <Navigate to="/login" />} 
        />

        {/* Workspace IDE (no navbar or sidebar wrapper for maximized viewport space) */}
        <Route 
          path="/challenge/:id" 
          element={
            user ? (
              <ErrorBoundary>
                <EditorPage 
                  user={user}
                  setUser={setUser}
                  addToast={addToast} 
                  theme={theme} 
                  toggleTheme={toggleTheme}
                  settings={settings}
                />
              </ErrorBoundary>
            ) : (
              <Navigate to="/login" />
            )
          } 
        />
        <Route 
          path="/pvp/arena/:battleId" 
          element={
            user ? (
              <ErrorBoundary>
                <PvPArena 
                  user={user}
                  setUser={setUser}
                  addToast={addToast} 
                  theme={theme} 
                  toggleTheme={toggleTheme}
                />
              </ErrorBoundary>
            ) : (
              <Navigate to="/login" />
            )
          } 
        />

        {/* Authenticated routes wrapped with core layout frame */}
        <Route 
          path="/*" 
          element={
            user ? (
              <AuthenticatedLayout 
                user={user} 
                setUser={setUser} 
                theme={theme} 
                toggleTheme={toggleTheme} 
                notifications={notifications}
                setNotifications={setNotifications}
                settings={settings}
                setSettings={setSettings}
                addToast={addToast}
              />
            ) : (
              <Navigate to="/login" />
            )
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

// Layout wrapper for authenticated pages
function AuthenticatedLayout({ 
  user, 
  setUser, 
  theme, 
  toggleTheme, 
  notifications, 
  setNotifications, 
  settings, 
  setSettings,
  addToast 
}) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-200">
      {/* Left panel */}
      <Sidebar 
        user={user} 
        setUser={setUser} 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)} 
      />
      
      {/* Right container panel */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
        {/* Header header */}
        <Navbar 
          user={user} 
          theme={theme} 
          toggleTheme={toggleTheme} 
          notifications={notifications} 
          onMenuToggle={() => setIsMobileMenuOpen(prev => !prev)}
        />
        
        {/* Central main page viewport */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          <Routes>
            <Route path="/dashboard" element={<Dashboard user={user} addToast={addToast} />} />
            <Route path="/home" element={<Navigate to="/dashboard" replace />} />
            <Route path="/challenges" element={<ChallengeSelection addToast={addToast} />} />
            <Route path="/sql-challenges" element={<SQLChallenges addToast={addToast} />} />
            <Route path="/design-challenges" element={<FrontendDesignChallenges addToast={addToast} />} />
            <Route path="/pvp" element={<PvPBattle user={user} addToast={addToast} />} />
            <Route path="/result" element={<ResultPage />} />

            <Route path="/analytics" element={<Navigate to="/profile" replace />} />
            <Route path="/leaderboard" element={<Leaderboard user={user} addToast={addToast} />} />
            <Route path="/profile" element={<UserProfile addToast={addToast} setUser={setUser} />} />
            <Route path="/career-insights" element={<CareerInsights user={user} addToast={addToast} />} />
            <Route path="/store" element={<BugBytesStore user={user} setUser={setUser} addToast={addToast} />} />
            <Route path="/admin" element={<AdminDashboard addToast={addToast} />} />
            <Route path="/notifications" element={<Navigate to="/settings?tab=notifications" replace />} />
            <Route 
              path="/settings" 
              element={
                <Settings 
                  user={user}
                  theme={theme} 
                  toggleTheme={toggleTheme} 
                  addToast={addToast} 
                  setUser={setUser}
                  settings={settings}
                  setSettings={setSettings}
                  notifications={notifications}
                  setNotifications={setNotifications}
                />
              } 
            />
            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </div>
  );
}
