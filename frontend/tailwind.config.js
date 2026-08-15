/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // support light/dark toggling
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
      },
      colors: {
        brand: {
          blue: 'var(--brand-accent)',
          sky: 'var(--brand-accent)',
          cyan: 'var(--brand-accent)',
          emerald: 'var(--color-success)',
          rose: 'var(--color-error)',
          amber: 'var(--color-warning)',
        }
      },
      boxShadow: {
        'glow-blue': '0 0 24px -2px var(--brand-accent-bg)',
        'glow-cyan': '0 0 24px -2px var(--brand-accent-bg)',
        'glow-emerald': '0 0 24px -2px var(--color-success-bg)',
        'glass': 'var(--card-shadow)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'slide-up': 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-glow': 'pulseGlow 2s infinite ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(12px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.6', filter: 'brightness(1)' },
          '50%': { opacity: '1', filter: 'brightness(1.2) drop-shadow(0 0 8px var(--brand-accent-bg))' },
        }
      }
    },
  },
  plugins: [],
}
