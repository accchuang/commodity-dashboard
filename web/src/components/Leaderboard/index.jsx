import { useMemo } from 'react';
import { formatPct, changeClass } from '../../utils/format';

export default function Leaderboard({ instruments, collapsed, onToggle }) {
  const maxAbs = useMemo(
    () => Math.max(0.01, ...instruments.map(d => Math.abs(d.changePct))),
    [instruments],
  );

  const sorted = useMemo(
    () => [...instruments].sort((a, b) => b.changePct - a.changePct),
    [instruments],
  );

  return (
    <section className={`shrink-0 flex flex-col bg-bg2 border border-border rounded-md overflow-hidden transition-all duration-300 ${
      collapsed ? 'panel-collapsed-l' : 'w-[358px]'
    }`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border text-[11px] uppercase tracking-wider text-txt2 font-semibold shrink-0">
        <span>涨跌幅天梯榜</span>
        <span className="flex items-center gap-2">
          <span className="text-[10px] normal-case tracking-normal font-normal">%</span>
          <button onClick={onToggle} className="text-txt3 hover:text-txt1 text-[10px] border border-border rounded px-1.5 py-0.5 transition">
            {collapsed ? '▶' : '◀'}
          </button>
        </span>
      </div>
      {!collapsed && (
        <div className="flex-1 overflow-auto">
          {sorted.map((d, i) => {
            const barPct = (Math.abs(d.changePct) / maxAbs) * 100;
            const cls = changeClass(d.changePct);
            return (
              <div key={d.insId} className="rank-row" title={`${d.name} (${d.exchange}.${d.code})\n最新价: ${d.lastPrice}\n振幅: ${d.amplitude?.toFixed(2)}%`}>
                <span className="rank-num font-mono">{i + 1}</span>
                <span className="rank-name">{d.name}</span>
                <span className="rank-code font-mono">{d.exchange}.{d.code}</span>
                <span className={`rank-change font-mono ${cls}`}>{formatPct(d.changePct)}</span>
                <span className="rank-bar-wrap">
                  <span className={`rank-bar-fill ${d.changePct >= 0 ? 'bg-up' : 'bg-down'}`} style={{ width: `${barPct}%` }} />
                </span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
