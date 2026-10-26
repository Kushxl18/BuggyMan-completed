import React, { useState, useEffect } from 'react';
import { Bell, Check, Trash2, Award, Info, Code2, CheckSquare } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { challengeService } from '../services/challengeService';

export default function Notifications({ notifications, setNotifications, addToast }) {
  const [filter, setFilter] = useState('all'); // all, unread, system, challenges, achievements
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadNotifications() {
      try {
        const backendNotifs = await challengeService.getNotifications();
        if (Array.isArray(backendNotifs) && backendNotifs.length > 0 && typeof setNotifications === 'function') {
          setNotifications(backendNotifs);
        }
      } catch (err) {
        // Fallback to local state
      }
    }
    loadNotifications();
  }, [setNotifications]);

  const handleMarkAsRead = async (id) => {
    try {
      await challengeService.markNotificationAsRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    setLoading(true);
    try {
      const unreads = notifications.filter(n => !n.read);
      await Promise.all(unreads.map(n => challengeService.markNotificationAsRead(n.id)));
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      addToast('All notifications marked as read.', 'success');
    } catch (err) {
      addToast('Failed to mark all as read.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAll = () => {
    if (window.confirm('Delete all notification logs?')) {
      setNotifications([]);
      addToast('Notification logs cleared.', 'info');
    }
  };

  const getIcon = (type) => {
    if (type === 'achievement') return <Award className="w-5 h-5 text-brand-amber shrink-0" />;
    if (type === 'challenge') return <Code2 className="w-5 h-5 text-brand-emerald shrink-0" />;
    return <Info className="w-5 h-5 text-brand-indigo shrink-0" />;
  };

  // Filter logic
  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'system') return n.type === 'system';
    if (filter === 'challenges') return n.type === 'challenge';
    if (filter === 'achievements') return n.type === 'achievement';
    return true;
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-100 flex items-center gap-2">
            <Bell className="w-6 h-6 text-brand-indigo" />
            <span>Notifications Inbox</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">Review announcements, challenge releases, and career milestone notifications.</p>
        </div>

        {notifications.length > 0 && (
          <div className="flex items-center gap-2">
            <button
              onClick={handleMarkAllRead}
              disabled={loading || notifications.every(n => n.read)}
              className="button-secondary text-[11px] px-3 py-2 flex items-center gap-1 hover:border-slate-700 disabled:opacity-40"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Mark all read</span>
            </button>
            <button
              onClick={handleDeleteAll}
              className="button-secondary text-[11px] px-3 py-2 border-brand-rose/25 text-brand-rose bg-rose-950/5 hover:bg-rose-950/10 flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear inbox</span>
            </button>
          </div>
        )}
      </div>

      {/* Tabs / Filter Badges */}
      <div className="flex flex-wrap gap-2 pt-2 border-b border-slate-900 pb-4">
        {['all', 'unread', 'achievements', 'challenges', 'system'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${
              filter === type
                ? 'bg-brand-indigo text-white shadow-glow-indigo'
                : 'bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Notifications list */}
      {filteredNotifications.length > 0 ? (
        <div className="space-y-3 pt-2">
          {filteredNotifications.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.read && handleMarkAsRead(n.id)}
              className={`glass-panel p-5 rounded-xl border transition-all flex items-start gap-4 cursor-pointer relative group ${
                n.read 
                  ? 'border-slate-800 opacity-90' 
                  : 'border-l-4 border-l-brand-cyan border-slate-800 hover:border-slate-700 shadow-md'
              }`}
            >
              {/* Blue dot indicator for unreads */}
              {!n.read && (
                <span className="absolute top-5 right-5 w-2 h-2 rounded-full bg-brand-indigo animate-pulse-glow" />
              )}
              
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-850">
                {getIcon(n.type)}
              </div>

              <div className="flex-1 min-w-0 pr-4">
                <h4 className={`text-xs font-bold text-slate-800 dark:text-slate-200 ${!n.read ? 'font-semibold text-slate-100' : ''}`}>
                  {n.title}
                </h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{n.message}</p>
                <span className="text-[10px] text-slate-500 font-bold block mt-2.5 uppercase">{n.time}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={CheckSquare}
          title="Clean Slate"
          description="No notifications matched this filter right now. You are fully caught up!"
          actionLabel={filter !== 'all' ? 'Show All Notifications' : null}
          onAction={() => setFilter('all')}
        />
      )}
    </div>
  );
}
