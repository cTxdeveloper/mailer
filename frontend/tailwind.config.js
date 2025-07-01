/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./nuxt.config.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        'obsidian-black': '#101014',
        'pure-white': '#FFFFFF',
        'quantum-purple': '#7F5AF0',
        'guardian-green': '#2CB67D',
        'danger-red': '#EF4444', // For errors or warnings
        'warning-yellow': '#F59E0B', // For warnings
        'glass-bg': 'rgba(18, 18, 22, 0.5)', // For glassmorphism effect
        'overlay-bg': 'rgba(0, 0, 0, 0.75)', // For modal overlays
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Using Inter as the primary sans-serif font
        display: ['Satoshi', 'sans-serif'], // Using Satoshi for headings/display text
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'glow-purple-sm': '0 0 8px 2px rgba(127, 90, 240, 0.5)',
        'glow-purple-md': '0 0 12px 4px rgba(127, 90, 240, 0.5)',
        'glow-green-sm': '0 0 8px 2px rgba(44, 182, 125, 0.5)',
        'card-hover': '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'fade-in-up': 'fadeInUp 0.6s ease-out forwards',
        'slide-in-left': 'slideInLeft 0.5s ease-out forwards',
        'pulse-glow': 'pulseGlow 2s infinite ease-in-out',
        'nexus-assemble': 'nexusAssemble 1.5s ease-out forwards',
        'orb-flow': 'orbFlow 2s ease-in-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-30px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(127, 90, 240, 0.2)' },
          '50%': { boxShadow: '0 0 20px 10px rgba(127, 90, 240, 0.7)' },
        },
        nexusAssemble: {
          '0%': { opacity: '0', transform: 'scale(0.5) rotate(-45deg)' },
          '100%': { opacity: '1', transform: 'scale(1) rotate(0deg)' },
        },
        orbFlow: {
          '0%': { transform: 'translateX(0) scale(1)', opacity: '1' },
          '50%': { transform: 'translateX(50px) scale(0.8)', opacity: '0.7' },
          '100%': { transform: 'translateX(100px) scale(0.5)', opacity: '0' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // For basic form styling resets
  ],
}
