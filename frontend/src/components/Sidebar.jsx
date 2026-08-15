import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Code2, 
  Database,
  Palette,
  Trophy, 
  BarChart3, 
  User, 
  Shield, 
  Bell, 
  Settings as SettingsIcon, 
  LogOut,
  Bug
} from 'lucide-react';
import { authService } from '../services/authService';

export default function Sidebar({ user, setUser, isOpen, onClose }) {
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin' || user?.isAdmin || user?.is_staff || user?.username === 'admin';

  const handleLogout = async () => {
    await authService.logout();
    setUser(null);
    if (onClose) onClose();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: 'Code Challenges', path: '/challenges', icon: <Code2 className="w-5 h-5" /> },
    { name: 'SQL Lab', path: '/sql-challenges', icon: <Database className="w-5 h-5" /> },
    { name: 'Frontend Studio', path: '/design-challenges', icon: <Palette className="w-5 h-5" /> },
    { name: 'Leaderboard', path: '/leaderboard', icon: <Trophy className="w-5 h-5" /> },
    { name: 'Analytics', path: '/analytics', icon: <BarChart3 className="w-5 h-5" /> },
    { name: 'My Profile', path: '/profile', icon: <User className="w-5 h-5" /> },
    { name: 'Notifications', path: '/notifications', icon: <Bell className="w-5 h-5" /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon className="w-5 h-5" /> },
  ];

  if (isAdmin) {
    navItems.splice(5, 0, { name: 'Admin Console', path: '/admin', icon: <Shield className="w-5 h-5 text-amber-400" /> });
  }

  const sidebarContent = (
    <div className="flex flex-col flex-1 justify-between h-full py-6 bg-white dark:bg-[#0E1012] border-r border-slate-200 dark:border-[#292E33]">
      <div className="flex flex-col flex-1">
        {/* Brand Logo */}
        <div className="flex items-center justify-between px-6 mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500 text-white shadow-sm">
              <Bug className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-heading font-extrabold text-lg text-slate-800 dark:text-slate-100 tracking-tight">BuggyMan</h1>
              <p className="text-[10px] text-cyan-500 font-semibold uppercase tracking-wider">AI Debugger Lab</p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-semibold border-l-2 border-cyan-500'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-[#1B1F23]'
                }`
              }
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Profile Info & Logout */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 flex flex-col gap-3">
        {user && (
          <div className="flex items-center gap-3 px-2.5 py-2 rounded-xl bg-slate-100 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800/80">
            <img
              src={user.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}
              alt={user.name}
              className="w-9 h-9 rounded-full object-cover ring-1 ring-blue-500/40"
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">{user.name}</p>
              <div className="flex items-center gap-1.5">
                <p className="text-[10px] text-slate-400 dark:text-slate-500 truncate">@{user.username}</p>
                {isAdmin && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-500/10 border border-amber-500/30 text-amber-400 uppercase">
                    Admin
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center justify-center gap-2 w-full py-2.5 bg-slate-100 dark:bg-slate-950 hover:bg-rose-50 dark:hover:bg-rose-950/20 border border-slate-200 dark:border-slate-800 hover:border-rose-500/30 text-slate-600 dark:text-slate-400 hover:text-rose-400 text-xs font-semibold rounded-xl transition-all duration-150 active:scale-95"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 h-screen sticky top-0 transition-colors duration-200">
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
