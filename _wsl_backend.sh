#!/bin/bash
set -e

WIN_SRC=/mnt/c/Users/NBPZAGORSKI/IdeaProjects/adk-fundamentals/adk_training/module_23_auggie_integration
WSL_DIR=~/adk23-test/module_23_auggie_integration

# --- auth: kopiuj session z Windows ---
mkdir -p ~/.augment
cp /mnt/c/Users/NBPZAGORSKI/.augment/session.json ~/.augment/session.json
chmod 600 ~/.augment/session.json
echo "=== session OK ==="

# --- synchronizuj kod z Windows ---
cd "$WSL_DIR"
for f in auggie_factory.py tools.py agent.py caching.py cost_tracker.py resilience.py health_check.py; do
    cp "$WIN_SRC/$f" . 2>/dev/null && echo "synced: $f" || echo "SKIP: $f"
done

# kopiuj web/ bez __pycache__ (Windows NTFS __pycache__ blokuje cp -r)
mkdir -p web/
for f in app.py runs.py __init__.py start.sh; do
    cp "$WIN_SRC/web/$f" web/ 2>/dev/null && echo "synced: web/$f" || echo "SKIP: web/$f"
done
# frontend jest statyczny - wystarczy symlink
[ -d web/frontend ] || ln -s "$WIN_SRC/web/frontend" web/frontend 2>/dev/null || true
echo "synced: web/"

source .venv/bin/activate

# --- env ---
export AUGGIE_CLI_PATH=/usr/bin/auggie
unset AUGGIE_USE_CLI          # ACP mode dla analyze_codebase
export AUGGIE_MODEL=sonnet4.5
export AUGGIE_TIMEOUT=180
export CONCIERGE_PORT=8770
export AUGGIE_WORKSPACE="$WIN_SRC/.."
export PYTHONIOENCODING=utf-8
# adk_training package (module_24, itd.) jest na Windows FS — dodaj do PYTHONPATH
export PYTHONPATH=/mnt/c/Users/NBPZAGORSKI/IdeaProjects/adk-fundamentals

echo ""
echo "=== Backend WSL starting on 0.0.0.0:8770 ==="
echo "    ACP mode: analyze_codebase via native /usr/bin/auggie"
echo ""

# 0.0.0.0 żeby Windows mógł się połączyć przez localhost (WSL2 port forwarding)
python -m uvicorn web.app:app --host 0.0.0.0 --port 8770 --log-level info
