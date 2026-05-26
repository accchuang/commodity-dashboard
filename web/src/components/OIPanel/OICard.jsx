import { formatPct, formatPrice, changeClass } from '../../utils/format';

export default function OICard({ data, maxAbsBar, maxAbsPriceBar, sectorColor }) {
  const {
    name, exchange, code, lastPrice, changePct,
    netDelta, netDeltaPct, bars, priceBars, signal,
  } = data;

  const priceCls = changeClass(changePct);
  const netSign = '+';

  return (
    <div
      className="relative flex flex-col items-center bg-bg3 rounded-md pt-1.5 pb-1 px-2 gap-0 cursor-default transition-colors hover:bg-[var(--clr-card-hover)]"
      style={{ width: 148, borderLeft: `3px solid ${sectorColor}` }}
      title={[
        `${name} (${exchange}.${code})`,
        `最新价: ${formatPrice(lastPrice)}  涨跌: ${formatPct(changePct)}`,
        `增仓: ${netSign}${netDelta.toLocaleString()} 手 (${netSign}${netDeltaPct.toFixed(2)}%)`,
      ].join('\n')}
    >
      {/* Name + Code */}
      <span className="text-[12px] font-bold text-txt1 leading-tight">{name}</span>
      <span className="text-[10px] text-txt3 font-mono leading-tight">{exchange}.{code}</span>

      {/* Price + Change% */}
      <span className="text-[13px] font-bold font-mono leading-tight mt-0.5">{formatPrice(lastPrice)}</span>
      <span className={`text-[11px] font-semibold font-mono leading-tight ${priceCls}`}>{formatPct(changePct)}</span>

      {/* Price change bars — 7 tick price deltas */}
      <div className="flex items-end justify-center gap-[2px] w-full h-[28px] px-1.5">
        {(priceBars || []).map((b, j) => {
          const h = maxAbsPriceBar > 0 ? Math.max(4, (Math.abs(b.delta) / maxAbsPriceBar) * 100) : 4;
          const cls = b.dir > 0 ? 'bg-up' : b.dir < 0 ? 'bg-down' : 'bg-[var(--clr-bar-zero)]';
          return (
            <span
              key={j}
              className={`flex-1 min-w-[5px] max-w-[10px] rounded-t-sm transition-all duration-500 ${cls}`}
              style={{ height: `${h}%`, minHeight: 2 }}
            />
          );
        })}
      </div>

      {/* Mini bars — 7 sub-period OI deltas */}
      <div className="flex items-end justify-center gap-[2px] w-full h-[28px] my-1 px-1.5">
        {bars.map((b, j) => {
          const h = maxAbsBar > 0 ? Math.max(4, (Math.abs(b.delta) / maxAbsBar) * 100) : 4;
          const cls = b.dir > 0 ? 'bg-up' : b.dir < 0 ? 'bg-down' : 'bg-[var(--clr-bar-zero)]';
          return (
            <span
              key={j}
              className={`flex-1 min-w-[5px] max-w-[10px] rounded-t-sm transition-all duration-500 ${cls}`}
              style={{ height: `${h}%`, minHeight: 2 }}
            />
          );
        })}
      </div>

      {/* Net OI delta */}
      <span className="text-[10px] font-bold font-mono text-up leading-tight">
        {netSign}{netDelta.toLocaleString()}
      </span>
      <span className="text-[9px] font-mono text-up leading-tight">
        {netSign}{netDeltaPct.toFixed(1)}%
      </span>

      {/* Signal factor tags */}
      <div className="w-full mt-0.5 pt-0.5 border-t border-[var(--clr-border-faint)] min-h-[14px] flex items-center justify-center flex-wrap gap-x-1 gap-y-0.5">
        {signal === 'bullish' && (
          <span className="text-[9px] px-1 rounded-sm bg-[rgba(88,166,255,0.15)] text-accent">MACD底背离</span>
        )}
        {signal === 'bearish' && (
          <span className="text-[9px] px-1 rounded-sm bg-[rgba(235,157,255,0.18)] text-warn">MACD顶背离</span>
        )}
      </div>
    </div>
  );
}
