import { useState, useMemo } from 'react';
import OICard from './OICard';
import { SECTOR_ORDER, SECTOR_META } from '../../utils/format';

const PERIODS = [
  { label: '15分钟', key: '15m' },
  { label: '30分钟', key: '30m' },
  { label: '1小时',  key: '1h'  },
  { label: '7小时',  key: '7h'  },
  { label: '18小时', key: '18h' },
];

export default function OIPanel({ instruments }) {
  const [periodIdx, setPeriodIdx] = useState(0);
  const [filterEnabled, setFilterEnabled] = useState(true);

  const period = PERIODS[periodIdx];

  // Build row data from instruments
  const rows = useMemo(() => {
    const key = period.key;
    const result = [];

    for (const d of instruments) {
      const oiBars = d.oiBars;
      if (!oiBars) continue;
      const bars = oiBars[key];
      if (!bars || !Array.isArray(bars) || bars.length === 0) continue;

      const todayDelta = d.todayOiDelta || 0;
      if (filterEnabled && todayDelta <= 0) continue;

      // Use last 7 bars for display (backend may send more for MACD)
      const displayBars = bars.slice(-7);
      const netDelta = displayBars.reduce((a, b) => a + b, 0);
      const pastOi = d.openInterest - netDelta;
      const netDeltaPct = pastOi > 0 ? (netDelta / pastOi) * 100 : 0;

      const priceBarsAll = d.priceBars?.[key] || [];
      const priceBarsArr = priceBarsAll.slice(-7);

      const signal = d.signals?.[key] || null;

      result.push({
        insId: d.insId, name: d.name, code: d.code,
        exchange: d.exchange, sectorId: d.sectorId,
        lastPrice: d.lastPrice, changePct: d.changePct,
        netDelta, netDeltaPct,
        signal,
        bars: displayBars.map(v => ({
          delta: v,
          dir: v > 0.5 ? 1 : v < -0.5 ? -1 : 0,
        })),
        priceBars: priceBarsArr.map(v => ({
          delta: v,
          dir: v > 0 ? 1 : v < 0 ? -1 : 0,
        })),
      });
    }
    return result;
  }, [instruments, period, filterEnabled]);

  // Group by sector
  const groups = useMemo(() => {
    const g = {};
    for (const r of rows) {
      if (!g[r.sectorId]) g[r.sectorId] = [];
      g[r.sectorId].push(r);
    }
    for (const arr of Object.values(g)) arr.sort((a, b) => b.netDelta - a.netDelta);
    return g;
  }, [rows]);

  const globalMaxBar = useMemo(
    () => Math.max(1, ...rows.flatMap(r => r.bars.map(b => Math.abs(b.delta)))),
    [rows],
  );

  const globalMaxPriceBar = useMemo(
    () => Math.max(0.01, ...rows.flatMap(r => r.priceBars.map(b => Math.abs(b.delta)))),
    [rows],
  );

  return (
    <section className="flex flex-col bg-bg2 border border-border rounded-md overflow-hidden" style={{ flex: '1 1 auto', minHeight: 220 }}>
      {/* Header */}
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border text-[11px] uppercase tracking-wider text-txt2 font-semibold shrink-0">
        <span>增仓排名 Open Interest Change</span>
        <span className="flex items-center gap-2">
          {/* Period buttons */}
          <span className="flex gap-1">
            {PERIODS.map((p, i) => (
              <button
                key={p.key}
                className={`period-btn${i === periodIdx ? ' active' : ''}`}
                onClick={() => setPeriodIdx(i)}
              >{p.label}</button>
            ))}
          </span>
          {/* Filter toggle */}
          <button
            className={`period-btn${filterEnabled ? ' active' : ''}`}
            style={!filterEnabled ? { background: 'var(--clr-btn-disabled-bg)', color: 'var(--clr-btn-disabled-text)' } : {}}
            onClick={() => setFilterEnabled(f => !f)}
          >{filterEnabled ? '仅增仓' : '全部'}</button>
        </span>
      </div>

      {/* Card grid */}
      <div className="flex-1 overflow-auto">
        {rows.length === 0 ? (
          <div className="flex items-center justify-center h-full text-txt3 text-[13px]">
            {filterEnabled ? `暂无增仓合约 (${period.label}内)` : '暂无数据'}
          </div>
        ) : (
          <div className="flex flex-col gap-0.5 p-1.5">
            {SECTOR_ORDER.map(sid => {
              const items = groups[sid];
              if (!items?.length) return null;
              const meta = SECTOR_META[sid] || { name: sid, color: '#888' };
              const localMax = Math.max(1, ...items.flatMap(r => r.bars.map(b => Math.abs(b.delta))));
              const localMaxPrice = Math.max(0.01, ...items.flatMap(r => r.priceBars.map(b => Math.abs(b.delta))));

              return (
                <div key={sid}>
                  <div className="text-[11px] font-bold tracking-wide py-0.5 pl-1 border-b border-[var(--clr-border-faint)]" style={{ color: `var(--clr-sector-${sid})` }}>
                    {meta.name} ({items.length})
                  </div>
                  <div className="flex flex-wrap gap-1.5 py-1 pl-1">
                    {items.map(r => (
                      <OICard key={r.insId} data={r} maxAbsBar={localMax} maxAbsPriceBar={localMaxPrice} sectorColor={`var(--clr-sector-${sid})`} />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
