import { useState, useCallback, useRef } from 'react';
import useWebSocket from './hooks/useWebSocket';
import useTheme from './hooks/useTheme';
import Header from './components/Header';
import Controls from './components/Controls';
import StatusBar from './components/StatusBar';
import OIPanel from './components/OIPanel';
import Leaderboard from './components/Leaderboard';
import DetailTable from './components/DetailTable';
import { timeNow } from './utils/format';

export default function App() {
  const { theme, toggle: toggleTheme } = useTheme();
  const { status, snapshot, connect } = useWebSocket();
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const lastUpdateRef = useRef('--');
  const rafRef = useRef(null);

  // Throttle rendering via requestAnimationFrame
  const [displaySnapshot, setDisplaySnapshot] = useState(null);
  const pendingRef = useRef(null);

  if (snapshot && autoRefresh) {
    pendingRef.current = snapshot;
    if (!rafRef.current) {
      rafRef.current = requestAnimationFrame(() => {
        rafRef.current = null;
        lastUpdateRef.current = timeNow();
        setDisplaySnapshot(pendingRef.current);
      });
    }
  }

  const handleConnect = useCallback((url) => connect(url), [connect]);

  const bothCollapsed = leftCollapsed && rightCollapsed;

  return (
    <div className="h-full flex flex-col">
      <Header status={status} lastUpdate={lastUpdateRef.current} theme={theme} onToggleTheme={toggleTheme} />
      <Controls
        onConnect={handleConnect}
        autoRefresh={autoRefresh}
        onToggleRefresh={() => setAutoRefresh(r => !r)}
      />

      <main className="flex-1 flex flex-col p-2.5 gap-2.5 min-h-0">
        <OIPanel instruments={displaySnapshot?.instruments || []} />

        {!bothCollapsed && (
          <div className="flex gap-2.5" style={{ flexBasis: '48%', minHeight: 180 }}>
            {!leftCollapsed && (
              <Leaderboard
                instruments={displaySnapshot?.instruments || []}
                collapsed={false}
                onToggle={() => setLeftCollapsed(true)}
              />
            )}
            {leftCollapsed && !rightCollapsed && (
              <div className="w-[42px] shrink-0 flex flex-col items-center justify-center bg-bg2 border border-border rounded-md cursor-pointer"
                   onClick={() => setLeftCollapsed(false)} title="展开天梯榜">
                <span className="text-txt3 text-[10px]">▶</span>
              </div>
            )}
            {!rightCollapsed && (
              <DetailTable
                instruments={displaySnapshot?.instruments || []}
                collapsed={false}
                onToggle={() => setRightCollapsed(true)}
              />
            )}
            {rightCollapsed && !leftCollapsed && (
              <div className="flex-1 min-w-[42px] flex flex-col items-center justify-center bg-bg2 border border-border rounded-md cursor-pointer flex-shrink-0"
                   style={{ flex: '0 0 42px' }}
                   onClick={() => setRightCollapsed(false)} title="展开纵深数据">
                <span className="text-txt3 text-[10px]">◀</span>
              </div>
            )}
          </div>
        )}

        {bothCollapsed && (
          <div className="flex gap-2.5 shrink-0" style={{ height: 36 }}>
            <div className="w-[42px] bg-bg2 border border-border rounded-md flex items-center justify-center cursor-pointer"
                 onClick={() => setLeftCollapsed(false)} title="展开天梯榜">
              <span className="text-txt3 text-[10px]">▶</span>
            </div>
            <div className="flex-1 min-w-[42px] bg-bg2 border border-border rounded-md flex items-center justify-center cursor-pointer"
                 style={{ maxWidth: 42 }}
                 onClick={() => setRightCollapsed(false)} title="展开纵深数据">
              <span className="text-txt3 text-[10px]">◀</span>
            </div>
          </div>
        )}
      </main>

      <StatusBar
        periodLabel="15分钟"
        timestamp={displaySnapshot?.timestamp}
        instrumentCount={displaySnapshot?.instruments?.length || 0}
      />
    </div>
  );
}
