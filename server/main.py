"""
FastAPI application — WebSocket data push + static file serving.

Start with:  python server/main.py           (auto-detects demo/tqsdk)
             python server/main.py --demo    (force demo mode)
             python server/main.py --live    (force tqsdk mode)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response

# Project root (commodity-dashboard/)
ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
sys.path.insert(0, str(ROOT))

from config.instruments import INSTRUMENTS, build_tqsdk_id
from config.settings import AppSettings, settings as default_settings
from core.data_store import DataStore
from core.market_data import create_provider
from core.analytics import compute

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("server")

# ── App ─────────────────────────────────────────────────────────────

app = FastAPI(title="Commodity Dashboard", version="1.0.0")


# Disable caching for development — browsers will always fetch fresh assets
@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    path = request.url.path
    if path.endswith((".css", ".js", ".html")) or path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Global state (initialised at startup)
store = DataStore()
settings: AppSettings = default_settings
connected_clients: set[WebSocket] = set()


# ── WebSocket endpoint ──────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    logger.info("Client connected (%d total)", len(connected_clients))
    try:
        while True:
            # Keep connection alive; client may send pings
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.debug("WS recv error: %s", exc)
    finally:
        connected_clients.discard(ws)
        logger.info("Client disconnected (%d remaining)", len(connected_clients))


# ── Push loop ───────────────────────────────────────────────────────

async def push_loop() -> None:
    """Continuously compute analytics from the store and push to all WS clients."""
    logger.info("Push loop started (interval=%.2fs)", settings.server.push_interval)
    while True:
        await asyncio.sleep(settings.server.push_interval)
        if not connected_clients:
            continue
        try:
            quotes = await store.snapshot_quotes()
            snapshot = compute(quotes, settings)
            payload = snapshot.to_dict()
            # Broadcast — disconnected clients raise; discard them
            dead: set[WebSocket] = set()
            for ws in connected_clients:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead.add(ws)
            connected_clients.difference_update(dead)
        except Exception as exc:
            logger.error("Push error: %s", exc, exc_info=True)


# ── REST: current snapshot (for initial page load) ──────────────────

@app.get("/api/snapshot")
async def get_snapshot():
    quotes = await store.snapshot_quotes()
    snapshot = compute(quotes, settings)
    return snapshot.to_dict()


@app.get("/api/instruments")
async def get_instruments():
    return [
        {
            "code": i.code,
            "exchange": i.exchange,
            "insId": build_tqsdk_id(i),
            "name": i.name,
            "sectorId": i.sector_id,
        }
        for i in INSTRUMENTS
    ]


# ── Static files ────────────────────────────────────────────────────

# Serve React production build if available, otherwise dev static files
DIST_DIR = WEB_DIR / "dist"
if DIST_DIR.is_dir():
    STATIC_DIR = DIST_DIR
    logger.info("Serving React production build from %s", STATIC_DIR)
else:
    STATIC_DIR = WEB_DIR
    logger.info("Serving static files from %s (dev mode — use Vite dev server)", STATIC_DIR)


@app.get("/")
async def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>No index.html found</h1>", status_code=500)


# Mount after explicit routes so "/" takes priority
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


# ── Startup / Shutdown ──────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    provider = create_provider(settings)
    asyncio.create_task(provider.run(store, INSTRUMENTS, settings))
    asyncio.create_task(push_loop())
    logger.info("Server ready — %s | ws://%s:%d/ws",
                "DEMO" if settings.demo_mode else "TQSDK",
                settings.server.host, settings.server.port)


# ── CLI entry ───────────────────────────────────────────────────────

def main():
    global settings

    parser = argparse.ArgumentParser(description="Commodity Dashboard Server")
    parser.add_argument("--demo", action="store_true", help="Force demo mode")
    parser.add_argument("--live", action="store_true", help="Force tqsdk live mode")
    parser.add_argument("--host", default=None, help="Bind host")
    parser.add_argument("--port", type=int, default=None, help="Bind port")
    parser.add_argument("--suffix", default=None, help="Contract suffix (e.g. 2609)")
    args = parser.parse_args()

    if args.demo:
        settings.demo_mode = True
    elif args.live:
        settings.demo_mode = False

    if args.host:
        settings.server.host = args.host
    if args.port:
        settings.server.port = args.port
    if args.suffix:
        settings.tqsdk.contract_suffix = args.suffix

    import uvicorn
    uvicorn.run(
        "server.main:app",
        host=settings.server.host,
        port=settings.server.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
