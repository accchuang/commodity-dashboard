export function formatPct(value) {
  const prefix = value > 0.005 ? '+' : '';
  return `${prefix}${value.toFixed(2)}%`;
}

export function formatPrice(value, decimals = 1) {
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function changeClass(pct) {
  if (pct > 0.005) return 'text-up';
  if (pct < -0.005) return 'text-down';
  return '';
}

export function timeNow() {
  return new Date().toLocaleTimeString('zh-CN', { hour12: false });
}

import { SECTOR } from './theme';

export const SECTOR_META = {
  ferrous:    { name: '黑色建材',     color: SECTOR.ferrous },
  energy:     { name: '能源化工',     color: SECTOR.energy },
  nonferrous: { name: '有色金属',     color: SECTOR.nonferrous },
  agri:       { name: '农产品/油脂', color: SECTOR.agri },
  newenergy:  { name: '新能源/其他', color: SECTOR.newenergy },
  financial:  { name: '金融期货',     color: SECTOR.financial },
};

export const SECTOR_ORDER = ['ferrous', 'energy', 'nonferrous', 'agri', 'newenergy', 'financial'];
