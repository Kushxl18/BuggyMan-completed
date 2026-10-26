import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  Home, 
  Code2, 
  Database, 
  Palette, 
  Trophy, 
  User, 
  Briefcase, 
  Shield, 
  Settings as SettingsIcon, 
  LogOut, 
  ShoppingBag, 
  Swords, 
  ChevronLeft, 
  ChevronRight, 
  Terminal, 
  Layers 
} from 'lucide-react';
import { authService } from '../services/authService';

export default function Sidebar({ user, setUser, isOpen, onClose }) {
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin' || user?.isAdmin || user?.is_staff || user?.username === 'admin';

  // Sidebar collapse state with localStorage persistence
  const [isCollapsed, setIsCollapsed] = useState(() => {
    return localStorage.getItem('buggyman_sidebar_collapsed') === 'true';
  });

  const toggleCollapse = () => {
    setIsCollapsed(prev => {
      const next = !prev;
      localStorage.setItem('buggyman_sidebar_collapsed', String(next));
      return next;
    });
  };

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    if (onClose) onClose();
    navigate('/login');
  };

  const navItems = [
    { name: 'Home', path: '/dashboard', icon: <Home className="w-4 h-4 shrink-0" /> },
    { name: 'Code Challenges', path: '/challenges', icon: <Code2 className="w-4 h-4 shrink-0" /> },
    { name: 'SQL Lab', path: '/sql-challenges', icon: <Database className="w-4 h-4 shrink-0" /> },
    { name: 'Frontend Studio', path: '/design-challenges', icon: <Palette className="w-4 h-4 shrink-0" /> },
    // { name: 'Feature Arena', path: '/feature-challenges', icon: <Layers className="w-4 h-4 shrink-0" /> }, // Unlinked for now - preserved to re-link later
    { name: 'PvP Battle', path: '/pvp', icon: <Swords className="w-4 h-4 shrink-0" /> },
    { name: 'Leaderboard', path: '/leaderboard', icon: <Trophy className="w-4 h-4 shrink-0" /> },
    { name: 'Profile', path: '/profile', icon: <User className="w-4 h-4 shrink-0" /> },
    { name: 'Career Insights', path: '/career-insights', icon: <Briefcase className="w-4 h-4 shrink-0" /> },
    { name: 'Store', path: '/store', icon: <ShoppingBag className="w-4 h-4 shrink-0" /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon className="w-4 h-4 shrink-0" /> },
  ];

  if (isAdmin) {
    navItems.splice(5, 0, { name: 'Admin Console', path: '/admin', icon: <Shield className="w-4 h-4 shrink-0" /> });
  }

  const sidebarContent = (
    <div className={`flex flex-col flex-1 justify-between h-full py-4 bg-slate-50/50 dark:bg-[#0C0F17] border-r border-slate-200/80 dark:border-white/[0.06] transition-all duration-200 ${
      isCollapsed ? 'items-center px-2' : ''
    }`}>
      <div className="flex flex-col flex-1 w-full min-w-0">
        {/* Brand Logo Header & Collapse Toggle */}
        <div className={`flex items-center justify-between mb-4 pb-3 border-b border-slate-200/80 dark:border-white/[0.06] ${isCollapsed ? 'justify-center px-0' : 'px-4'}`}>
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-b from-blue-600 to-indigo-700 text-white flex items-center justify-center shrink-0 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.25)]">
              <Terminal className="w-4 h-4" />
            </div>
            {!isCollapsed && (
              <div className="min-w-0 truncate">
                <span className="font-semibold text-sm text-slate-900 dark:text-slate-100 tracking-tight block">BuggyMan</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono block">Dev Platform</span>
              </div>
            )}
          </div>

          {/* Desktop Minimize Toggle Button */}
          <button
            onClick={toggleCollapse}
            className="hidden lg:flex p-1 rounded-md border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-colors shrink-0"
            title={isCollapsed ? "Expand Sidebar" : "Minimize Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className={`flex-1 space-y-1 ${isCollapsed ? 'px-1' : 'px-2.5'}`}>
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={onClose}
              title={isCollapsed ? item.name : undefined}
              className={({ isActive }) =>
                `group flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                  isCollapsed ? 'justify-center px-0' : ''
                } ${
                  isActive
                    ? 'bg-slate-200/70 dark:bg-white/[0.08] text-slate-900 dark:text-white font-medium shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)] border border-slate-300/40 dark:border-white/[0.08]'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100/70 dark:hover:bg-white/[0.04] border border-transparent'
                }`
              }
            >
              <span className="transition-colors group-hover:text-blue-500 dark:group-hover:text-blue-400">
                {item.icon}
              </span>
              {!isCollapsed && <span className="truncate">{item.name}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Profile Info & Logout */}
      <div className={`border-t border-slate-200/80 dark:border-white/[0.06] pt-3 flex flex-col gap-2 w-full ${
        isCollapsed ? 'p-1.5 items-center' : 'px-3'
      }`}>
        {user && !isCollapsed && (
          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg border border-slate-200/80 dark:border-white/[0.08] bg-white/70 dark:bg-white/[0.03] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
            <img
              src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
              alt={user.name || user.username}
              className="w-6 h-6 rounded-md object-cover shrink-0 ring-1 ring-slate-200 dark:ring-white/10"
            />
            <div className="flex-1 min-w-0">
              <p className="text-[11px] font-medium text-slate-800 dark:text-slate-200 truncate">{user.name || user.username}</p>
              <p className="text-[10px] text-slate-400 dark:text-slate-500 font-mono truncate">@{user.username}</p>
            </div>
            {isAdmin && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900/60 uppercase shrink-0">
                Admin
              </span>
            )}
          </div>
        )}

        <button
          onClick={handleLogout}
          title="Sign Out"
          aria-label="Sign Out"
          className={`flex items-center justify-center gap-2 py-1.5 border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] text-slate-600 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:border-rose-300 dark:hover:border-rose-900/60 hover:bg-rose-50/50 dark:hover:bg-rose-950/20 text-xs font-medium rounded-lg transition-all shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)] active:scale-98 ${
            isCollapsed ? 'w-8 h-8 p-0' : 'w-full'
          }`}
        >
          <LogOut className="w-3.5 h-3.5 shrink-0" />
          <span className={isCollapsed ? 'sr-only' : ''}>Sign Out</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex h-screen sticky top-0 transition-all duration-200 ${
        isCollapsed ? 'w-16' : 'w-56'
      }`}>
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={onClose} />
          <div className="relative z-10 w-64 h-full shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
