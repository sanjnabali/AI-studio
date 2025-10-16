/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['Fira Code', 'Monaco', 'Cascadia Code', 'Ubuntu Mono', 'monospace'],
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      colors: {
        primary: {
          50: '#fff7ed',
          100: '#ffe4d5',
          200: '#ffd6b5',
          300: '#ffb98a',
          400: '#ff924e',
          500: '#ff6a1a',
          600: '#e65c17',
          700: '#b34713',
          800: '#80320e',
          900: '#4d1d09',
        },
        accent: {
          50: '#fef6fb',
          100: '#fde4f3',
          200: '#fbc2e3',
          300: '#f78ac7',
          400: '#f04fa6',
          500: '#e0117a',
          600: '#c10f6a',
          700: '#900b4e',
          800: '#600832',
          900: '#300416',
        },
        neutral: {
          50: '#f5f5f4',
          100: '#e7e5e4',
          200: '#d6d3d1',
          300: '#a8a29e',
          400: '#78716c',
          500: '#57534e',
          600: '#44403c',
          700: '#292524',
          800: '#1c1917',
          900: '#0c0a09',
        }
      }
    },
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        aistudioDark: {
          "primary": "#00AEEF",
          "primary-focus": "#0096CC",
          "primary-content": "#001018",
          "secondary": "#7F8EA3",
          "accent": "#5CE1E6",
          "neutral": "#1E232A",
          "base-100": "#0D1117",
          "base-200": "#161B22",
          "base-300": "#1F2630",
          "base-content": "#E6EDF3",
          "info": "#00AEEF",
          "success": "#00C853",
          "warning": "#FFAB00",
          "error": "#EF4444",
        }
      },
      "dark",
      "light"
    ],
  },
  darkMode: ['class', '[data-theme="dark"]']
}
