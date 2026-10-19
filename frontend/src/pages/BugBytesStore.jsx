import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Bug, 
  ShoppingBag, 
  Sparkles, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  RotateCcw, 
  X, 
  Loader2, 
  Award, 
  Zap, 
  CreditCard,
  Gift,
  HelpCircle,
  FileText,
  QrCode,
  Smartphone,
  Building,
  Check,
  AlertCircle,
  Receipt,
  Wallet
} from 'lucide-react';
import { storeService } from '../services/storeService';
import LoadingSpinner from '../components/LoadingSpinner';

export default function BugBytesStore({ user, setUser, addToast }) {
  const [packages, setPackages] = useState([]);
  const [balance, setBalance] = useState(user?.bugbytes_balance ?? user?.bugbytesBalance ?? 0);
  const [loading, setLoading] = useState(true);
  
  // Checkout modal state
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [checkoutSession, setCheckoutSession] = useState(null);
  const [isProcessingCheckout, setIsProcessingCheckout] = useState(false);
  const [checkoutOutcome, setCheckoutOutcome] = useState(null); // 'SUCCESS' | 'FAILED' | null
  const [startMissionChecked, setStartMissionChecked] = useState(true);

  // Tabbed Payment Simulation state
  const [checkoutPaymentMethod, setCheckoutPaymentMethod] = useState('upi'); // 'upi' | 'card' | 'netbanking'
  const [simUpiApp, setSimUpiApp] = useState('gpay'); // 'gpay' | 'phonepe' | 'paytm' | 'bhim'
  const [simUpiId, setSimUpiId] = useState('developer@okhdfcbank');
  const [simCardNumber, setSimCardNumber] = useState('4532 8921 7734 1029');
  const [simCardExpiry, setSimCardExpiry] = useState('08/28');
  const [simCardCvv, setSimCardCvv] = useState('742');
  const [simBank, setSimBank] = useState('HDFC Bank');

  // Refund modal state
  const [refundTarget, setRefundTarget] = useState(null); // purchase object
  const [refundReason, setRefundReason] = useState('');
  const [isProcessingRefund, setIsProcessingRefund] = useState(false);
  const [refundResult, setRefundResult] = useState(null);

  // Missions & History state
  const [activeTab, setActiveTab] = useState('packages'); // 'packages' | 'missions' | 'purchases' | 'rewards'
  const [missionsData, setMissionsData] = useState({ missions: [], activeMissions: [], completedMissions: [], claimedMissions: [], expiredMissions: [] });
  const [purchases, setPurchases] = useState([]);
  const [rewardsSummary, setRewardsSummary] = useState(null);
  const [claimingMissionId, setClaimingMissionId] = useState(null);
  const [claimResult, setClaimResult] = useState(null);

  const loadStoreData = async () => {
    try {
      setLoading(true);
      const [pkgRes, misRes, purRes, rewRes] = await Promise.allSettled([
        storeService.getPackages(),
        storeService.getMissions(),
        storeService.getPurchases(),
        storeService.getRewardsSummary()
      ]);

      if (pkgRes.status === 'fulfilled' && pkgRes.value) {
        setPackages(pkgRes.value.packages || []);
        if (typeof pkgRes.value.userBalance === 'number') {
          setBalance(pkgRes.value.userBalance);
        }
      }

      if (misRes.status === 'fulfilled' && misRes.value) {
        setMissionsData(misRes.value);
      }

      if (purRes.status === 'fulfilled' && purRes.value) {
        setPurchases(purRes.value.purchases || []);
      }

      if (rewRes.status === 'fulfilled' && rewRes.value) {
        setRewardsSummary(rewRes.value);
      }
    } catch (err) {
      if (addToast) addToast('Failed to load some store data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStoreData();
  }, []);

  useEffect(() => {
    if (user) {
      setBalance(user.bugbytes_balance ?? user.bugbytesBalance ?? 0);
    }
  }, [user]);

  const handleOpenCheckout = async (pkg) => {
    try {
      setSelectedPackage(pkg);
      setCheckoutOutcome(null);
      setIsProcessingCheckout(true);

      const res = await storeService.createCheckout(pkg.id);
      setCheckoutSession(res);
    } catch (err) {
      if (addToast) addToast(err?.message || 'Could not initiate demo checkout.', 'error');
      setSelectedPackage(null);
    } finally {
      setIsProcessingCheckout(false);
    }
  };

  const handleSimulatePayment = async (outcome) => {
    if (!checkoutSession?.purchase?.transactionReference) return;

    try {
      setIsProcessingCheckout(true);
      const payload = {
        transactionReference: checkoutSession.purchase.transactionReference,
        simulateOutcome: outcome,
        startMission: startMissionChecked,
        failureReason: outcome === 'FAILURE' ? 'Simulated Card/UPI Decline (Academic Test)' : undefined
      };

      const res = await storeService.confirmPayment(payload);

      if (outcome === 'SUCCESS' && res.success) {
        setCheckoutOutcome({
          status: 'SUCCESS',
          message: res.message,
          purchase: res.purchase,
          newBalance: res.newBalance,
          rewardMission: res.rewardMission
        });

        setBalance(res.newBalance);
        if (typeof setUser === 'function') {
          setUser(prev => prev ? { ...prev, bugbytes_balance: res.newBalance, bugbytesBalance: res.newBalance } : prev);
        }
        if (addToast) addToast(`Simulated Payment Success! +${res.purchase?.bugbytesAmount} BugBytes credited.`, 'success');
        
        // Refresh missions and purchases lists
        const [misRes, purRes] = await Promise.allSettled([
          storeService.getMissions(),
          storeService.getPurchases()
        ]);
        if (misRes.status === 'fulfilled') setMissionsData(misRes.value);
        if (purRes.status === 'fulfilled') setPurchases(purRes.value.purchases || []);

      } else {
        setCheckoutOutcome({
          status: 'FAILED',
          message: res.message || 'Simulated payment was declined.',
          failureReason: res.failureReason || 'Simulated decline test'
        });
        if (addToast) addToast('Simulated payment failed. No BugBytes credited.', 'warning');
      }
    } catch (err) {
      if (addToast) addToast(err?.message || 'Error confirming payment simulation.', 'error');
    } finally {
      setIsProcessingCheckout(false);
    }
  };

  const handleClaimReward = async (missionId) => {
    try {
      setClaimingMissionId(missionId);
      const res = await storeService.claimReward(missionId);
      if (res.success) {
        setClaimResult(res);
        if (addToast) addToast(`Simulated refund of ₹${res.rewardTransaction?.rewardAmountInr} issued!`, 'success');
        // Refresh missions and rewards summary
        const [misRes, rewRes] = await Promise.allSettled([
          storeService.getMissions(),
          storeService.getRewardsSummary()
        ]);
        if (misRes.status === 'fulfilled') setMissionsData(misRes.value);
        if (rewRes.status === 'fulfilled') setRewardsSummary(rewRes.value);
      }
    } catch (err) {
      if (addToast) addToast(err?.message || 'Could not claim reward.', 'error');
    } finally {
      setClaimingMissionId(null);
    }
  };

  const handleOpenRefundModal = (purchase) => {
    setRefundTarget(purchase);
    setRefundReason('');
    setRefundResult(null);
  };

  const handleProcessRefund = async () => {
    if (!refundTarget) return;
    try {
      setIsProcessingRefund(true);
      const res = await storeService.refundPurchase(refundTarget.id, refundReason);
      if (res.success) {
        setRefundResult(res);
        setBalance(res.newBalance);
        if (typeof setUser === 'function') {
          setUser(prev => prev ? { ...prev, bugbytes_balance: res.newBalance, bugbytesBalance: res.newBalance } : prev);
        }
        if (addToast) addToast(`Simulated refund of ₹${res.purchase?.refundAmountInr || refundTarget.priceInr} processed!`, 'success');

        // Refresh purchases & store data
        const [purRes, misRes, rewRes] = await Promise.allSettled([
          storeService.getPurchases(),
          storeService.getMissions(),
          storeService.getRewardsSummary()
        ]);
        if (purRes.status === 'fulfilled') setPurchases(purRes.value.purchases || []);
        if (misRes.status === 'fulfilled') setMissionsData(misRes.value);
        if (rewRes.status === 'fulfilled') setRewardsSummary(rewRes.value);
      }
    } catch (err) {
      if (addToast) addToast(err?.message || 'Could not process refund.', 'error');
    } finally {
      setIsProcessingRefund(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const activeMissionsCount = missionsData.activeMissions?.length || 0;
  const claimableCount = missionsData.completedMissions?.length || 0;

  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-primary)] p-4 md:p-8 space-y-8 max-w-7xl mx-auto">

      {/* Hero Header & BugBytes Balance Summary */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 glass-panel p-6 rounded-3xl">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <ShoppingBag className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-heading font-extrabold text-[var(--text-primary)] flex items-center gap-2">
                <span>BugBytes Store</span>
                <span className="badge badge-cyan text-[10px]">MOCK STORE</span>
              </h1>
              <p className="text-xs text-[var(--text-secondary)]">
                Purchase virtual BugBytes to unlock AI debugging mentor hints & earn 100% money back through coding missions.
              </p>
            </div>
          </div>
        </div>

        {/* Current Balance & Quick Stats */}
        <div className="flex items-center gap-4 shrink-0">
          <div className="px-5 py-3 rounded-2xl bg-slate-900 border border-amber-500/30 flex items-center gap-3 shadow-lg">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Bug className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Your Balance</span>
              <div className="text-xl font-heading font-extrabold text-amber-400 flex items-center gap-1.5">
                <span>{balance}</span>
                <span className="text-xs font-semibold text-amber-500/80">BugBytes</span>
              </div>
            </div>
          </div>

          {claimableCount > 0 && (
            <button
              onClick={() => setActiveTab('missions')}
              className="px-4 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/40 text-emerald-300 flex items-center gap-2 animate-bounce text-xs font-bold"
            >
              <Gift className="w-4 h-4 text-emerald-400" />
              <span>{claimableCount} Reward Claimable!</span>
            </button>
          )}
        </div>
      </div>

      {/* ZERO BUGBYTES HELPER BANNER */}
      {balance === 0 && (
        <div className="p-5 rounded-2xl border border-cyan-500/30 bg-cyan-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 shrink-0">
              <Zap className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-heading font-bold text-cyan-200">
                You have 0 BugBytes! Don't worry, solving challenges is 100% free.
              </h3>
              <p className="text-xs text-slate-400">
                You can purchase mock BugBytes below to unlock AI debugging hints, or solve challenges to earn BugBytes naturally (+10 Easy, +20 Medium, +35 Hard).
              </p>
            </div>
          </div>
          <Link to="/challenges" className="button-secondary text-xs px-4 py-2 whitespace-nowrap shrink-0 flex items-center gap-1.5">
            <span>Explore Free Challenges</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-[var(--border-color)] pb-2 overflow-x-auto select-none">
        <button
          onClick={() => setActiveTab('packages')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'packages'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-glow-cyan'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
          }`}
        >
          <ShoppingBag className="w-4 h-4" />
          <span>Purchase Packages</span>
        </button>

        <button
          onClick={() => setActiveTab('missions')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 relative ${
            activeTab === 'missions'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-glow-cyan'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
          }`}
        >
          <Award className="w-4 h-4" />
          <span>Money-Back Missions</span>
          {(activeMissionsCount > 0 || claimableCount > 0) && (
            <span className="w-2 h-2 rounded-full bg-emerald-400 absolute top-1.5 right-1.5" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('purchases')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'purchases'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-glow-cyan'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
          }`}
        >
          <CreditCard className="w-4 h-4" />
          <span>Purchase History</span>
        </button>

        <button
          onClick={() => setActiveTab('rewards')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === 'rewards'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-glow-cyan'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
          }`}
        >
          <Gift className="w-4 h-4" />
          <span>Refund & Reward Ledger</span>
        </button>
      </div>

      {/* TAB 1: PACKAGES GRID */}
      {activeTab === 'packages' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-heading font-bold text-[var(--text-primary)]">Select a BugBytes Package</h2>
              <p className="text-xs text-[var(--text-secondary)]">Each purchase includes an optional Money-Back Challenge to recover 100% of your simulated purchase price.</p>
            </div>
            <span className="text-[11px] text-slate-500 font-medium">All prices in INR (₹)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {packages.map((pkg) => {
              const perByteCost = (pkg.price_inr / pkg.bugbytes).toFixed(2);
              return (
                <div 
                  key={pkg.id} 
                  className={`glass-card p-6 rounded-3xl flex flex-col justify-between transition-all duration-300 relative overflow-hidden group ${
  pkg.is_best_value
    ? 'border-cyan-500/50 shadow-glow-cyan ring-1 ring-cyan-500/30'
    : 'hover:border-[var(--brand-cyan)]'
}`}
                >
                  {pkg.is_best_value && (
                    <div className="absolute top-0 right-0 bg-gradient-to-l from-cyan-500 to-blue-600 text-white font-heading font-extrabold text-[9px] uppercase tracking-wider py-1 px-3 rounded-bl-xl shadow-md">
                      Best Value (₹{perByteCost}/🐞)
                    </div>
                  )}

                  <div className="space-y-4">
                    {/* Package Title & BugBytes */}
                    <div className="space-y-1">
                      <span className="text-[10px] text-[var(--text-secondary)] font-bold uppercase tracking-wider block">{pkg.name}</span>
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-heading font-extrabold text-[var(--text-primary)]">{pkg.bugbytes}</span>
                        <span className="text-amber-400 font-bold text-sm flex items-center gap-1">
                          <Bug className="w-4 h-4" /> BugBytes
                        </span>
                      </div>
                      <p className="text-[11px] text-[var(--text-secondary)]">₹{perByteCost} per BugByte credit</p>
                    </div>

                    {/* Price tag */}
                    <div className="py-2.5 px-3.5 rounded-xl bg-[var(--bg-hover)] border border-[var(--border-color)] flex items-center justify-between">
                      <span className="text-xs text-[var(--text-secondary)]">Total Price:</span>
                      <span className="text-xl font-heading font-extrabold text-cyan-400">₹{pkg.price_inr}</span>
                    </div>

                    {/* Money-back Mission Offer */}
                    <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 space-y-1.5">
                      <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-bold font-heading">
                        <Gift className="w-3.5 h-3.5 shrink-0" />
                        <span>100% Money-Back Mission</span>
                      </div>
                      <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">
                        Solve <strong className="text-[var(--color-success)]">{pkg.mission_challenge_count}</strong> {pkg.mission_difficulty} challenges within <strong className="text-[var(--color-success)]">{pkg.mission_days} days</strong> to get a simulated refund of <strong className="text-[var(--color-success)]">₹{pkg.reward_amount_inr}</strong>.
                      </p>
                    </div>
                  </div>

                  {/* Purchase Button */}
                  <div className="mt-6 pt-4 border-t border-slate-800">
                    <button
                      onClick={() => handleOpenCheckout(pkg)}
                      className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                        pkg.is_best_value
                          ? 'button-primary shadow-glow-cyan'
                          : 'button-secondary'
                      }`}
                    >
                      <CreditCard className="w-4 h-4" />
                      <span>Buy for ₹{pkg.price_inr}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 2: MONEY-BACK REWARD MISSIONS */}
      {activeTab === 'missions' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-heading font-bold text-slate-100">Earn Your Money Back Missions</h2>
              <p className="text-xs text-slate-400">Complete assigned challenges before the deadline to earn virtual refunds for your mock purchases.</p>
            </div>
            <Link to="/challenges" className="button-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5">
              <span>Go to Challenges</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Claimable Ready Missions */}
          {missionsData.completedMissions?.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5 font-heading">
                <CheckCircle2 className="w-4 h-4" />
                <span>Requirements Satisfied — Ready to Claim:</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {missionsData.completedMissions.map((m) => (
                  <div key={m.id} className="p-5 rounded-2xl border border-emerald-500/40 bg-emerald-500/10 space-y-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-heading font-bold text-sm text-emerald-300">{m.title}</h4>
                        <p className="text-xs text-slate-300">
                          {m.completed_count}/{m.required_count} {m.required_difficulty} challenges completed.
                        </p>
                      </div>
                      <span className="badge badge-emerald text-[9px]">COMPLETED</span>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-emerald-500/20">
                      <div>
                        <span className="text-[10px] text-slate-400 block uppercase font-bold">Simulated Reward</span>
                        <span className="text-xl font-heading font-extrabold text-emerald-400">₹{m.reward_amount_inr}</span>
                      </div>
                      <button
                        onClick={() => handleClaimReward(m.id)}
                        disabled={claimingMissionId === m.id}
                        className="button-primary bg-emerald-600 hover:bg-emerald-500 text-xs px-4 py-2 font-bold flex items-center gap-2"
                      >
                        {claimingMissionId === m.id ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Claiming...</span>
                          </>
                        ) : (
                          <>
                            <Gift className="w-4 h-4" />
                            <span>Claim ₹{m.reward_amount_inr} Reward</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Active In-Progress Missions */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5 font-heading">
              <Clock className="w-4 h-4" />
              <span>Active Missions ({missionsData.activeMissions?.length || 0}):</span>
            </h3>

            {missionsData.activeMissions?.length === 0 ? (
              <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center space-y-3">
                <Award className="w-8 h-8 text-slate-600 mx-auto" />
                <h4 className="text-sm font-heading font-bold text-slate-300">No Active Missions</h4>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Purchase a BugBytes package to start a Money-Back Challenge and earn 100% of your simulated purchase back!
                </p>
                <button onClick={() => setActiveTab('packages')} className="button-primary text-xs px-4 py-2">
                  Browse Packages
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {missionsData.activeMissions.map((m) => {
                  const progressPct = Math.min(100, Math.round((m.completed_count / m.required_count) * 100));
                  return (
                    <div key={m.id} className="glass-card p-5 rounded-2xl border border-slate-800 bg-slate-900/70 space-y-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-heading font-bold text-sm text-slate-100">{m.title}</h4>
                          <p className="text-[11px] text-slate-400">
                            Required: Solve {m.required_count} {m.required_difficulty} challenges
                          </p>
                        </div>
                        <span className="badge badge-cyan text-[9px]">ACTIVE</span>
                      </div>

                      {/* Progress Bar */}
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400 font-semibold">Progress</span>
                          <span className="font-heading font-extrabold text-cyan-400">
                            {m.completed_count} / {m.required_count} ({progressPct}%)
                          </span>
                        </div>
                        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500" 
                            style={{ width: `${progressPct}%` }}
                          />
                        </div>
                      </div>

                      {/* Remaining Time & Reward info */}
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1.5 text-amber-400 font-semibold">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{m.remainingTimeFormatted} remaining</span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-slate-500 block uppercase font-bold">Reward</span>
                          <span className="font-heading font-bold text-emerald-400">₹{m.reward_amount_inr}</span>
                        </div>
                      </div>

                      <div className="pt-2 flex justify-end">
                        <Link to="/challenges" className="button-secondary text-xs px-3 py-1.5 flex items-center gap-1">
                          <span>Solve Eligible Challenges</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Claimed and Expired Missions Overview */}
          {(missionsData.claimedMissions?.length > 0 || missionsData.expiredMissions?.length > 0) && (
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">Past Missions:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {missionsData.claimedMissions.map((m) => (
                  <div key={m.id} className="p-3.5 rounded-xl border border-slate-800 bg-slate-950 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-300 truncate">{m.title}</span>
                      <span className="badge badge-emerald text-[8px]">REWARD CLAIMED</span>
                    </div>
                    <p className="text-[10px] text-slate-400">Simulated Refund: ₹{m.reward_amount_inr}</p>
                  </div>
                ))}
                {missionsData.expiredMissions.map((m) => (
                  <div key={m.id} className="p-3.5 rounded-xl border border-slate-800 bg-slate-950 text-xs space-y-1 opacity-70">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-400 truncate">{m.title}</span>
                      <span className="badge badge-rose text-[8px]">EXPIRED</span>
                    </div>
                    <p className="text-[10px] text-slate-500">{m.completed_count}/{m.required_count} completed</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: PURCHASE HISTORY */}
      {activeTab === 'purchases' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-heading font-bold text-slate-100">Mock Purchase History</h2>
            <span className="text-xs text-slate-400">{purchases.length} Transactions</span>
          </div>

          {purchases.length === 0 ? (
            <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-slate-400 text-xs">
              No purchase history yet. Complete a mock purchase to view transactions here.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
                  <tr>
                    <th className="p-4">Reference</th>
                    <th className="p-4">Package</th>
                    <th className="p-4">BugBytes</th>
                    <th className="p-4">Amount (₹)</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Date</th>
                    <th className="p-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {purchases.map((p) => {
                    const mission = p.rewardMission;
                    const isRefunded = p.status === 'REFUNDED' || (mission && mission.status === 'CLAIMED');
                    const isMissionCompleted = mission && mission.status === 'COMPLETED';
                    const isMissionActive = mission && mission.status === 'ACTIVE';
                    const isMissionExpired = mission && mission.status === 'EXPIRED';

                    return (
                      <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="p-4 font-mono text-[11px] text-cyan-400 font-semibold">{p.transactionReference}</td>
                        <td className="p-4 font-semibold text-slate-200">{p.packageName}</td>
                        <td className="p-4 text-amber-400 font-bold">+{p.bugbytesAmount} 🐞</td>
                        <td className="p-4 font-bold text-slate-100">₹{p.priceInr}</td>
                        <td className="p-4">
                          <div className="flex flex-col gap-0.5">
                            {isRefunded ? (
                              <>
                                <span className="badge badge-emerald text-[9px] w-fit font-bold">
                                  100% REFUNDED
                                </span>
                                <span className="text-[10px] text-emerald-400/90 font-medium">
                                  ₹{p.refundAmountInr || p.priceInr} returned • Kept 🐞
                                </span>
                              </>
                            ) : isMissionCompleted ? (
                              <>
                                <span className="badge badge-emerald text-[9px] w-fit font-bold animate-pulse">
                                  CHALLENGES SOLVED
                                </span>
                                <span className="text-[10px] text-emerald-400 font-medium">
                                  Eligible for 100% refund!
                                </span>
                              </>
                            ) : isMissionActive ? (
                              <>
                                <span className="badge badge-cyan text-[9px] w-fit font-bold">
                                  MISSION ACTIVE
                                </span>
                                <span className="text-[10px] text-slate-400 font-medium">
                                  {mission.completedCount}/{mission.requiredCount} solved • {mission.remainingTimeFormatted}
                                </span>
                              </>
                            ) : isMissionExpired ? (
                              <>
                                <span className="badge badge-rose text-[9px] w-fit font-bold">
                                  EXPIRED (NO REFUND)
                                </span>
                                <span className="text-[10px] text-slate-500 font-medium">
                                  Deadline missed ({mission.completedCount}/{mission.requiredCount})
                                </span>
                              </>
                            ) : (
                              <span className={`badge ${p.status === 'COMPLETED' ? 'badge-slate' : 'badge-rose'} text-[9px] w-fit font-bold`}>
                                {p.status}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="p-4 text-slate-400">{p.createdAt ? new Date(p.createdAt).toLocaleDateString() : 'N/A'}</td>
                        <td className="p-4 text-right">
                          {isRefunded ? (
                            <div className="flex flex-col items-end">
                              <span className="text-[11px] text-emerald-400 font-bold flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                <span>₹{p.priceInr} Refunded</span>
                              </span>
                              <span className="text-[10px] text-amber-400/80 font-medium">Kept +{p.bugbytesAmount} 🐞</span>
                            </div>
                          ) : isMissionCompleted ? (
                            <button
                              onClick={() => handleOpenRefundModal(p)}
                              className="px-3.5 py-1.5 rounded-xl border border-emerald-500/40 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 text-xs font-bold inline-flex items-center gap-1.5 transition-all shadow-md shadow-emerald-950/40"
                            >
                              <RotateCcw className="w-3.5 h-3.5 text-emerald-300" />
                              <span>Claim ₹{p.priceInr} Refund</span>
                            </button>
                          ) : isMissionActive ? (
                            <button
                              onClick={() => setActiveTab('missions')}
                              className="px-3 py-1.5 rounded-xl border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-semibold inline-flex items-center gap-1.5 transition-all"
                            >
                              <Clock className="w-3.5 h-3.5" />
                              <span>Solve {mission.requiredCount - mission.completedCount} more</span>
                            </button>
                          ) : isMissionExpired ? (
                            <span className="text-[11px] text-slate-500 italic">Non-refundable</span>
                          ) : (
                            <span className="text-[11px] text-slate-600">—</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: REWARD & REFUND LEDGER */}
      {activeTab === 'rewards' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-heading font-bold text-slate-100">Simulated Refund & Reward Ledger</h2>
            <span className="badge badge-cyan text-[10px]">ACADEMIC AUDIT</span>
          </div>

          {/* Financial summary cards */}
          {rewardsSummary && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Total Mock Purchases</span>
                <span className="text-2xl font-heading font-extrabold text-slate-200">₹{rewardsSummary.totalPurchasedInr}</span>
              </div>
              <div className="glass-card p-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/5 space-y-1">
                <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block">Total Simulated Refunds</span>
                <span className="text-2xl font-heading font-extrabold text-emerald-400">₹{rewardsSummary.totalRewardedInr}</span>
              </div>
              <div className="glass-card p-5 rounded-2xl border border-cyan-500/30 bg-cyan-500/5 space-y-1">
                <span className="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block">Net Simulated Cost</span>
                <span className="text-2xl font-heading font-extrabold text-cyan-400">₹{rewardsSummary.netSimulatedCostInr}</span>
              </div>
            </div>
          )}

          {/* Vouchers list */}
          <div className="space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block font-heading">
              Refund Vouchers ({rewardsSummary?.rewards?.length || 0}):
            </span>

            {(!rewardsSummary?.rewards || rewardsSummary.rewards.length === 0) ? (
              <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-slate-500 text-xs">
                No simulated rewards claimed yet. Complete a Money-Back Mission to generate refund vouchers.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rewardsSummary.rewards.map((r) => (
                  <div key={r.id} className="p-5 rounded-2xl border border-emerald-500/30 bg-slate-900/80 space-y-3 relative overflow-hidden">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-2">
                        <Gift className="w-4 h-4 text-emerald-400" />
                        <span className="font-heading font-bold text-xs text-slate-200">Demonstration Refund Voucher</span>
                      </div>
                      <span className="badge badge-emerald text-[9px]">VIRTUAL REFUND</span>
                    </div>

                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Refund Reference:</span>
                        <span className="font-mono text-cyan-400 font-semibold">{r.transactionReference}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Amount Refunded:</span>
                        <span className="font-heading font-extrabold text-emerald-400">₹{r.rewardAmountInr}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Issued On:</span>
                        <span className="text-slate-300">{r.createdAt ? new Date(r.createdAt).toLocaleDateString() : 'N/A'}</span>
                      </div>
                    </div>

                    <p className="text-[10px] text-slate-500 border-t border-slate-800/80 pt-2 leading-relaxed">
                      {r.notes}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* MOCK CHECKOUT MODAL */}
      {selectedPackage && checkoutSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-slate-800 max-w-md w-full rounded-3xl p-6 shadow-2xl space-y-5 relative">
            <button 
              onClick={() => { setSelectedPackage(null); setCheckoutSession(null); }}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            {!checkoutOutcome ? (
              <>
                <div className="space-y-1">
                  <h3 className="font-heading font-bold text-lg text-slate-100 flex items-center gap-2">
                    <ShoppingBag className="w-5 h-5 text-cyan-400" />
                    <span>Mock Checkout</span>
                  </h3>
                  <p className="text-xs text-slate-400">Demonstration purchase prototype</p>
                </div>

                {/* Important Demo Notice */}
                <div className="p-3.5 rounded-xl border border-amber-500/30 bg-amber-500/10 text-xs text-amber-300 space-y-1">
                  <strong className="block font-bold flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>DEMO PAYMENT — NO REAL MONEY CHARGED</span>
                  </strong>
                  <p className="text-[11px] text-slate-300">
                    This order is for academic evaluation only. No real banking details or payment gateways are connected.
                  </p>
                </div>

                {/* Order Summary */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Package:</span>
                    <span className="font-bold text-slate-200">{selectedPackage.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">BugBytes to Credit:</span>
                    <span className="font-bold text-amber-400">+{selectedPackage.bugbytes} 🐞</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Mock Order Ref:</span>
                    <span className="font-mono text-cyan-400 text-[11px]">{checkoutSession.purchase?.transactionReference}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-800 flex justify-between font-bold text-sm">
                    <span className="text-slate-300">Total Price:</span>
                    <span className="text-cyan-400">₹{selectedPackage.price_inr}</span>
                  </div>
                </div>

                {/* 100% Money-Back Guarantee Feature Card */}
                <div className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-cyan-950/40 border border-emerald-500/40 space-y-1.5 shadow-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-emerald-300 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>100% Money-Back Guarantee Included</span>
                    </span>
                    <span className="badge badge-emerald text-[8px] font-bold">100% REFUND</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Solve the required challenges within <strong className="text-cyan-300">{selectedPackage.mission_days || 7} days</strong>. Once completed on time, you receive a <strong>100% refund of ₹{selectedPackage.price_inr}</strong> back to your payment method — and <strong>keep all +{selectedPackage.bugbytes} BugBytes</strong> for free!
                  </p>
                </div>

                {/* Interactive Payment Method Simulation Tabs */}
                <div className="space-y-3 pt-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                      Payment Method
                    </span>
                    <span className="badge badge-cyan text-[8px]">SIMULATION</span>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setCheckoutPaymentMethod('upi')}
                      className={`p-2 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all ${
                        checkoutPaymentMethod === 'upi'
                          ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300 shadow-sm shadow-cyan-500/20'
                          : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <QrCode className="w-4 h-4" />
                      <span className="text-[11px] font-bold">UPI / QR</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setCheckoutPaymentMethod('card')}
                      className={`p-2 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all ${
                        checkoutPaymentMethod === 'card'
                          ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300 shadow-sm shadow-cyan-500/20'
                          : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <CreditCard className="w-4 h-4" />
                      <span className="text-[11px] font-bold">Cards</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setCheckoutPaymentMethod('netbanking')}
                      className={`p-2 rounded-xl border flex flex-col items-center justify-center gap-1 transition-all ${
                        checkoutPaymentMethod === 'netbanking'
                          ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300 shadow-sm shadow-cyan-500/20'
                          : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <Building className="w-4 h-4" />
                      <span className="text-[11px] font-bold">NetBanking</span>
                    </button>
                  </div>

                  {/* UPI Sub-Panel */}
                  {checkoutPaymentMethod === 'upi' && (
                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 space-y-2.5">
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-slate-400 font-semibold">Select UPI App</span>
                        <span className="text-cyan-400 font-bold">Instant Autopay</span>
                      </div>
                      <div className="grid grid-cols-4 gap-1.5 text-center">
                        {[
                          { id: 'gpay', label: 'Google Pay' },
                          { id: 'phonepe', label: 'PhonePe' },
                          { id: 'paytm', label: 'Paytm' },
                          { id: 'bhim', label: 'BHIM UPI' }
                        ].map(app => (
                          <button
                            key={app.id}
                            type="button"
                            onClick={() => setSimUpiApp(app.id)}
                            className={`py-1 px-1 rounded-lg text-[10px] font-bold border transition-all truncate ${
                              simUpiApp === app.id
                                ? 'border-cyan-500 bg-cyan-500/20 text-cyan-300'
                                : 'border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700'
                            }`}
                          >
                            {app.label}
                          </button>
                        ))}
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10px] text-slate-400 block font-medium">Virtual UPI ID / VPA</label>
                        <div className="relative">
                          <input
                            type="text"
                            value={simUpiId}
                            onChange={(e) => setSimUpiId(e.target.value)}
                            className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                            placeholder="username@bank"
                          />
                          <span className="absolute right-2.5 top-2 text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                            <Check className="w-3 h-3" /> Verified
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Card Sub-Panel */}
                  {checkoutPaymentMethod === 'card' && (
                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                      <div className="space-y-1">
                        <div className="flex justify-between items-center text-[10px] text-slate-400">
                          <span>Simulated Card Number</span>
                          <span className="text-[10px] font-bold text-cyan-400">VISA / MASTERCARD</span>
                        </div>
                        <input
                          type="text"
                          value={simCardNumber}
                          onChange={(e) => setSimCardNumber(e.target.value)}
                          className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1">
                          <span className="text-[10px] text-slate-400 block">Valid Thru</span>
                          <input
                            type="text"
                            value={simCardExpiry}
                            onChange={(e) => setSimCardExpiry(e.target.value)}
                            className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                          />
                        </div>
                        <div className="space-y-1">
                          <span className="text-[10px] text-slate-400 block">CVV</span>
                          <input
                            type="password"
                            value={simCardCvv}
                            onChange={(e) => setSimCardCvv(e.target.value)}
                            maxLength={4}
                            className="w-full px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* NetBanking Sub-Panel */}
                  {checkoutPaymentMethod === 'netbanking' && (
                    <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                      <span className="text-[10px] text-slate-400 block font-semibold">Select Bank</span>
                      <div className="grid grid-cols-3 gap-1.5">
                        {['HDFC Bank', 'SBI', 'ICICI Bank', 'Axis Bank', 'Kotak', 'PNB'].map(bank => (
                          <button
                            key={bank}
                            type="button"
                            onClick={() => setSimBank(bank)}
                            className={`py-1.5 px-2 rounded-lg text-[10px] font-bold border truncate transition-all ${
                              simBank === bank
                                ? 'border-cyan-500 bg-cyan-500/20 text-cyan-300'
                                : 'border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700'
                            }`}
                          >
                            {bank}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Simulation Action Buttons */}
                <div className="space-y-2 pt-2">
                  <button
                    onClick={() => handleSimulatePayment('SUCCESS')}
                    disabled={isProcessingCheckout}
                    className="w-full py-3 px-4 rounded-xl button-primary bg-emerald-600 hover:bg-emerald-500 text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40"
                  >
                    {isProcessingCheckout ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Simulating Payment Gateway...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Pay ₹{selectedPackage.price_inr} (Simulate Success)</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleSimulatePayment('FAILURE')}
                    disabled={isProcessingCheckout}
                    className="w-full py-2.5 px-4 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-bold flex items-center justify-center gap-2 transition-all"
                  >
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Test Bank Decline (Simulate Failure)</span>
                  </button>
                </div>
              </>
            ) : checkoutOutcome.status === 'SUCCESS' ? (
              /* Success Result View */
              <div className="text-center space-y-4 py-2">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-lg font-heading font-extrabold text-emerald-400">Simulated Purchase Successful!</h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Credited <strong className="text-amber-400">+{checkoutOutcome.purchase?.bugbytesAmount} BugBytes</strong> to your account.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-left text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-400">New BugBytes Balance:</span>
                    <span className="font-bold text-amber-400">{checkoutOutcome.newBalance} 🐞</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Transaction Reference:</span>
                    <span className="font-mono text-cyan-400 text-[11px]">{checkoutOutcome.purchase?.transactionReference}</span>
                  </div>
                  {checkoutOutcome.rewardMission && (
                    <div className="pt-2 border-t border-slate-800 text-emerald-400 font-bold text-[11px]">
                      ✓ {checkoutOutcome.rewardMission.title} activated!
                    </div>
                  )}
                </div>

                <div className="pt-2 flex gap-3">
                  <button
                    onClick={() => {
                      setSelectedPackage(null);
                      setCheckoutSession(null);
                      setActiveTab('missions');
                    }}
                    className="flex-1 button-primary text-xs py-2.5"
                  >
                    View Active Missions
                  </button>
                  <button
                    onClick={() => {
                      setSelectedPackage(null);
                      setCheckoutSession(null);
                    }}
                    className="button-secondary text-xs py-2.5 px-4"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              /* Failure Result View */
              <div className="text-center space-y-4 py-2">
                <div className="w-12 h-12 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto border border-rose-500/30">
                  <X className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-lg font-heading font-extrabold text-rose-400">Simulated Payment Declined</h4>
                  <p className="text-xs text-slate-400 mt-1">
                    {checkoutOutcome.failureReason || 'Simulated transaction test decline.'}
                  </p>
                </div>
                <p className="text-xs text-slate-500">
                  No BugBytes were credited and no real money was charged.
                </p>
                <div className="pt-2">
                  <button
                    onClick={() => {
                      setSelectedPackage(null);
                      setCheckoutSession(null);
                    }}
                    className="w-full button-secondary text-xs py-2.5"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* REWARD CLAIM CONFIRMATION MODAL */}
      {claimResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-emerald-500/30 max-w-md w-full rounded-3xl p-6 shadow-2xl space-y-5 text-center relative">
            <button 
              onClick={() => setClaimResult(null)}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/40">
              <Gift className="w-7 h-7" />
            </div>

            <div>
              <h3 className="text-xl font-heading font-extrabold text-emerald-400">Money-Back Reward Issued!</h3>
              <p className="text-xs text-slate-300 mt-1">
                You successfully solved all required challenges before the deadline.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-left text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Refund Amount:</span>
                <span className="font-heading font-extrabold text-emerald-400 text-base">
                  ₹{claimResult.rewardTransaction?.rewardAmountInr}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Reward Voucher Ref:</span>
                <span className="font-mono text-cyan-400">{claimResult.rewardTransaction?.transactionReference}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className="badge badge-emerald text-[9px]">SIMULATED SUCCESS</span>
              </div>
            </div>

            <p className="text-[10px] text-amber-400/90 bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20">
              Notice: Prototype demonstration only. This is a simulated virtual refund record for academic grading.
            </p>

            <button
              onClick={() => {
                setClaimResult(null);
                setActiveTab('rewards');
              }}
              className="w-full button-primary text-xs py-2.5"
            >
              View Refund Ledger
            </button>
          </div>
        </div>
      )}

      {/* 100% MONEY-BACK REFUND MODAL */}
      {refundTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
          <div className="bg-slate-900 border border-emerald-500/30 max-w-md w-full rounded-3xl p-6 shadow-2xl space-y-5 relative">
            <button 
              onClick={() => { setRefundTarget(null); setRefundResult(null); }}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            {!refundResult ? (
              <>
                <div className="space-y-1">
                  <h3 className="font-heading font-bold text-lg text-slate-100 flex items-center gap-2">
                    <Gift className="w-5 h-5 text-emerald-400" />
                    <span>Claim 100% Money-Back Refund</span>
                  </h3>
                  <p className="text-xs text-slate-400">You completed the coding mission before the deadline!</p>
                </div>

                {/* Challenge Goal Achieved Banner */}
                <div className="p-3.5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 text-xs text-emerald-300 space-y-1">
                  <strong className="block font-bold flex items-center gap-1.5 text-emerald-400">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>CHALLENGES SOLVED ON TIME</span>
                  </strong>
                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Under the <strong>100% Money-Back Guarantee</strong>, <strong>₹{refundTarget.priceInr}</strong> will be refunded to your original payment method. You keep all <strong>+{refundTarget.bugbytesAmount} BugBytes</strong> as your learning reward!
                  </p>
                </div>

                {/* Calculation breakdown */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Order Reference:</span>
                    <span className="font-mono text-cyan-400 font-semibold">{refundTarget.transactionReference}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Package:</span>
                    <span className="font-semibold text-slate-200">{refundTarget.packageName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Refund Amount (Real Money):</span>
                    <span className="font-heading font-extrabold text-emerald-400 text-base">₹{refundTarget.priceInr}</span>
                  </div>
                  <div className="pt-2 border-t border-slate-800 space-y-1.5">
                    <div className="flex justify-between">
                      <span className="text-slate-400">BugBytes Retained:</span>
                      <span className="font-bold text-amber-400">+{refundTarget.bugbytesAmount} 🐞 (100% Yours to Keep)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">BugBytes Deducted:</span>
                      <span className="font-bold text-emerald-400">0 🐞 (No deduction!)</span>
                    </div>
                    <div className="flex justify-between pt-1 border-t border-slate-800/80 font-bold">
                      <span className="text-slate-300">Your BugBytes Balance:</span>
                      <span className="text-amber-400">{balance} 🐞</span>
                    </div>
                  </div>
                </div>

                {/* Optional Refund Feedback Note */}
                <div className="space-y-1.5">
                  <label className="text-[11px] font-semibold text-slate-400 block">
                    Notes / Feedback (Optional)
                  </label>
                  <textarea
                    value={refundReason}
                    onChange={(e) => setRefundReason(e.target.value)}
                    placeholder="e.g. Loved solving the challenges! Testing refund flow..."
                    rows={2}
                    className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 resize-none"
                  />
                </div>

                {/* Actions */}
                <div className="pt-1 flex gap-2.5">
                  <button
                    type="button"
                    onClick={() => { setRefundTarget(null); setRefundResult(null); }}
                    className="flex-1 button-secondary text-xs py-2.5"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleProcessRefund}
                    disabled={isProcessingRefund}
                    className="flex-1 py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all button-primary bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950/40"
                  >
                    {isProcessingRefund ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Processing Refund...</span>
                      </>
                    ) : (
                      <>
                        <RotateCcw className="w-4 h-4" />
                        <span>Claim ₹{refundTarget.priceInr} Refund</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              /* Refund Success View */
              <div className="text-center space-y-4 py-2">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-lg font-heading font-extrabold text-emerald-400">100% Refund Issued!</h4>
                  <p className="text-xs text-slate-300 mt-1">
                    Refund of <strong className="text-emerald-400">₹{refundResult.purchase?.refundAmountInr || refundTarget.priceInr}</strong> processed back to your payment method.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-left text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Order Reference:</span>
                    <span className="font-mono text-cyan-400 text-[11px]">{refundTarget.transactionReference}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Money Refunded:</span>
                    <span className="font-bold text-emerald-400">₹{refundTarget.priceInr}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">BugBytes Retained:</span>
                    <span className="font-bold text-amber-400">+{refundTarget.bugbytesAmount} 🐞 (Retained)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Your BugBytes Balance:</span>
                    <span className="font-bold text-amber-400">{balance} 🐞</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Status:</span>
                    <span className="badge badge-emerald text-[9px] font-bold">100% REFUNDED</span>
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    onClick={() => {
                      setRefundTarget(null);
                      setRefundResult(null);
                    }}
                    className="w-full button-primary text-xs py-2.5"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
