# Findings

## 项目架构

- **前端**: React 18 + Vite 6 + Tailwind CSS 3, `web/src/`
- **后端**: Python FastAPI + WebSocket, `server/`, `core/`, `config/`
- **数据源**: tqsdk (实盘) 或 DemoProvider (演示)

## 关键发现

### 1. 合约配置 (`config/instruments.py`)
- 当前 26 个活跃品种 + 10 个被注释 (共 36 个)
- 纯 Python 代码配置，无 JSON/YAML 用户配置文件
- 注释掉的品种: sm, sf, fg, sa, ta, ma, rm, sr, cf, oi
- DemoProvider 的 `base_prices` 需同步更新

### 2. 柱子大小 (`OICard.jsx`)
- Price bars 容器: `h-[28px]`, bar `max-w-[10px]`
- OI bars 容器: `h-[22px]`, bar `max-w-[8px]`
- 统一方案: 都改为 28px 容器, 10px max-w

### 3. Kline 数据 (`core/market_data.py`)
- `OI_NUM_BARS = 7` — 仅保留 7 根 bar
- MACD 计算需要至少 35+ 根 bar (EMA26 + signal9)
- 需要扩展为 60 根 bar，前 7 根用于柱状图展示，全部 60 根用于 MACD

### 4. 信号因子现状
- OICard.jsx 底部有预留的 signal tag 区域（目前为空）
- `hasAlert` 仅基于价格涨跌幅+振幅阈值（非技术指标）
- 项目中不存在任何 MACD、RSI、EMA 等技术指标计算
- 需从零实现 MACD + 背离检测

### 5. 数据流
```
market_data.py → data_store.py → analytics.py → server/main.py (WS push) → useWebSocket.js → App.jsx → OIPanel → OICard
```
- analytics.py 的 `compute()` 函数构建 `InstrumentRow`，通过 `to_dict()` 序列化
- 新增 signals 需要在 `InstrumentRow.to_dict()` 中添加字段
