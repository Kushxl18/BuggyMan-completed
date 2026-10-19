import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sun, Moon, Bell, Award, Flame, Menu, Bug } from 'lucide-react';
import Breadcrumbs from './Breadcrumbs';

export default function Navbar({ user, theme, toggleTheme, notifications = [], onMenuToggle }) {
  const location = useLocation();

  const getBreadcrumbPaths = () => {
    const segments = location.pathname.split('/').filter(Boolean);
    return segments.map((seg, index) => {
      const url = '/' + segments.slice(0, index + 1).join('/');
      const name = seg.charAt(0).toUpperCase() + seg.slice(1).replace('-', ' ');
      return { name, url };
    });
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/70 dark:bg-slate-950/70 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-4 md:px-6 transition-colors duration-200">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {/* Mobile Menu Hamburger Button */}
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 transition-all active:scale-95"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Breadcrumbs Navigation */}
        <div className="flex-1 truncate">
          <Breadcrumbs paths={getBreadcrumbPaths()} />
        </div>
      </div>

      {/* Utilities Action Bar */}
      <div className="flex items-center gap-3 md:gap-5">
        {/* User stats */}
        {user && (
          <div className="hidden sm:flex items-center gap-2.5 text-xs font-semibold">
            {/* Streak */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-amber-600 dark:text-amber-400">
              <Flame className="w-4 h-4 fill-amber-500 dark:fill-amber-400 text-amber-500 dark:text-amber-400" />
              <span>{user.streak} Day Streak</span>
            </div>
            {/* BugBytes Store Link */}
            <Link 
              to="/store" 
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-amber-700 dark:text-amber-400 hover:border-amber-500/50 hover:bg-amber-500/10 font-bold transition-all" 
              title="Visit BugBytes Store — Purchase credits & earn money back"
            >
              <Bug className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>{user.bugbytes_balance ?? user.bugbytesBalance ?? 50} BugBytes</span>
            </Link>
            {/* Points */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-cyan-700 dark:text-cyan-400">
              <Award className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <span>{user.totalScore} XP</span>
            </div>
          </div>
        )}

        {/* Theme Switcher */}
        <button
          onClick={toggleTheme}
          className="p-2 hover:bg-slate-100 dark:hover:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-all active:scale-95"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400 animate-pulse-glow" /> : <Moon className="w-4 h-4 text-slate-700" />}
        </button>

        {/* Notifications Icon */}
        <Link
          to="/settings?tab=notifications"
          className="relative p-2 hover:bg-slate-100 dark:hover:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-all active:scale-95"
          title="Notifications Inbox"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 border border-white dark:border-slate-950 text-white rounded-full flex items-center justify-center text-[9px] font-bold">
              {unreadCount}
            </span>
          )}
        </Link>

        {/* User Profile Avatar Link */}
        {user && (
          <Link to="/profile" className="flex items-center">
            <img
              src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
              alt={user.name}
              className="w-8 h-8 rounded-full object-cover ring-2 ring-blue-500/40 hover:ring-blue-400 transition-all cursor-pointer"
            />
          </Link>
        )}
      </div>
    </header>
  );
}
