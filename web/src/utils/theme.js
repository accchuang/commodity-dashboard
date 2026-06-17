/**
 * theme.js — Central color configuration (pixel B&W).
 *
 * **After changing colors here:**
 * 1. Restart Vite dev server or rebuild — ``tailwind.config.js`` imports this file.
 * 2. Sync the matching ``:root { }`` CSS variables in ``index.css``
 *    if you changed up / down / accent / gold / warn.
 *
 * Tailwind classes (``bg-accent``, ``text-up``, etc.) update automatically.
 */

// ── Core palette (dark default) ──────────────────────────────────────────
export const PALETTE = {
  primary:   '#FFFFFF',
  success:   '#FFFFFF',
  light:     '#CCCCCC',
  text:      '#FFFFFF',
  highlight: '#FFFFFF',
};

// ── Background hierarchy ─────────────────────────────────────────────────
export const BG = {
  bg1: '#000000',    // page background
  bg2: '#000000',    // panel background
  bg3: '#1A1A1A',    // card / elevated surface
};

// ── Text on dark bg ──────────────────────────────────────────────────────
export const TEXT = {
  primary:   PALETTE.text,
  secondary: 'rgba(255, 255, 255, 0.55)',
  muted:     'rgba(255, 255, 255, 0.38)',
};

// ── Functional ───────────────────────────────────────────────────────────
export const FUNC = {
  accent:    '#FFFFFF',
  up:        '#FFFFFF',
  down:      '#888888',
  warn:      '#FFFFFF',
  gold:      '#FFFFFF',
  border:    'rgba(255, 255, 255, 0.20)',
  sectorAvg: 'rgba(255, 255, 255, 0.40)',
};

// ── Sector colors (grayscale gradient for differentiation) ───────────────
export const SECTOR = {
  ferrous:    '#FFFFFF',
  energy:     'rgba(255, 255, 255, 0.70)',
  nonferrous: 'rgba(255, 255, 255, 0.55)',
  agri:       'rgba(255, 255, 255, 0.38)',
  newenergy:  'rgba(255, 255, 255, 0.25)',
  financial:  'rgba(255, 255, 255, 0.45)',
};

// ── Mini bar colors ──────────────────────────────────────────────────────
export const BAR = {
  up:    FUNC.up,
  down:  FUNC.down,
  zero:  'rgba(255, 255, 255, 0.08)',
};

// ── Connection dot ───────────────────────────────────────────────────────
export const DOT = {
  live:        '#FFFFFF',
  connecting:  '#CCCCCC',
  off:         '#888888',
};

// ── Light theme palette ──────────────────────────────────────────────────
export const LIGHT = {
  BG: {
    bg1: '#FFFFFF',
    bg2: '#FFFFFF',
    bg3: '#F0F0F0',
  },
  TEXT: {
    primary:   '#000000',
    secondary: 'rgba(0, 0, 0, 0.55)',
    muted:     'rgba(0, 0, 0, 0.38)',
  },
  FUNC: {
    accent:    '#000000',
    up:        '#000000',
    down:      '#888888',
    warn:      '#000000',
    gold:      '#000000',
    border:    'rgba(0, 0, 0, 0.20)',
    sectorAvg: 'rgba(0, 0, 0, 0.40)',
  },
  SECTOR: {
    ferrous:    '#000000',
    energy:     'rgba(0, 0, 0, 0.70)',
    nonferrous: 'rgba(0, 0, 0, 0.55)',
    agri:       'rgba(0, 0, 0, 0.38)',
    newenergy:  'rgba(0, 0, 0, 0.25)',
    financial:  'rgba(0, 0, 0, 0.45)',
  },
  BAR: {
    up:    '#000000',
    down:  '#888888',
    zero:  'rgba(0, 0, 0, 0.08)',
  },
  DOT: {
    live:        '#000000',
    connecting:  '#666666',
    off:         '#888888',
  },
  HOVER: 'rgba(0, 0, 0, 0.04)',
};
