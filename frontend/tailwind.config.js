/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgRoot:     '#0D0D14',
        bgShell:    '#111118',
        glassBg:    'rgba(255,255,255,0.04)',
        glassBorder:'rgba(255,255,255,0.10)',
        
        // Brand / Dashboard System Colors
        brandPink:  '#FF2D6B',
        brandBlue:  '#4A6CF7',
        brandBlueLight: '#6B8EFF',
        brandGreen: '#00D084',
        brandTeal:  '#00E5CC',
        brandPurple:'#9B6DFF',
        brandOrange:'#FF9F43',
        brandRed:   '#FF5252',
        
        // Typography Default
        textPrimary:'#FFFFFF',
        textSecondary:'#B0B8D0',

        // Legacy / Standard App Utility Colors (Required for Sub-pages)
        bg:         '#0A0A12',
        surface:    'rgba(255,255,255,0.03)',
        surfaceAlt: 'rgba(255,255,255,0.06)',
        border:     'rgba(255,255,255,0.09)',
        text:       '#F0F2FF',
        textMuted:  '#4A5070',
        textDim:    '#2A2A3D',
        
        // Utility state colors
        red:        '#FF5252',
        redDim:     'rgba(255,82,82,0.15)',
        green:      '#00D084',
        greenDim:   'rgba(0,208,132,0.15)',
        amber:      '#f0a500',
        amberDim:   'rgba(240,165,0,0.15)',
        blue:       '#4A6CF7',
        purple:     '#9B6DFF',
        purpleDim:  'rgba(155,109,255,0.15)',
      },
      fontFamily: {
        sora: ['Sora', 'sans-serif'],
        dm: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'card': '18px',
        'btn': '999px',
        'badge': '8px',
      },
    },
  },
  plugins: [],
}
