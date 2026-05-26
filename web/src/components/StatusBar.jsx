export default function StatusBar({ text, instrumentCount, periodLabel, timestamp }) {
  return (
    <footer className="flex justify-between px-5 py-1.5 bg-bg2 border-t border-border text-[10px] text-txt3 shrink-0">
      <span>{text || `增仓周期: ${periodLabel} · ${timestamp}`}</span>
      <span className="font-mono">品种: {instrumentCount}</span>
    </footer>
  );
}
