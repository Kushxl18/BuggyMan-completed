import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Play
} from 'lucide-react';
import { authService } from '../services/authService';

export default function Settings({ theme, toggleTheme, addToast, setUser, settings, setSettings }) {
  const navigate = useNavigate();

  const handleFontSizeChange = (e) => {
    setSettings(prev => ({ ...prev, fontSize: parseInt(e.target.value) }));
  };

  const handleAutoSaveToggle = (e) => {
    setSettings(prev => ({ ...prev, autoSave: e.target.checked }));
    addToast(e.target.checked ? 'Auto-save enabled' : 'Auto-save disabled', 'info');
  };

  const handleLanguageChange = (e) => {
    setSettings(prev => ({ ...prev, language: e.target.value }));
    addToast(`Preferred environment set to: ${e.target.value}`, 'success');
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

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to log out?')) {
      await authService.logout();
      setUser(null);
      addToast('Logged out of session.', 'info');
      navigate('/login');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="font-heading font-extrabold text-2xl text-slate-100 flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-brand-indigo" />
          <span>Editor & Account Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">Configure layout, editor behaviors, notifications, and active session limits.</p>
      </div>

      <div className="space-y-6">
        
        {/* Editor Preferences */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-heading font-bold text-sm text-slate-200 flex items-center gap-2 border-b border-slate-800 pb-3">
            <Sliders className="w-4.5 h-4.5 text-brand-indigo" />
            <span>IDE Workspace Preferences</span>
          </h3>

          <div className="space-y-4 text-xs">
            {/* Font size */}
            <div className="flex justify-between items-center">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Type className="w-4 h-4 text-slate-500" />
                  <span>Editor Font Size</span>
                </p>
                <p className="text-[10px] text-slate-500">Configure text scaling within the Monaco code workspace.</p>
              </div>
              <select
                value={settings.fontSize}
                onChange={handleFontSizeChange}
                className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg px-3 py-1.5 focus:border-brand-indigo outline-none"
              >
                {[12, 14, 16, 18, 20].map(size => (
                  <option key={size} value={size}>{size}px</option>
                ))}
              </select>
            </div>

            {/* Auto save */}
            <div className="flex justify-between items-center">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Save className="w-4 h-4 text-slate-500" />
                  <span>Editor Auto-Save</span>
                </p>
                <p className="text-[10px] text-slate-500">Enable automatic local draft persistence as you type.</p>
              </div>
              <input
                type="checkbox"
                checked={settings.autoSave}
                onChange={handleAutoSaveToggle}
                className="w-4 h-4 rounded border-slate-850 text-brand-indigo focus:ring-brand-indigo bg-slate-950 accent-brand-indigo"
              />
            </div>

            {/* Preferred language */}
            <div className="flex justify-between items-center">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Globe className="w-4 h-4 text-slate-500" />
                  <span>Workspace Language</span>
                </p>
                <p className="text-[10px] text-slate-500">Predefine standard syntax highlighters.</p>
              </div>
              <select
                value={settings.language}
                onChange={handleLanguageChange}
                className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg px-3 py-1.5 focus:border-brand-indigo outline-none"
              >
                <option value="JavaScript">JavaScript / React</option>
                <option value="Python">Python / Django</option>
                <option value="HTML">HTML / CSS</option>
              </select>
            </div>
          </div>
        </div>

        {/* Global theme selection & notifications */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-heading font-bold text-sm text-slate-200 flex items-center gap-2 border-b border-slate-800 pb-3">
            <Sun className="w-4.5 h-4.5 text-brand-indigo" />
            <span>Theme & Notification preferences</span>
          </h3>

          <div className="space-y-4 text-xs">
            {/* Theme switcher */}
            <div className="flex justify-between items-center">
              <div className="space-y-0.5">
                <p className="font-semibold text-slate-200">Application Theme</p>
                <p className="text-[10px] text-slate-500">Toggle light / dark visibility constraints.</p>
              </div>
              <button
                onClick={toggleTheme}
                className="button-secondary text-xs px-4 py-2 border-slate-800 flex items-center gap-2"
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="w-4 h-4 text-brand-amber animate-pulse-glow" />
                    <span>Switch Light Theme</span>
                  </>
                ) : (
                  <>
                    <Moon className="w-4 h-4 text-slate-400" />
                    <span>Switch Dark Theme</span>
                  </>
                )}
              </button>
            </div>

            {/* Notification triggers */}
            <div className="space-y-3 pt-2">
              <p className="font-semibold text-slate-200 flex items-center gap-1.5">
                <BellRing className="w-4.5 h-4.5 text-slate-500" />
                <span>Email & Toast Alerts</span>
              </p>
              <div className="grid grid-cols-1 gap-2.5 pl-6">
                {[
                  { key: 'achievements', label: 'Unlockable Badges & Achievements' },
                  { key: 'challenges', label: 'New Challenges Released' },
                  { key: 'system', label: 'System maintenance & announcements' }
                ].map(item => (
                  <label key={item.key} className="flex items-center text-slate-400 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications[item.key]}
                      onChange={() => handleTogglePreference(item.key)}
                      className="w-4 h-4 rounded border-slate-850 text-brand-indigo focus:ring-brand-indigo bg-slate-950 accent-brand-indigo mr-2.5"
                    />
                    <span>{item.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Danger zone session */}
        <div className="glass-card p-6 rounded-2xl border border-brand-rose/25 space-y-4">
          <h3 className="font-heading font-bold text-sm text-brand-rose flex items-center gap-2 border-b border-brand-rose/15 pb-3">
            <ShieldIcon />
            <span>Danger Actions Zone</span>
          </h3>

          <div className="flex justify-between items-center text-xs">
            <div className="space-y-0.5">
              <p className="font-semibold text-slate-200">Logout Current Session</p>
              <p className="text-[10px] text-slate-500">Remove stored JWT token, resetting view settings back to defaults.</p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2.5 bg-brand-rose/10 hover:bg-brand-rose border border-brand-rose/30 hover:border-brand-rose text-brand-rose hover:text-white font-semibold rounded-xl transition-all duration-150 flex items-center gap-2 active:scale-95"
            >
              <LogOut className="w-4.5 h-4.5" />
              <span>Logout</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

// Compact warning icon
function ShieldIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m0-10.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.249-8.25-3.286Zm0 13.036h.008v.008H12v-.008Z" />
    </svg>
  );
}
