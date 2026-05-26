import { useState, useEffect } from 'react';
import { timeNow } from '../utils/format';

export default function Header({ status, lastUpdate, theme, onToggleTheme }) {
  const [clock, setClock] = useState(timeNow());

  useEffect(() => {
    const t = setInterval(() => setClock(timeNow()), 1000);
    return () => clearInterval(t);
  }, []);

  const dotClass = {
    live: 'dot-live', connecting: 'dot-connecting', off: 'dot-off',
  }[status] || 'dot-off';

  const label = { live: '实时连接', connecting: '连接中...', off: '未连接' }[status] || '未连接';

  return (
    <header className="flex items-center justify-between px-5 py-2.5 bg-bg2 border-b border-border shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-[16px] font-bold tracking-wide">
          COMMODITY <span className="text-accent">DASHBOARD</span>
        </h1>
        <span className={`w-2 h-2 rounded-full inline-block ${dotClass}`} />
        <span className="text-[11px] text-txt3">{label}</span>
        <button
          onClick={onToggleTheme}
          className="text-[11px] text-txt3 hover:text-txt1 border border-border rounded px-2 py-0.5 transition"
          title={theme === 'dark' ? '切换到浅色' : '切换到深色'}
        >{theme === 'dark' ? '☀' : '☾'}</button>
      </div>
      <div className="flex items-center gap-3 text-[12px]">
        <span className="font-mono">{clock}</span>
        <span className="text-txt3 opacity-30">|</span>
        <span className="text-txt3">{lastUpdate || '--'}</span>
      </div>
    </header>
  );
}
