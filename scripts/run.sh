#!/usr/bin/env bash
# ── Commodity Dashboard — Startup Script ─────────────────────────────
# Usage:
#   ./scripts/run.sh                     # prod mode (Python only)
#   ./scripts/run.sh --dev               # dev mode (Python + Vite HMR)
#   ./scripts/run.sh --build             # build React, then start Python
#   ./scripts/run.sh --demo / --live     # as before
#
# Environment variables (all prefixed with CD_):
#   CD_TQ_USERNAME, CD_TQ_PASSWORD   tqsdk account
#   CD_SERVER_HOST, CD_SERVER_PORT   bind address (default :8765)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="prod"
BUILD_FIRST=false
PY_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --dev)   MODE="dev" ;;
    --build) BUILD_FIRST=true ;;
    *)       PY_ARGS+=("$arg") ;;
  esac
done

# ── Python venv ──────────────────────────────────────────────────────

if [ ! -d "venv" ]; then
  echo "==> Creating Python virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# ── Node deps (install if needed) ────────────────────────────────────

if [ ! -d "web/node_modules" ]; then
  echo "==> Installing frontend dependencies..."
  cd web && npm install --silent && cd ..
fi

# ── Build (--build flag) ─────────────────────────────────────────────

if $BUILD_FIRST || { [ "$MODE" = "prod" ] && [ ! -d "web/dist" ]; }; then
  echo "==> Building React frontend..."
  cd web && npm run build --silent && cd ..
  echo "==> Build complete → web/dist/"
fi

# ── Start ────────────────────────────────────────────────────────────

if [ "$MODE" = "dev" ]; then
  echo "==> Starting dev servers..."

  cleanup() {
    echo ""
    echo "==> Shutting down..."
    kill $PY_PID 2>/dev/null || true
    kill $VITE_PID 2>/dev/null || true
    wait $PY_PID 2>/dev/null || true
    wait $VITE_PID 2>/dev/null || true
    echo "==> Done."
  }
  trap cleanup EXIT INT TERM

  # Start Python backend in background
  python server/main.py "${PY_ARGS[@]}" &
  PY_PID=$!
  echo "   Python backend → http://localhost:8765  (pid $PY_PID)"

  # Start Vite dev server in foreground
  cd web
  echo "   Vite dev server → http://localhost:5173"
  npx vite --host &
  VITE_PID=$!
  cd ..

  echo ""
  echo "   >>> Open http://localhost:5173 in your browser <<<"
  echo ""

  wait
else
  echo "==> Starting Commodity Dashboard server (production)..."
  if [ -d "web/dist" ]; then
    echo "   Serving React build from web/dist/"
  fi
  echo "   >>> Open http://localhost:8765 in your browser <<<"
  exec python server/main.py "${PY_ARGS[@]}"
fi
