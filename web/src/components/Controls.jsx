import { useState } from 'react';

export default function Controls({ onConnect, autoRefresh, onToggleRefresh }) {
  const [wsUrl, setWsUrl] = useState('ws://localhost:8765/ws');

  return (
    <div className="flex items-center gap-3 px-5 py-1.5 bg-bg2 border-b border-border text-[11px] shrink-0">
      <label className="text-txt2">WS</label>
      <input
        value={wsUrl}
        onChange={e => setWsUrl(e.target.value)}
        className="bg-bg3 text-txt1 border border-border rounded px-2 py-1 text-[11px] font-mono w-[180px] outline-none focus:border-accent"
      />
      <button
        onClick={() => onConnect(wsUrl)}
        className="bg-accent text-white rounded px-3 py-1 text-[11px] font-semibold hover:opacity-85 transition"
      >连接</button>
      <button
        onClick={onToggleRefresh}
        className="bg-bg3 border border-border text-txt1 rounded px-3 py-1 text-[11px] font-semibold hover:opacity-85 transition"
      >自动刷新: {autoRefresh ? '开' : '关'}</button>
      <span className="text-txt3 ml-auto">等待连接...</span>
    </div>
  );
}
