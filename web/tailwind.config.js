/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg1: 'var(--clr-bg1)',
        bg2: 'var(--clr-bg2)',
        bg3: 'var(--clr-bg3)',
        txt1: 'var(--clr-txt1)',
        txt2: 'var(--clr-txt2)',
        txt3: 'var(--clr-txt3)',
        accent: 'var(--clr-accent)',
        up: 'var(--clr-up)',
        down: 'var(--clr-down)',
        warn: 'var(--clr-warn)',
        gold: 'var(--clr-gold)',
        border: 'var(--clr-border)',
        'sector-avg': 'var(--clr-sector-avg)',
        sector: {
          ferrous: 'var(--clr-sector-ferrous)',
          energy: 'var(--clr-sector-energy)',
          nonferrous: 'var(--clr-sector-nonferrous)',
          agri: 'var(--clr-sector-agri)',
          newenergy: 'var(--clr-sector-newenergy)',
        },
      },
      fontFamily: { mono: ['Courier New', 'Courier', 'monospace'] },
    },
  },
  plugins: [],
};
