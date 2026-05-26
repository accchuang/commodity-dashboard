# Task Plan: 新增 7小时/18小时 周期 ✅

- [x] `core/market_data.py` — OI_KLINE_PERIODS 新增 "7h": 25200, "18h": 64800
- [x] `core/market_data.py` — DemoProvider 硬编码周期列表改为引用 OI_KLINE_PERIODS
- [x] `web/src/components/OIPanel/index.jsx` — PERIODS 新增 7小时/18小时
- [x] 验证: 5 个周期全部生成 60 根 bar, 前端构建通过
