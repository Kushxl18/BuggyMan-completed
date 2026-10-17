import React, { useState, useEffect } from 'react';
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
  Bug,
  ShoppingBag,
  Swords,
  ChevronLeft,
  ChevronRight
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
    { name: 'Home', path: '/dashboard', icon: <Home className="w-5 h-5 shrink-0" /> },
    { name: 'Code Challenges', path: '/challenges', icon: <Code2 className="w-5 h-5 shrink-0" /> },
    { name: 'SQL Lab', path: '/sql-challenges', icon: <Database className="w-5 h-5 shrink-0" /> },
    { name: 'Frontend Studio', path: '/design-challenges', icon: <Palette className="w-5 h-5 shrink-0" /> },
    { name: 'PvP Battle', path: '/pvp', icon: <Swords className="w-5 h-5 shrink-0 text-rose-500" /> },
    { name: 'Leaderboard', path: '/leaderboard', icon: <Trophy className="w-5 h-5 shrink-0" /> },
    { name: 'My Profile', path: '/profile', icon: <User className="w-5 h-5 shrink-0" /> },
    { name: 'Career Insights', path: '/career-insights', icon: <Briefcase className="w-5 h-5 shrink-0" /> },
    { name: 'BugBytes Store', path: '/store', icon: <ShoppingBag className="w-5 h-5 shrink-0 text-amber-500" /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon className="w-5 h-5 shrink-0" /> },
  ];

  if (isAdmin) {
    navItems.splice(5, 0, { name: 'Admin Console', path: '/admin', icon: <Shield className="w-5 h-5 text-amber-400 shrink-0" /> });
  }

  const sidebarContent = (
    <div className={`flex flex-col flex-1 justify-between h-full py-6 bg-white dark:bg-[#0E1012] border-r border-slate-200 dark:border-[#292E33] transition-all duration-300 ${
      isCollapsed ? 'items-center px-2' : ''
    }`}>
      <div className="flex flex-col flex-1 w-full min-w-0">
        {/* Brand Logo Header & Collapse Toggle */}
        <div className={`flex items-center justify-between mb-8 ${isCollapsed ? 'justify-center px-0' : 'px-6'}`}>
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2 rounded-xl bg-cyan-500 text-white shadow-sm shrink-0">
              <Bug className="w-6 h-6 text-white" />
            </div>
            {!isCollapsed && (
              <div className="min-w-0 truncate">
                <h1 className="font-heading font-extrabold text-lg text-slate-800 dark:text-slate-100 tracking-tight truncate">BuggyMan</h1>
                <p className="text-[10px] text-cyan-500 font-semibold uppercase tracking-wider truncate">AI Debugger Lab</p>
              </div>
            )}
          </div>

          {/* Desktop Minimize Toggle Button */}
          <button
            onClick={toggleCollapse}
            className="hidden lg:flex p-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-900 transition-all active:scale-95 shrink-0"
            title={isCollapsed ? "Expand Sidebar" : "Minimize Sidebar"}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className={`flex-1 space-y-1.5 ${isCollapsed ? 'px-1' : 'px-3'}`}>
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={onClose}
              title={isCollapsed ? item.name : undefined}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isCollapsed ? 'justify-center px-0' : ''
                } ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold border-l-2 border-cyan-500'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-[#1B1F23]'
                }`
              }
            >
              {item.icon}
              {!isCollapsed && <span className="truncate">{item.name}</span>}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Profile Info & Logout */}
      <div className={`border-t border-slate-200 dark:border-slate-800 flex flex-col gap-3 w-full ${
        isCollapsed ? 'p-2 items-center' : 'p-4'
      }`}>
        {user && (
          <div className={`flex items-center rounded-xl bg-slate-100 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80 ${
            isCollapsed ? 'justify-center p-2' : 'gap-3 px-2.5 py-2'
          }`}>
            <img
              src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
              alt={user.name}
              className="w-8 h-8 rounded-full object-cover ring-1 ring-blue-500/40 shrink-0"
              title={isCollapsed ? `${user.name} (@${user.username})` : undefined}
            />
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">{user.name}</p>
                <div className="flex items-center gap-1.5">
                  <p className="text-[10px] text-slate-400 dark:text-slate-500 truncate">@{user.username}</p>
                  {isAdmin && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400 uppercase shrink-0">
                      Admin
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
        <button
          onClick={handleLogout}
          title={isCollapsed ? "Sign Out" : undefined}
          className={`flex items-center justify-center gap-2 py-2.5 bg-slate-100 dark:bg-slate-950 hover:bg-rose-50 dark:hover:bg-rose-950/20 border border-slate-200 dark:border-slate-800 hover:border-rose-500/30 text-slate-600 dark:text-slate-400 hover:text-rose-400 text-xs font-semibold rounded-xl transition-all duration-150 active:scale-95 ${
            isCollapsed ? 'w-10 h-10 p-0' : 'w-full'
          }`}
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {!isCollapsed && <span>Sign Out</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex h-screen sticky top-0 transition-all duration-300 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}>
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm" onClick={onClose} />
          <div className="relative z-10 w-72 h-full shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
