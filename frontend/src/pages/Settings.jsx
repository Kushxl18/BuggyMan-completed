import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Settings as SettingsIcon, 
  Sun, 
  Moon, 
  Type, 
  Save, 
  BellRing, 
  Globe, 
  LogOut,
  Sliders,
  Bell,
  Check,
  Trash2,
  Award,
  Info,
  Code2,
  CheckSquare
} from 'lucide-react';
import { authService } from '../services/authService';
import { challengeService } from '../services/challengeService';

export default function Settings({ user, theme, toggleTheme, addToast, setUser, settings, setSettings, notifications = [], setNotifications }) {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Determine active section tab from URL query param ?tab=notifications or state
  const queryParams = new URLSearchParams(location.search);
  const initialTab = queryParams.get('tab') === 'notifications' ? 'notifications' : 'general';
  
  const [activeTab, setActiveTab] = useState(initialTab);
  const [notifFilter, setNotifFilter] = useState('all');
  const [notifLoading, setNotifLoading] = useState(false);

  useEffect(() => {
    if (queryParams.get('tab') === 'notifications') {
      setActiveTab('notifications');
    }
  }, [location.search]);

  useEffect(() => {
    async function loadNotifications() {
      try {
        const backendNotifs = await challengeService.getNotifications();
        if (Array.isArray(backendNotifs) && backendNotifs.length > 0 && typeof setNotifications === 'function') {
          setNotifications(backendNotifs);
        }
      } catch (err) {
        // Local fallback
      }
    }
    loadNotifications();
  }, [setNotifications]);

  const handleFontSizeChange = (e) => {
    setSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }));
  };

  const handleAutoSaveToggle = (e) => {
    setSettings(prev => ({ ...prev, autoSave: e.target.checked }));
    if (addToast) addToast(e.target.checked ? 'Auto-save enabled' : 'Auto-save disabled', 'info');
  };

  const handleLanguageChange = (e) => {
    setSettings(prev => ({ ...prev, language: e.target.value }));
    if (addToast) addToast(`Preferred environment set to: ${e.target.value}`, 'success');
  };

  const handleTogglePreference = (key) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }));
  };

  const handleMarkAsRead = async (id) => {
    try {
      await challengeService.markNotificationAsRead(id);
      if (typeof setNotifications === 'function') {
        setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    setNotifLoading(true);
    try {
      const unreads = notifications.filter(n => !n.read);
      await Promise.all(unreads.map(n => challengeService.markNotificationAsRead(n.id)));
      if (typeof setNotifications === 'function') {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      }
      if (addToast) addToast('All notifications marked as read.', 'success');
    } catch (err) {
      if (addToast) addToast('Failed to mark all as read.', 'error');
    } finally {
      setNotifLoading(false);
    }
  };

  const handleDeleteAll = () => {
    if (window.confirm('Clear notification history log?')) {
      if (typeof setNotifications === 'function') {
        setNotifications([]);
      }
      if (addToast) addToast('Notification logs cleared.', 'info');
    }
  };

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to log out?')) {
      await authService.logout();
      if (typeof setUser === 'function') setUser(null);
      if (addToast) addToast('Logged out of session.', 'info');
      navigate('/login');
    }
  };

  const getIcon = (type) => {
    if (type === 'achievement') return <Award className="w-5 h-5 text-amber-500 shrink-0" />;
    if (type === 'challenge') return <Code2 className="w-5 h-5 text-emerald-500 shrink-0" />;
    return <Info className="w-5 h-5 text-cyan-500 shrink-0" />;
  };

  const filteredNotifications = notifications.filter(n => {
    if (notifFilter === 'unread') return !n.read;
    if (notifFilter === 'system') return n.type === 'system';
    if (notifFilter === 'challenges') return n.type === 'challenge';
    if (notifFilter === 'achievements') return n.type === 'achievement';
    return true;
  });

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in py-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#292E33] pb-4">
        <div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
            <SettingsIcon className="w-6 h-6 text-cyan-500" />
            <span>Settings & Notifications</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Configure account settings, theme, IDE workspace, and review notification history.</p>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-xl self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('general')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'general'
                ? 'bg-cyan-500 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            General & IDE
          </button>
          <button
            onClick={() => setActiveTab('notifications')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'notifications'
                ? 'bg-cyan-500 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
            }`}
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Notifications</span>
            {notifications.filter(n => !n.read).length > 0 && (
              <span className="w-2 h-2 rounded-full bg-rose-500" />
            )}
          </button>
        </div>
      </div>

      {/* Tab 1: General & IDE Preferences */}
      {activeTab === 'general' && (
        <div className="space-y-6">
          {/* IDE Workspace Preferences */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2 border-b border-slate-200 dark:border-[#292E33] pb-3">
              <Sliders className="w-4.5 h-4.5 text-cyan-500" />
              <span>IDE Workspace Preferences</span>
            </h3>

            <div className="space-y-4 text-xs">
              <div className="flex justify-between items-center">
                <div className="space-y-0.5">
                  <p className="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                    <Type className="w-4 h-4 text-slate-500" />
                    <span>Editor Font Size</span>
                  </p>
                  <p className="text-[10px] text-slate-500">Configure text scaling within the Monaco code workspace.</p>
                </div>
                <select
                  value={settings.fontSize}
                  onChange={handleFontSizeChange}
                  className="bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-1.5 outline-none focus:border-cyan-500"
                >
                  {[12, 14, 16, 18, 20].map(size => (
                    <option key={size} value={size}>{size}px</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-between items-center">
                <div className="space-y-0.5">
                  <p className="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                    <Save className="w-4 h-4 text-slate-500" />
                    <span>Editor Auto-Save</span>
                  </p>
                  <p className="text-[10px] text-slate-500">Enable automatic local draft persistence as you type.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={handleAutoSaveToggle}
                  className="w-4 h-4 rounded border-slate-700 text-cyan-500 bg-slate-950 focus:ring-cyan-500"
                />
              </div>

              <div className="flex justify-between items-center">
                <div className="space-y-0.5">
                  <p className="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                    <Globe className="w-4 h-4 text-slate-500" />
                    <span>Workspace Language</span>
                  </p>
                  <p className="text-[10px] text-slate-500">Predefine standard syntax highlighters.</p>
                </div>
                <select
                  value={settings.language}
                  onChange={handleLanguageChange}
                  className="bg-white dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] text-slate-800 dark:text-[#F0F2F4] rounded-lg px-3 py-1.5 outline-none focus:border-cyan-500"
                >
                  <option value="JavaScript">JavaScript / React</option>
                  <option value="Python">Python / Django</option>
                  <option value="HTML">HTML / CSS</option>
                </select>
              </div>
            </div>
          </div>

          {/* Application Theme */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2 border-b border-slate-200 dark:border-[#292E33] pb-3">
              <Sun className="w-4.5 h-4.5 text-cyan-500" />
              <span>Application Theme</span>
            </h3>

            <div className="flex justify-between items-center text-xs">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-700 dark:text-slate-200">Appearance Mode</p>
                <p className="text-[10px] text-slate-500">Select Dark, Light, or System theme.</p>
              </div>
              <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33] rounded-xl">
                {['dark', 'light', 'system'].map((t) => (
                  <button
                    key={t}
                    onClick={() => toggleTheme(t)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                      theme === t
                        ? 'bg-cyan-500 text-white shadow-sm'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>



          {/* Danger Zone */}
          <div className="glass-card p-6 rounded-2xl border border-rose-500/25 space-y-4">
            <h3 className="font-heading font-bold text-sm text-rose-500 flex items-center gap-2 border-b border-rose-500/15 pb-3">
              <LogOut className="w-4 h-4" />
              <span>Session Actions</span>
            </h3>

            <div className="flex justify-between items-center text-xs">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-700 dark:text-slate-200">Logout Current Session</p>
                <p className="text-[10px] text-slate-500">Remove active session token and reset views.</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2.5 bg-rose-500/10 hover:bg-rose-500 border border-rose-500/30 hover:border-rose-500 text-rose-400 hover:text-white font-semibold rounded-xl transition-all duration-150 flex items-center gap-2 active:scale-95"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Notifications Inbox & Alert Preferences */}
      {activeTab === 'notifications' && (
        <div className="space-y-6">
          {/* Notification Alert Toggles */}
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <h3 className="font-heading font-bold text-sm text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2 border-b border-slate-200 dark:border-[#292E33] pb-3">
              <BellRing className="w-4.5 h-4.5 text-cyan-500" />
              <span>Notification Alert Preferences</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              {[
                { key: 'achievements', label: 'Badges & Achievements' },
                { key: 'challenges', label: 'New Challenges Released' },
                { key: 'system', label: 'System Announcements' }
              ].map(item => (
                <label key={item.key} className="flex items-center text-slate-700 dark:text-slate-300 cursor-pointer p-3 rounded-xl bg-slate-50 dark:bg-[#1B1F23] border border-slate-200 dark:border-[#292E33]">
                  <input
                    type="checkbox"
                    checked={settings.notifications?.[item.key] ?? true}
                    onChange={() => handleTogglePreference(item.key)}
                    className="w-4 h-4 rounded border-slate-700 text-cyan-500 bg-slate-950 focus:ring-cyan-500 mr-2.5"
                  />
                  <span className="font-medium">{item.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Notification Inbox Log */}
          <div className="glass-card p-6 rounded-2xl space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#292E33] pb-4">
              <div>
                <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2">
                  <Bell className="w-5 h-5 text-cyan-500" />
                  <span>Notification Inbox History</span>
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">Review releases, achievements, and maintenance logs.</p>
              </div>

              {notifications.length > 0 && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleMarkAllRead}
                    disabled={notifLoading || notifications.every(n => n.read)}
                    className="button-secondary text-[11px] px-3 py-1.5 flex items-center gap-1.5 disabled:opacity-40"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Mark all read</span>
                  </button>
                  <button
                    onClick={handleDeleteAll}
                    className="button-secondary text-[11px] px-3 py-1.5 text-rose-400 hover:text-white border-rose-500/30 flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Clear inbox</span>
                  </button>
                </div>
              )}
            </div>

            {/* Filter Badges */}
            <div className="flex flex-wrap gap-2">
              {['all', 'unread', 'achievements', 'challenges', 'system'].map((type) => (
                <button
                  key={type}
                  onClick={() => setNotifFilter(type)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${
                    notifFilter === type
                      ? 'bg-cyan-500 text-white shadow-sm'
                      : 'bg-slate-100 dark:bg-[#1B1F23] text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-[#292E33]'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>

            {/* List */}
            {filteredNotifications.length > 0 ? (
              <div className="space-y-3 pt-2">
                {filteredNotifications.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => !n.read && handleMarkAsRead(n.id)}
                    className={`p-4 rounded-xl border transition-all flex items-start gap-4 cursor-pointer relative group ${
                      n.read 
                        ? 'border-slate-200 dark:border-[#292E33] bg-slate-50/50 dark:bg-[#15181B] opacity-80' 
                        : 'border-l-4 border-l-cyan-500 border-slate-200 dark:border-[#292E33] bg-white dark:bg-[#1B1F23] shadow-sm'
                    }`}
                  >
                    {!n.read && (
                      <span className="absolute top-4 right-4 w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                    )}
                    
                    <div className="p-2 rounded-lg bg-slate-100 dark:bg-[#0E1012] border border-slate-200 dark:border-[#292E33]">
                      {getIcon(n.type)}
                    </div>

                    <div className="flex-1 min-w-0 pr-4">
                      <h4 className={`text-xs font-bold text-slate-800 dark:text-[#F0F2F4] ${!n.read ? 'text-cyan-500' : ''}`}>
                        {n.title}
                      </h4>
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{n.message}</p>
                      <span className="text-[10px] text-slate-500 font-bold block mt-2 uppercase">{n.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="glass-panel p-8 rounded-xl text-center text-slate-500 space-y-2">
                <CheckSquare className="w-8 h-8 text-cyan-500 mx-auto" />
                <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">All caught up!</p>
                <p className="text-[11px] text-slate-500">No notifications match this filter tag.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
