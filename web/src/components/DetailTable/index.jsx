import { useMemo } from 'react';
import { formatPct, formatPrice, changeClass, SECTOR_ORDER, SECTOR_META } from '../../utils/format';

export default function DetailTable({ instruments, collapsed, onToggle }) {
  const { alertCount, rows } = useMemo(() => {
    const groups = {};
    for (const d of instruments) {
      const sid = d.sectorId;
      if (!groups[sid]) groups[sid] = [];
      groups[sid].push(d);
    }
    // Stable sort by code within each sector
    for (const items of Object.values(groups)) {
      items.sort((a, b) => a.code.localeCompare(b.code));
    }

    const ordered = [...new Set([...SECTOR_ORDER.filter(s => groups[s]), ...Object.keys(groups)])];
    let alerts = 0;
    const html = [];

    for (const sid of ordered) {
      const items = groups[sid];
      if (!items?.length) continue;
      const meta = SECTOR_META[sid] || { name: sid, color: '#888' };
      const avg = items.reduce((a, b) => a + b.changePct, 0) / items.length;

      html.push({ type: 'sector', sid, meta, avg, count: items.length });
      for (const d of items) {
        if (d.hasAlert) alerts++;
        html.push({ type: 'row', ...d });
      }
    }
    return { alertCount: alerts, rows: html };
  }, [instruments]);

  return (
    <section className={`flex-1 flex flex-col bg-bg2 border border-border rounded-md overflow-hidden transition-all duration-300 min-w-0 ${
      collapsed ? 'panel-collapsed-r' : ''
    }`}>
      <div className="flex items-center justify-between px-3.5 py-2 border-b border-border text-[11px] uppercase tracking-wider text-txt2 font-semibold shrink-0">
        <span>板块纵深数据</span>
        <span className="flex items-center gap-2">
          <span className="text-[10px] normal-case tracking-normal font-normal">
            {alertCount > 0 ? `${alertCount} 个极端信号` : ''}
          </span>
          <button onClick={onToggle} className="text-txt3 hover:text-txt1 text-[10px] border border-border rounded px-1.5 py-0.5 transition">
            {collapsed ? '◀' : '▶'}
          </button>
        </span>
      </div>
      {!collapsed && (
        <div className="flex-1 overflow-auto">
          <table className="detail-table w-full border-collapse text-[12px]">
            <thead className="sticky top-0 z-10">
              <tr>
                <th className="bg-bg3 text-txt2 py-1.5 px-2.5 text-left text-[10px] uppercase tracking-wider font-medium border-b-2 border-border">品种</th>
                <th className="bg-bg3 text-txt2 py-1.5 px-2.5 text-right text-[10px] uppercase tracking-wider font-medium border-b-2 border-border">最新价</th>
                <th className="bg-bg3 text-txt2 py-1.5 px-2.5 text-right text-[10px] uppercase tracking-wider font-medium border-b-2 border-border">涨跌幅</th>
                <th className="bg-bg3 text-txt2 py-1.5 px-2.5 text-right text-[10px] uppercase tracking-wider font-medium border-b-2 border-border">振幅</th>
                <th className="bg-bg3 text-txt2 py-1.5 px-2.5 text-center text-[10px] uppercase tracking-wider font-medium border-b-2 border-border w-[50px]">警报</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) =>
                r.type === 'sector' ? (
                  <tr key={`s-${r.sid}`} className="sector-divider">
                    <td colSpan={5}>
                      {r.meta.icon} {r.meta.name}
                      <span className={`text-[10px] ml-2 ${r.avg >= 0 ? 'text-up' : 'text-down'}`}>
                        均幅 {formatPct(r.avg)} · {r.count} 品种
                      </span>
                    </td>
                  </tr>
                ) : (
                  <tr key={r.insId} className="data-row">
                    <td className="text-left">
                      <span className="font-semibold">{r.name}</span>
                      <span className="text-txt3 text-[10px] ml-1">{r.code.toUpperCase()}</span>
                    </td>
                    <td className="text-right font-mono">{formatPrice(r.lastPrice)}</td>
                    <td className={`text-right font-mono ${changeClass(r.changePct)}`}>{formatPct(r.changePct)}</td>
                    <td className="text-right font-mono">{r.amplitude?.toFixed(2)}%</td>
                    <td className={`text-center text-[14px] ${r.hasAlert ? 'alert-active' : ''}`}>
                      {r.hasAlert ? '⚠️' : <span className="opacity-[0.12]">-</span>}
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
