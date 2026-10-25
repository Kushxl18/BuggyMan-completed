import React, { useState, useEffect, useRef } from 'react';
import authBg from '../assets/buggyman-auth-bg.png';

export default function AuthBackground({ children }) {
  const [mousePos, setMousePos] = useState({ x: -1000, y: -1000 });
  const [isReducedMotion, setIsReducedMotion] = useState(false);

  useEffect(() => {
    // Check reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(mediaQuery.matches);
    const motionHandler = (e) => setIsReducedMotion(e.matches);
    mediaQuery.addEventListener('change', motionHandler);

    // Global smooth window mousemove listener
    const handleWindowMouseMove = (e) => {
      if (mediaQuery.matches) return;
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleWindowMouseMove);
    return () => {
      mediaQuery.removeEventListener('change', motionHandler);
      window.removeEventListener('mousemove', handleWindowMouseMove);
    };
  }, []);

  // Floating glowing purple & violet particles (placed in outer margins)
  const particles = [
    { id: 1, left: '6%', top: '22%', size: 5, duration: 12, delay: 0, color: 'bg-purple-400' },
    { id: 2, left: '12%', top: '65%', size: 6, duration: 16, delay: 2, color: 'bg-violet-400' },
    { id: 3, left: '18%', top: '35%', size: 4, duration: 14, delay: 4, color: 'bg-fuchsia-400' },
    { id: 4, left: '24%', top: '80%', size: 7, duration: 18, delay: 1, color: 'bg-purple-300' },
    { id: 5, left: '76%', top: '24%', size: 5, duration: 13, delay: 3, color: 'bg-violet-300' },
    { id: 6, left: '82%', top: '72%', size: 7, duration: 17, delay: 5, color: 'bg-purple-400' },
    { id: 7, left: '88%', top: '16%', size: 4, duration: 15, delay: 2, color: 'bg-indigo-300' },
    { id: 8, left: '94%', top: '58%', size: 6, duration: 19, delay: 0, color: 'bg-fuchsia-300' },
    { id: 9, left: '15%', top: '12%', size: 5, duration: 20, delay: 6, color: 'bg-purple-300' },
    { id: 10, left: '85%', top: '88%', size: 6, duration: 16, delay: 4, color: 'bg-violet-400' },
    { id: 11, left: '28%', top: '18%', size: 4, duration: 14, delay: 3, color: 'bg-fuchsia-400' },
    { id: 12, left: '72%', top: '82%', size: 5, duration: 17, delay: 1, color: 'bg-indigo-400' },
  ];

  // Neon floating programming symbols
  const codeSymbols = [
    { id: 's1', char: '</>', left: '7%', top: '42%', duration: 14, delay: 1, size: 'text-base', color: 'text-purple-300' },
    { id: 's2', char: '{ }', left: '14%', top: '78%', duration: 18, delay: 4, size: 'text-lg', color: 'text-violet-300' },
    { id: 's3', char: ';', left: '21%', top: '20%', duration: 11, delay: 2, size: 'text-2xl', color: 'text-fuchsia-300' },
    { id: 's4', char: '=>', left: '78%', top: '64%', duration: 15, delay: 3, size: 'text-base', color: 'text-purple-300' },
    { id: 's5', char: '{ }', left: '86%', top: '22%', duration: 19, delay: 0, size: 'text-xl', color: 'text-violet-300' },
    { id: 's6', char: '</>', left: '92%', top: '76%', duration: 16, delay: 5, size: 'text-sm', color: 'text-indigo-300' },
    { id: 's7', char: ';', left: '89%', top: '44%', duration: 13, delay: 2, size: 'text-xl', color: 'text-purple-200' },
  ];

  return (
    <div
      className="dark auth-page min-h-screen relative flex items-center justify-center px-4 py-8 overflow-y-auto bg-slate-950 bg-cover bg-center bg-no-repeat bg-fixed selection:bg-purple-500/30 text-slate-100"
      style={{
        backgroundImage: `url(${authBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Embedded CSS animations & strict dark input enforcement */}
      <style>{`
        /* Enforce dark inputs regardless of system light theme */
        .auth-page input:not([type="checkbox"]):not([type="radio"]) {
          background-color: #0b0f19 !important;
          color: #f8fafc !important;
          border-color: rgba(255, 255, 255, 0.15) !important;
          -webkit-text-fill-color: #f8fafc !important;
        }

        .auth-page input:not([type="checkbox"]):not([type="radio"])::placeholder {
          color: #64748b !important;
        }

        .auth-page input:not([type="checkbox"]):not([type="radio"]):focus {
          border-color: #38bdf8 !important;
          box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.4) !important;
        }

        /* Chrome, Edge, Safari autofill override */
        .auth-page input:-webkit-autofill,
        .auth-page input:-webkit-autofill:hover, 
        .auth-page input:-webkit-autofill:focus, 
        .auth-page input:-webkit-autofill:active {
          background-color: #0b0f19 !important;
          -webkit-box-shadow: 0 0 0 1000px #0b0f19 inset !important;
          -webkit-text-fill-color: #f8fafc !important;
          color: #f8fafc !important;
          caret-color: #f8fafc !important;
          border-color: rgba(255, 255, 255, 0.2) !important;
          transition: background-color 5000s ease-in-out 0s !important;
        }

        @keyframes authParticleFloat {
          0%, 100% {
            transform: translateY(0px) translateX(0px) scale(1);
            opacity: 0.35;
          }
          50% {
            transform: translateY(-35px) translateX(15px) scale(1.15);
            opacity: 0.9;
          }
        }
        @keyframes authSymbolDrift {
          0%, 100% {
            transform: translateY(0px) rotate(0deg);
            opacity: 0.3;
          }
          50% {
            transform: translateY(-25px) rotate(10deg);
            opacity: 0.75;
          }
        }
        @keyframes authAmbientPulse {
          0%, 100% {
            opacity: 0.3;
          }
          50% {
            opacity: 0.6;
          }
        }
        .auth-particle {
          animation: authParticleFloat ease-in-out infinite;
        }
        .auth-symbol {
          animation: authSymbolDrift ease-in-out infinite;
        }
        .auth-ambient {
          animation: authAmbientPulse 8s ease-in-out infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .auth-particle, .auth-symbol, .auth-ambient {
            animation: none !important;
          }
        }
      `}</style>

      {/* 1. Ambient Lighting (Gentle breathing purple & violet ambient wash) */}
      <div 
        className="pointer-events-none fixed inset-0 z-0 auth-ambient transition-opacity duration-1000"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.18), rgba(15, 23, 42, 0.35) 75%)'
        }}
      />

      {/* 2. Interactive Mouse-Following Purple Glow */}
      {!isReducedMotion && mousePos.x >= 0 && (
        <div
          className="pointer-events-none fixed inset-0 z-0 transition-opacity duration-300"
          style={{
            background: `radial-gradient(550px circle at ${mousePos.x}px ${mousePos.y}px, rgba(168, 85, 247, 0.22), rgba(99, 102, 241, 0.08) 40%, transparent 75%)`
          }}
        />
      )}

      {/* 3. Floating Glowing Particles */}
      {!isReducedMotion && (
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          {particles.map((p) => (
            <span
              key={p.id}
              className={`absolute rounded-full ${p.color} auth-particle`}
              style={{
                left: p.left,
                top: p.top,
                width: `${p.size}px`,
                height: `${p.size}px`,
                boxShadow: '0 0 12px rgba(192, 132, 252, 0.9), 0 0 24px rgba(147, 51, 234, 0.6)',
                animationDuration: `${p.duration}s`,
                animationDelay: `${p.delay}s`
              }}
            />
          ))}
        </div>
      )}

      {/* 4. Floating Glowing Programming Symbols */}
      {!isReducedMotion && (
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          {codeSymbols.map((s) => (
            <span
              key={s.id}
              className={`absolute font-mono font-bold select-none auth-symbol ${s.size} ${s.color}`}
              style={{
                left: s.left,
                top: s.top,
                filter: 'drop-shadow(0 0 10px rgba(168, 85, 247, 0.85)) drop-shadow(0 0 20px rgba(139, 92, 246, 0.5))',
                animationDuration: `${s.duration}s`,
                animationDelay: `${s.delay}s`
              }}
            >
              {s.char}
            </span>
          ))}
        </div>
      )}

      {/* 5. Central Authentication Card Viewport */}
      <div className="relative z-10 w-full flex items-center justify-center">
        {children}
      </div>
    </div>
  );
}
