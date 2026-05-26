# Commodity Dashboard — 大宗商品行情与板块强弱动态大屏

Real-time commodity futures dashboard with sector strength heatmap, market leaderboard,
and sector details table. 41 instruments across 5 sectors.

## Architecture

```
commodity-dashboard/
├── config/                  # All configuration — edit these to customise
│   ├── instruments.py       # Instrument & sector definitions
│   └── settings.py          # Server, tqsdk, alert thresholds (env-var overridable)
├── core/                    # Business logic — framework-agnostic
│   ├── data_store.py        # Thread-safe central quote store
│   ├── market_data.py       # Market data providers (tqsdk + demo)
│   └── analytics.py         # Sector scoring, ranking, alert computation
├── server/                  # Web layer
│   └── main.py              # FastAPI app, WebSocket push, static files
├── web/                     # Frontend (served as static files)
│   ├── index.html           # Entry point
│   ├── css/dashboard.css    # All styles
│   └── js/
│       ├── utils.js          # Formatting & color helpers
│       ├── ws-client.js      # WebSocket client (reconnect, dispatch)
│       ├── heatmap.js        # Sector heatmap component
│       ├── leaderboard.js    # ECharts leaderboard component
│       ├── table.js          # Detail table component
│       └── app.js            # Main controller (wires everything)
├── scripts/run.sh           # One-command startup
├── requirements.txt
└── README.md
```

**Data flow:** `tqsdk / DemoProvider → DataStore → Analytics → WebSocket → Browser`

## Quick Start

```bash
# 1. Install & run (demo mode, no credentials needed)
./scripts/run.sh --demo

# 2. Open browser
open http://localhost:8765
```

## Tqsdk Live Mode

```bash
# Set credentials via env vars
export CD_TQ_USERNAME="15583300776"
export CD_TQ_PASSWORD="Unfair4400"
export CD_TQ_CONTRACT_SUFFIX="2609"   # default contract month

./scripts/run.sh --live
```

Or pass credentials in `config/settings.py` directly.

## Configuration

All settings are in `config/settings.py` and can be overridden via environment variables:

| Variable | Default | Description |
|---|---|---|
| `CD_TQ_USERNAME` | — | tqsdk account |
| `CD_TQ_PASSWORD` | — | tqsdk password |
| `CD_TQ_CONTRACT_SUFFIX` | `2609` | Contract month suffix (YYMM) |
| `CD_SERVER_HOST` | `0.0.0.0` | Bind address |
| `CD_SERVER_PORT` | `8765` | Server port |
| `CD_PUSH_INTERVAL` | `0.5` | Data push interval (seconds) |
| `CD_DEMO_MODE` | auto | Force demo mode (`true/false`) |
| `CD_ALERT_CHANGE_THRESHOLD` | `2.5` | Alert: abs(change%) > this |
| `CD_ALERT_AMPLITUDE_THRESHOLD` | `4.0` | Alert: amplitude% > this |

## Adding Instruments

Edit `config/instruments.py` — add a single line to `INSTRUMENTS`:

```python
Instrument(code="fb", exchange="DCE", name="纤维板", sector_id="ferrous"),
```

The new instrument appears automatically in all three panels. No frontend changes needed.

## Adding Sectors

Edit `config/instruments.py` — add to `SECTORS` list and assign instruments to the new `sector_id`.
The frontend will pick up the sector automatically.
