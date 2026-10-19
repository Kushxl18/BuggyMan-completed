import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  FileText, 
  Headphones, 
  X, 
  Mail, 
  Check, 
  Copy, 
  Send, 
  HelpCircle, 
  Clock, 
  Lock, 
  Scale, 
  ChevronDown, 
  ChevronUp,
  Sparkles
} from 'lucide-react';

export default function Footer() {
  const [activeModal, setActiveModal] = useState(null); // 'privacy' | 'terms' | 'support' | null
  const [copiedEmail, setCopiedEmail] = useState(false);
  const [ticketCategory, setTicketCategory] = useState('Challenge Test Issue');
  const [ticketEmail, setTicketEmail] = useState('');
  const [ticketMessage, setTicketMessage] = useState('');
  const [isSubmittingTicket, setIsSubmittingTicket] = useState(false);
  const [ticketSubmittedId, setTicketSubmittedId] = useState(null);
  const [openFaq, setOpenFaq] = useState(null);

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setActiveModal(null);
      }
    };
    if (activeModal) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [activeModal]);

  const handleCopyEmail = () => {
    navigator.clipboard.writeText('support@buggyman.dev');
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2000);
  };

  const handleSubmitTicket = (e) => {
    e.preventDefault();
    if (!ticketMessage.trim()) return;
    setIsSubmittingTicket(true);
    setTimeout(() => {
      setIsSubmittingTicket(false);
      setTicketSubmittedId(`BM-${Math.floor(10000 + Math.random() * 90000)}`);
      setTicketMessage('');
      setTicketEmail('');
    }, 600);
  };

  const faqs = [
    {
      q: 'How does code evaluation work in BuggyMan?',
      a: 'All submitted code executes inside secure, isolated sandbox micro-containers with strict memory, timeout, and CPU resource limits to protect security and provide deterministic test results.'
    },
    {
      q: 'How are PvP matchmaking ratings (MMR) computed?',
      a: 'Ratings utilize an adjusted Elo system. You gain or lose MMR based on the outcome of head-to-head matches against opponents of differing rating tiers, with bonus XP for win streaks.'
    },
    {
      q: 'What are BugBytes and how can I earn them?',
      a: 'BugBytes are virtual platform credits used to unlock progressive AI hints and challenge features. You earn BugBytes by solving challenges, maintaining daily streaks, or winning PvP duels.'
    },
    {
      q: 'Can I report broken test cases or outdated challenges?',
      a: 'Yes! Use the Support Desk form below or submit an issue report directly from the problem statement panel inside the code editor.'
    }
  ];

  return (
    <>
      <footer className="border-t border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md py-6 px-6 text-center transition-colors duration-200">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400 font-medium">
          <p>© {new Date().getFullYear()} BuggyMan AI Labs. All rights reserved.</p>
          
          <div className="flex items-center gap-6">
            <button
              type="button"
              onClick={() => setActiveModal('privacy')}
              className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors cursor-pointer font-medium"
            >
              Privacy Policy
            </button>
            <span className="text-slate-300 dark:text-slate-700 select-none">•</span>
            <button
              type="button"
              onClick={() => setActiveModal('terms')}
              className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors cursor-pointer font-medium"
            >
              Terms and Services
            </button>
            <span className="text-slate-300 dark:text-slate-700 select-none">•</span>
            <button
              type="button"
              onClick={() => setActiveModal('support')}
              className="hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors cursor-pointer font-medium"
            >
              Support Desk
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <p>System Version 1.2.0-beta</p>
          </div>
        </div>
      </footer>

      {/* MODAL DIALOG */}
      {activeModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fade-in"
          onClick={(e) => {
            if (e.target === e.currentTarget) setActiveModal(null);
          }}
        >
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl relative overflow-hidden animate-slide-up">
            
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4 bg-slate-50/50 dark:bg-slate-900/50">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-600 dark:text-cyan-400">
                  {activeModal === 'privacy' && <Lock className="w-5 h-5" />}
                  {activeModal === 'terms' && <Scale className="w-5 h-5" />}
                  {activeModal === 'support' && <Headphones className="w-5 h-5" />}
                </div>
                <div>
                  <h3 className="text-lg font-heading font-bold text-slate-900 dark:text-slate-100">
                    {activeModal === 'privacy' && 'Privacy Policy'}
                    {activeModal === 'terms' && 'Terms and Services'}
                    {activeModal === 'support' && 'BuggyMan Support Desk'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {activeModal === 'privacy' && 'How we protect, store, and respect your code and data.'}
                    {activeModal === 'terms' && 'Rules, intellectual property, and community guidelines.'}
                    {activeModal === 'support' && 'Get assistance with challenges, matchmaking, or platform tools.'}
                  </p>
                </div>
              </div>

              {/* Close Button */}
              <button
                onClick={() => setActiveModal(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Nav Tabs for Quick Switching */}
            <div className="flex items-center gap-2 px-6 pt-3 pb-1 border-b border-slate-100 dark:border-slate-800/60 bg-white dark:bg-slate-900 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setActiveModal('privacy')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeModal === 'privacy'
                    ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Privacy</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveModal('terms')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeModal === 'terms'
                    ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Terms</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveModal('support')}
                className={`px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeModal === 'support'
                    ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
                }`}
              >
                <Headphones className="w-3.5 h-3.5" />
                <span>Support Desk</span>
              </button>
            </div>

            {/* Scrollable Content Area */}
            <div className="p-6 overflow-y-auto space-y-6 text-slate-600 dark:text-slate-300 text-xs leading-relaxed">
              
              {/* TAB 1: PRIVACY POLICY */}
              {activeModal === 'privacy' && (
                <div className="space-y-5 animate-fade-in">
                  <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-700 dark:text-cyan-300 text-xs">
                    <p className="font-semibold">Security Pledge</p>
                    <p className="mt-0.5 text-[11px] opacity-90">
                      We treat developer code and personal identity with the highest level of security. Your solutions are evaluated in ephemeral sandboxes and are never sold or trained on.
                    </p>
                  </div>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                      1. Information We Collect
                    </h4>
                    <p>
                      When you create an account, we collect your display name, email address, hashed credentials, and optional profile avatar. When you complete challenges or enter PvP arenas, we log execution test results, solve durations, and XP points to maintain your leaderboard position and career suitability profiler.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                      2. Sandbox Code Privacy
                    </h4>
                    <p>
                      Code snippets submitted to the BuggyMan evaluator run inside strictly isolated micro-environments. Once test evaluation finishes, the execution container is destroyed. We do not use your proprietary or submitted code for public machine learning models or third-party syndication.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                      3. Cookies & Session Storage
                    </h4>
                    <p>
                      We utilize local storage and secure HTTP tokens strictly to maintain your logged-in session, remember your editor preferences (such as auto-save and tab size), and persist your chosen dark/light color theme.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                      4. Your Data Rights
                    </h4>
                    <p>
                      You retain full rights to your data. You may update your profile details, clear your notification archives, or request full account deletion at any time by contacting our privacy officer at <span className="font-mono text-cyan-600 dark:text-cyan-400 font-semibold">privacy@buggyman.dev</span>.
                    </p>
                  </section>
                </div>
              )}

              {/* TAB 2: TERMS OF SERVICE */}
              {activeModal === 'terms' && (
                <div className="space-y-5 animate-fade-in">
                  <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-700 dark:text-purple-300 text-xs">
                    <p className="font-semibold">Developer Code of Conduct</p>
                    <p className="mt-0.5 text-[11px] opacity-90">
                      BuggyMan is designed as a fair, competitive, and supportive community for debugging skills. Sportsmanship and fair play are required.
                    </p>
                  </div>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                      1. Acceptance of Terms
                    </h4>
                    <p>
                      By registering an account, writing code in the BuggyMan editor, or engaging in live multiplayer PvP duels, you agree to comply with and be legally bound by these Terms of Service.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                      2. Fair Play & Security Sandbox Integrity
                    </h4>
                    <p>
                      You agree not to bypass sandbox runtime restrictions, attempt denial-of-service against test clusters, use automated bots in PvP battles, or manipulate network traffic to artificially inflate leaderboard standings. Violations will result in permanent account suspension.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                      3. Intellectual Property
                    </h4>
                    <p>
                      You own all intellectual property rights to the unique source code and fixes you compose. BuggyMan AI Labs retains exclusive rights to the platform design, challenge definitions, test suites, AI hint algorithms, and visual branding.
                    </p>
                  </section>

                  <section className="space-y-1.5">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                      4. BugBytes & Virtual Currency
                    </h4>
                    <p>
                      BugBytes and XP are non-transferable digital credits solely intended to unlock platform progression, hint tiers, and cosmetic badges. They have no cash equivalency outside of simulated platform rewards.
                    </p>
                  </section>
                </div>
              )}

              {/* TAB 3: SUPPORT DESK */}
              {activeModal === 'support' && (
                <div className="space-y-6 animate-fade-in">
                  
                  {/* Direct Contact Banner */}
                  <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
                        <Mail className="w-5 h-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-slate-900 dark:text-slate-100">Direct Developer Support</p>
                        <p className="text-[11px] text-slate-500 font-mono">support@buggyman.dev</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 w-full sm:w-auto">
                      <button
                        type="button"
                        onClick={handleCopyEmail}
                        className="button-secondary text-xs px-3 py-1.5 flex items-center justify-center gap-1.5 flex-1 sm:flex-initial"
                      >
                        {copiedEmail ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-500" />
                            <span className="text-emerald-600 dark:text-emerald-400 font-bold">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy Email</span>
                          </>
                        )}
                      </button>
                      <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full border border-emerald-500/20 whitespace-nowrap">
                        Avg response &lt; 24h
                      </span>
                    </div>
                  </div>

                  {/* Quick Support Ticket Form */}
                  <div className="space-y-3">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <Send className="w-4 h-4 text-cyan-500" />
                      <span>Submit a Support Ticket</span>
                    </h4>

                    {ticketSubmittedId ? (
                      <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 space-y-1">
                        <div className="flex items-center gap-2 font-bold text-xs">
                          <Check className="w-4 h-4 text-emerald-500" />
                          <span>Ticket #{ticketSubmittedId} Submitted Successfully!</span>
                        </div>
                        <p className="text-[11px] opacity-90">
                          Thank you for reaching out. Our engineering team has logged this request and will follow up shortly.
                        </p>
                        <button
                          type="button"
                          onClick={() => setTicketSubmittedId(null)}
                          className="mt-2 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 underline hover:opacity-80"
                        >
                          Submit another inquiry
                        </button>
                      </div>
                    ) : (
                      <form onSubmit={handleSubmitTicket} className="space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                              Inquiry Category
                            </label>
                            <select
                              value={ticketCategory}
                              onChange={(e) => setTicketCategory(e.target.value)}
                              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:border-cyan-500"
                            >
                              <option>Challenge Test Issue</option>
                              <option>PvP Matchmaking & Rating</option>
                              <option>BugBytes & Store Rewards</option>
                              <option>Account & Login Issues</option>
                              <option>Feature Request / Feedback</option>
                            </select>
                          </div>
                          <div>
                            <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                              Your Email (Optional)
                            </label>
                            <input
                              type="email"
                              value={ticketEmail}
                              onChange={(e) => setTicketEmail(e.target.value)}
                              placeholder="developer@example.com"
                              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-cyan-500"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                            Describe the problem or question
                          </label>
                          <textarea
                            rows={3}
                            value={ticketMessage}
                            onChange={(e) => setTicketMessage(e.target.value)}
                            placeholder="Provide details about what happened, steps to reproduce, or your question..."
                            required
                            className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-xs text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-cyan-500"
                          />
                        </div>

                        <div className="flex justify-end">
                          <button
                            type="submit"
                            disabled={isSubmittingTicket || !ticketMessage.trim()}
                            className="button-primary text-xs px-4 py-2 flex items-center gap-2 disabled:opacity-50"
                          >
                            <Send className="w-3.5 h-3.5" />
                            <span>{isSubmittingTicket ? 'Sending Ticket...' : 'Send Message'}</span>
                          </button>
                        </div>
                      </form>
                    )}
                  </div>

                  {/* Common FAQs Accordion */}
                  <div className="space-y-3 pt-2">
                    <h4 className="font-heading font-bold text-sm text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <HelpCircle className="w-4 h-4 text-cyan-500" />
                      <span>Frequently Asked Questions</span>
                    </h4>

                    <div className="space-y-2">
                      {faqs.map((faq, idx) => (
                        <div
                          key={idx}
                          className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden bg-slate-50/50 dark:bg-slate-950/40"
                        >
                          <button
                            type="button"
                            onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                            className="w-full p-3 text-left font-semibold text-slate-900 dark:text-slate-200 flex items-center justify-between gap-3 hover:bg-slate-100/50 dark:hover:bg-slate-900/50 transition-colors"
                          >
                            <span>{faq.q}</span>
                            {openFaq === idx ? (
                              <ChevronUp className="w-4 h-4 text-slate-400 shrink-0" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-slate-400 shrink-0" />
                            )}
                          </button>
                          {openFaq === idx && (
                            <div className="p-3 pt-0 text-slate-600 dark:text-slate-400 text-xs border-t border-slate-100 dark:border-slate-800/60 mt-1 leading-relaxed">
                              {faq.a}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              )}

            </div>

            {/* Modal Footer Action */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 flex items-center justify-between gap-4">
              <span className="text-[11px] text-slate-400">
                Press <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-[10px] font-mono">Esc</kbd> to close
              </span>
              <button
                type="button"
                onClick={() => setActiveModal(null)}
                className="button-secondary text-xs px-4 py-2"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
