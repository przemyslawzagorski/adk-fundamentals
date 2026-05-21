#!/usr/bin/env bash
# Concierge Web — Linux/WSL launcher (ACP native, no CLI fallback)
set -euo pipefail

PORT="${CONCIERGE_PORT:-8770}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/../../.." && pwd)"

BUILD_FRONTEND=0
OPEN_BROWSER=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build) BUILD_FRONTEND=1; shift ;;
    --open)  OPEN_BROWSER=1; shift ;;
    --port)  PORT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "==> Concierge Web (Linux/WSL)"
echo "    Repo:  $REPO_ROOT"
echo "    Port:  $PORT"

if [[ "$BUILD_FRONTEND" == "1" ]]; then
  echo "==> Building frontend..."
  pushd "$HERE/frontend" >/dev/null
  [[ ! -d node_modules ]] && npm install
  npm run build
  popd >/dev/null
fi

export CONCIERGE_PORT="$PORT"
# Linux/WSL: zostaw natywny ACP (nie wymuszaj CLI)
unset AUGGIE_USE_CLI || true

if [[ "$OPEN_BROWSER" == "1" ]]; then
  ( sleep 2 && (xdg-open "http://127.0.0.1:$PORT" || open "http://127.0.0.1:$PORT") ) &
fi

cd "$REPO_ROOT"
echo "==> Starting FastAPI on http://127.0.0.1:$PORT"
exec python -m adk_training.module_23_auggie_integration.web.app
