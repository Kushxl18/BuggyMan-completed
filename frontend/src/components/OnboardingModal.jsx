import React, { useState } from 'react';
import { 
  Bug, 
  Code2, 
  Database, 
  Palette, 
  Play, 
  Send, 
  Sparkles, 
  Trophy, 
  CheckCircle2, 
  ChevronRight, 
  ChevronLeft, 
  X 
} from 'lucide-react';

const STEPS = [
  {
    id: 1,
    title: 'Welcome to BuggyMan',
    subtitle: 'The AI-Powered Debugging & Software Engineering Lab',
    icon: Bug,
    iconColor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    content: (
      <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
        <p>
          BuggyMan is a specialized hands-on platform built to master full-stack software debugging, error diagnosis, and code repair.
        </p>
        <p>
          Instead of building applications from scratch, you will inspect real buggy templates, identify root causes, and submit working solutions verified by automated sandboxes.
        </p>
      </div>
    )
  },
  {
    id: 2,
    title: 'The 3 Debugging Arenas',
    subtitle: 'Explore specialized environments for full-stack skills',
    icon: Code2,
    iconColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    content: (
      <div className="grid grid-cols-3 gap-2.5 text-xs">
        <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5 text-center">
          <Code2 className="w-5 h-5 text-blue-400 mx-auto" />
          <h4 className="font-bold text-slate-200">Code Lab</h4>
          <p className="text-[10px] text-slate-400">React, Node.js, Python logic & state bugs.</p>
        </div>
        <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5 text-center">
          <Database className="w-5 h-5 text-amber-400 mx-auto" />
          <h4 className="font-bold text-slate-200">SQL Lab</h4>
          <p className="text-[10px] text-slate-400">Queries, JOINs, schema & index fixes.</p>
        </div>
        <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1.5 text-center">
          <Palette className="w-5 h-5 text-emerald-400 mx-auto" />
          <h4 className="font-bold text-slate-200">Frontend Studio</h4>
          <p className="text-[10px] text-slate-400">Flexbox, Grid, CSS & UI responsiveness.</p>
        </div>
      </div>
    )
  },
  {
    id: 3,
    title: 'Run vs. Submit',
    subtitle: 'Evaluate your code before recording your submission',
    icon: Play,
    iconColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    content: (
      <div className="space-y-3 text-xs">
        <div className="p-3 rounded-xl bg-slate-950 border border-cyan-500/30 flex items-start gap-3">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 shrink-0">
            <Play className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-cyan-300">Run Code</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Runs unit tests inside isolated sandboxes without penalty. Use this to verify fix ideas.</p>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950 border border-blue-500/30 flex items-start gap-3">
          <div className="p-1.5 rounded-lg bg-blue-500/10 text-blue-400 shrink-0">
            <Send className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-blue-300">Submit Solution</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Records your official submission, calculates XP points, updates streaks, and logs rankings.</p>
          </div>
        </div>
      </div>
    )
  },
  {
    id: 4,
    title: 'AI Intelligence Suite',
    subtitle: 'Multi-level hints, diagnostic feedback & solution explanations',
    icon: Sparkles,
    iconColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    content: (
      <div className="space-y-2.5 text-xs text-slate-300">
        <div className="flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span><strong>Graduated AI Hints:</strong> Conceptual hints $\rightarrow$ Targeted direction $\rightarrow$ Solution clues.</span>
        </div>
        <div className="flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span><strong>AI Diagnostic Feedback:</strong> Analyzes failed test outputs and pinpoints likely code defects.</span>
        </div>
        <div className="flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span><strong>Solution Explainer:</strong> Step-by-step breakdown of why the bug occurred and how to prevent it.</span>
        </div>
      </div>
    )
  },
  {
    id: 5,
    title: 'XP, Streaks & Leaderboards',
    subtitle: 'Earn points, climb ranks, and track your proficiency',
    icon: Trophy,
    iconColor: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
    content: (
      <div className="space-y-3 text-xs text-slate-300 text-center">
        <p>
          Every solved challenge rewards XP based on difficulty. Maintain your daily streak to earn bonus badges and climb global and college leaderboards!
        </p>
        <div className="p-3 bg-gradient-to-r from-blue-600/20 to-cyan-500/20 border border-blue-500/30 rounded-xl text-cyan-300 font-bold">
          Ready to solve your first bug? Let's get started!
        </div>
      </div>
    )
  }
];

export default function OnboardingModal({ isOpen, onClose }) {
  const [currentStep, setCurrentStep] = useState(0);

  if (!isOpen) return null;

  const step = STEPS[currentStep];
  const IconComp = step.icon;

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      localStorage.setItem('buggyman_onboarding_completed', 'true');
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSkip = () => {
    localStorage.setItem('buggyman_onboarding_completed', 'true');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 md:p-8 space-y-6 shadow-2xl relative overflow-hidden">
        {/* Top Glow */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-blue-500/10 blur-3xl pointer-events-none" />

        {/* Header Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
            <span>Step {currentStep + 1} of {STEPS.length}</span>
          </div>
          <button
            onClick={handleSkip}
            className="p-1 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors"
            title="Skip Onboarding"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Step Icon & Title */}
        <div className="space-y-3">
          <div className={`p-3.5 rounded-2xl border w-fit ${step.iconColor} shadow-glow-blue/20`}>
            <IconComp className="w-7 h-7" />
          </div>
          <div>
            <h3 className="font-heading font-extrabold text-xl text-slate-100">{step.title}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{step.subtitle}</p>
          </div>
        </div>

        {/* Step Content */}
        <div className="py-2 min-h-[120px]">
          {step.content}
        </div>

        {/* Stepper Dots & Navigation Buttons */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          {/* Progress dots */}
          <div className="flex items-center gap-1.5">
            {STEPS.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => setCurrentStep(idx)}
                className={`h-2 rounded-full transition-all ${
                  idx === currentStep ? 'w-6 bg-blue-500' : 'w-2 bg-slate-800 hover:bg-slate-700'
                }`}
                title={`Go to step ${idx + 1}`}
              />
            ))}
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            {currentStep > 0 && (
              <button
                onClick={handlePrev}
                className="flex items-center gap-1 px-3 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 bg-slate-800/60 hover:bg-slate-800 rounded-xl transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
            )}

            <button
              onClick={handleNext}
              className="flex items-center gap-1.5 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg transition-all active:scale-95"
            >
              <span>{currentStep === STEPS.length - 1 ? 'Get Started' : 'Next'}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
