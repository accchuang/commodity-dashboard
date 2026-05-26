/**
 * theme.js — Central color configuration.
 *
 * **After changing colors here:**
 * 1. Restart Vite dev server or rebuild — ``tailwind.config.js`` imports this file.
 * 2. Sync the matching ``:root { }`` CSS variables in ``index.css`` (lines 8-17)
 *    if you changed up / down / accent / gold / warn.
 *
 * Tailwind classes (``bg-accent``, ``text-up``, etc.) update automatically.
 */

// ── Core palette ────────────────────────────────────────────────────
export const PALETTE = {
  primary:   '#4757E8',   // (71, 87, 232)   — buttons, accent, active
  success:   '#F1C40F',   // (16, 195, 120)  — up / positive / 增仓
  light:     '#ADE699',   // (173, 230, 153) — light positive, hover
  text:      '#F4F0F1',   // (244, 240, 241) — primary text
  highlight: '#EB9DFF',   // (235, 157, 255) — alerts, special markers
};

// ── Background hierarchy (dark navy derived from primary) ───────────
// Mix primary with black at different ratios
export const BG = {
  bg1: '#0a0d24',    // page background  (darkest)
  bg2: '#0f1233',    // panel background
  bg3: '#151844',    // card / hover background
};

// ── Text on dark bg ─────────────────────────────────────────────────
export const TEXT = {
  primary:   PALETTE.text,                        // #F4F0F1
  secondary: 'rgba(244, 240, 241, 0.52)',
  muted:     'rgba(244, 240, 241, 0.32)',
};

// ── Functional ──────────────────────────────────────────────────────
export const FUNC = {
  accent:    PALETTE.primary,    // buttons, active states, links
  up:        PALETTE.success,    // positive price / OI changes
  down:      '#83C5BE',          // negative (warm red — complementary)
  warn:      PALETTE.highlight,  // alert signals
  gold:      '#f5c542',          // rankings top-3
  border:    'rgba(71, 87, 232, 0.18)',
  sectorAvg: 'rgba(71, 87, 232, 0.45)',
};

// ── Sector colors (mapped from palette) ─────────────────────────────
export const SECTOR = {
  ferrous:    '#5b6aee',   // blue-purple variant  (steel)
  energy:     '#f0a050',   // warm amber           (oil/energy)
  nonferrous: PALETTE.success,     // #10C378     (metals)
  agri:       PALETTE.light,       // #ADE699     (crops)
  newenergy:  PALETTE.highlight,   // #EB9DFF     (new tech)
};

// ── Mini bar colors ─────────────────────────────────────────────────
export const BAR = {
  up:    PALETTE.success,
  down:  FUNC.down,
  zero:  'rgba(244, 240, 241, 0.08)',
};

// ── Connection dot ──────────────────────────────────────────────────
export const DOT = {
  live:        PALETTE.success,
  connecting:  '#f5c542',
  off:         FUNC.down,
};

// ── Light theme palette ─────────────────────────────────────────────
export const LIGHT = {
  BG: {
    bg1: '#f0f2f5',
    bg2: '#ffffff',
    bg3: '#e8eaf0',
  },
  TEXT: {
    primary:   '#1a1d33',
    secondary: 'rgba(26, 29, 51, 0.55)',
    muted:     'rgba(26, 29, 51, 0.38)',
  },
  FUNC: {
    accent:    '#4757E8',
    up:        '#b8960a',
    down:      '#cf4520',
    warn:      '#9b30d4',
    gold:      '#b8960a',
    border:    'rgba(71, 87, 232, 0.22)',
    sectorAvg: 'rgba(71, 87, 232, 0.55)',
  },
  SECTOR: {
    ferrous:    '#4a56d4',
    energy:     '#d48835',
    nonferrous: '#b8960a',
    agri:       '#5c9e4a',
    newenergy:  '#9b30d4',
  },
  BAR: {
    up:    '#b8960a',
    down:  '#cf4520',
    zero:  'rgba(26, 29, 51, 0.08)',
  },
  DOT: {
    live:        '#b8960a',
    connecting:  '#b8960a',
    off:         '#cf4520',
  },
  HOVER:   'rgba(71, 87, 232, 0.08)',
};
