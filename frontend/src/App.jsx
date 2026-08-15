import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Toast from './components/Toast';

// Auth Pages
import Login from './pages/Auth/Login';
import Signup from './pages/Auth/Signup';
import ForgotPassword from './pages/Auth/ForgotPassword';

// Core Pages
import Dashboard from './pages/Dashboard';
import ChallengeSelection from './pages/ChallengeSelection';
import SQLChallenges from './pages/SQLChallenges';
import FrontendDesignChallenges from './pages/FrontendDesignChallenges';
import EditorPage from './pages/Challenge/EditorPage';

import ResultPage from './pages/ResultPage';
import Analytics from './pages/Analytics';
import Leaderboard from './pages/Leaderboard';
import UserProfile from './pages/UserProfile';
import AdminDashboard from './pages/AdminDashboard';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';

import { authService } from './services/authService';

export default function App() {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('dark');
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
        } catch (err) {
          localStorage.removeItem('token');
          sessionStorage.removeItem('token');
        }
      }
      setLoading(false);
    }
    loadSession();
  }, []);

  // Theme change sync
  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
    addToast(`Switched to ${theme === 'dark' ? 'Light' : 'Dark'} theme`, 'info');
  };

  const addToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  };

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

        {/* Workspace IDE (no navbar or sidebar wrapper for maximized viewport space) */}
        <Route 
          path="/challenge/:id" 
          element={
            user ? (
              <EditorPage 
                addToast={addToast} 
                theme={theme} 
                toggleTheme={toggleTheme}
                settings={settings}
                setUser={setUser}
              />
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
            <Route path="/challenges" element={<ChallengeSelection addToast={addToast} />} />
            <Route path="/sql-challenges" element={<SQLChallenges addToast={addToast} />} />
            <Route path="/design-challenges" element={<FrontendDesignChallenges addToast={addToast} />} />
            <Route path="/result" element={<ResultPage />} />

            <Route path="/analytics" element={<Analytics addToast={addToast} />} />
            <Route path="/leaderboard" element={<Leaderboard addToast={addToast} />} />
            <Route path="/profile" element={<UserProfile addToast={addToast} setUser={setUser} />} />
            <Route path="/admin" element={<AdminDashboard addToast={addToast} />} />
            <Route 
              path="/notifications" 
              element={
                <Notifications 
                  notifications={notifications} 
                  setNotifications={setNotifications} 
                  addToast={addToast} 
                />
              } 
            />
            <Route 
              path="/settings" 
              element={
                <Settings 
                  theme={theme} 
                  toggleTheme={toggleTheme} 
                  addToast={addToast} 
                  setUser={setUser}
                  settings={settings}
                  setSettings={setSettings}
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
