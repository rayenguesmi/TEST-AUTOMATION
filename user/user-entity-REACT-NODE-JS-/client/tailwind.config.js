/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#22d3ee',
          hover: '#67e8f9',
          muted: 'rgba(34, 211, 238, 0.12)',
        },
        ai: {
          DEFAULT: '#a855f7',
          muted: 'rgba(168, 85, 247, 0.12)',
        },
        surface: {
          base: '#0a0e1a',
          raised: '#0d1220',
          overlay: '#111827',
        },
      },
      fontFamily: {
        sans: ['Space Grotesk', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm': '6px',
        'md': '10px',
        'lg': '14px',
        'xl': '20px',
        '2xl': '24px',
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.3s ease forwards',
        'shimmer': 'shimmer 1.8s infinite linear',
        'pulse-dot': 'pulse-dot 1.5s ease-in-out infinite',
        'spin-slow': 'spin-slow 1.5s linear infinite',
        'ai-pulse': 'ai-pulse 2s ease-in-out infinite',
        'cyber-glow': 'cyber-glow 2.5s ease-in-out infinite',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(34,211,238,0.3)',
        'glow-cyan-lg': '0 0 40px rgba(34,211,238,0.4)',
        'glow-ai': '0 0 24px rgba(168,85,247,0.25)',
        'card': '0 1px 3px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)',
      },
    },
  },
  plugins: [],
}
