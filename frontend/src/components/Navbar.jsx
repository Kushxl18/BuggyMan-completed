import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sun, Moon, Bell, Menu } from 'lucide-react';
import Breadcrumbs from './Breadcrumbs';

export default function Navbar({ user, theme, toggleTheme, notifications = [], onMenuToggle }) {
  const location = useLocation();

  const getBreadcrumbPaths = () => {
    const segments = location.pathname.split('/').filter(Boolean);
    return segments.map((seg, index) => {
      const url = '/' + segments.slice(0, index + 1).join('/');
      let name = seg.charAt(0).toUpperCase() + seg.slice(1).replace('-', ' ');
      if (seg.toLowerCase() === 'dashboard') name = 'Home';
      return { name, url };
    });
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="h-14 border-b border-slate-200/80 dark:border-white/[0.06] bg-white/80 dark:bg-[#08090D]/80 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-4 md:px-6 transition-colors duration-150 shadow-[0_1px_0_0_rgba(255,255,255,0.02)]">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {/* Mobile Menu Hamburger Button */}
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-1.5 rounded-md border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.04] text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-colors"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        {/* Breadcrumbs Navigation */}
        <div className="flex-1 truncate">
          <Breadcrumbs paths={getBreadcrumbPaths()} />
        </div>
      </div>

      {/* Utilities Action Bar */}
      <div className="flex items-center gap-2 md:gap-3">
        {/* User stats - Raycast/Linear inspired developer badge pills */}
        {user && (
          <div className="hidden sm:flex items-center gap-2 text-xs">
            {/* Streak */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-slate-200 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.03] text-slate-700 dark:text-slate-300 font-mono text-[11px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              <span className="text-slate-400 dark:text-slate-500">Streak:</span>
              <span className="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">{user.streak || 0}d</span>
            </div>

            {/* BugBytes Store Link */}
            <Link 
              to="/store" 
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-slate-200 dark:border-white/[0.08] bg-slate-50/80 dark:bg-white/[0.03] hover:bg-slate-100 dark:hover:bg-white/[0.07] hover:border-slate-300 dark:hover:border-white/[0.15] text-slate-700 dark:text-slate-300 font-mono text-[11px] transition-all shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] group" 
              title="Visit BugBytes Store — Purchase credits & earn money back"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors">Credits:</span>
              <span className="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">{user.bugbytes_balance ?? user.bugbytesBalance ?? 50} BB</span>
            </Link>

            {/* Points */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-blue-200/60 dark:border-blue-900/40 bg-blue-50/60 dark:bg-blue-950/30 text-blue-700 dark:text-blue-300 font-mono text-[11px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              <span className="text-blue-500 dark:text-blue-400/80">Score:</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400 tabular-nums">{user.totalScore || 0} XP</span>
            </div>
          </div>
        )}

        {/* Theme Switcher */}
        <button
          onClick={toggleTheme}
          className="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] bg-slate-50/50 dark:bg-white/[0.02] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-all shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] active:scale-95"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* Notifications Icon */}
        <Link
          to="/settings?tab=notifications"
          className="relative p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] bg-slate-50/50 dark:bg-white/[0.02] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-all shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] active:scale-95"
          title="Notifications Inbox"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 bg-rose-500 border border-white dark:border-[#08090D] text-white rounded-full flex items-center justify-center text-[9px] font-bold">
              {unreadCount}
            </span>
          )}
        </Link>

        {/* User Profile Avatar Link */}
        {user && (
          <Link to="/profile" className="flex items-center ml-1 group">
            <img
              src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
              alt={user.name || user.username}
              className="w-7 h-7 rounded-md object-cover ring-1 ring-slate-200 dark:ring-white/[0.12] group-hover:ring-blue-500/60 transition-all cursor-pointer shadow-sm"
            />
          </Link>
        )}
      </div>
    </header>
  );
}
