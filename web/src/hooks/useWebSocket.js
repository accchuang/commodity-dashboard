import { useState, useEffect, useRef, useCallback } from 'react';

export default function useWebSocket(url = 'ws://localhost:8765/ws') {
  const [status, setStatus] = useState('off'); // 'off' | 'connecting' | 'live'
  const [snapshot, setSnapshot] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectDelay = useRef(2000);

  const connect = useCallback((wsUrl) => {
    const target = wsUrl || url;
    if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    if (reconnectTimer.current) { clearTimeout(reconnectTimer.current); reconnectTimer.current = null; }

    setStatus('connecting');
    try {
      const ws = new WebSocket(target);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectDelay.current = 2000;
        setStatus('live');
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'market_snapshot') setSnapshot(msg);
        } catch (_) { /* ignore */ }
      };

      ws.onclose = () => {
        setStatus('off');
        reconnectTimer.current = setTimeout(() => {
          reconnectDelay.current = Math.min(reconnectDelay.current * 1.5, 30000);
          connect(target);
        }, reconnectDelay.current);
      };

      ws.onerror = () => {};
    } catch (_) {
      setStatus('off');
    }
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  return { status, snapshot, connect };
}
