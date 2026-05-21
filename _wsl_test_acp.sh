#!/bin/bash
set -e

# --- auth: upewnij się że WSL ma service account session z Windows ---
cp /mnt/c/Users/NBPZAGORSKI/.augment/session.json ~/.augment/session.json
chmod 600 ~/.augment/session.json
python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.augment/session.json'))); print('=== session: tenant=' + d.get('tenantURL','?') + '  scopes=' + str(d.get('scopes','?')))"

cd ~/adk23-test/module_23_auggie_integration
cp /mnt/c/Users/NBPZAGORSKI/IdeaProjects/adk-fundamentals/adk_training/module_23_auggie_integration/auggie_factory.py .
source .venv/bin/activate
echo "=== cli_path detection ==="
python -c "import sys; sys.path.insert(0,'.'); from auggie_factory import AuggieConfig; c = AuggieConfig.from_env(); print('cli_path =', c.cli_path)"
echo
echo "=== smoke test 2 6 7 8 (ACP mode on native Linux auggie) ==="
unset AUGGIE_USE_CLI
# Force native WSL binary — WSL PATH leaks Windows npm paths (.cmd files can't exec on Linux)
export AUGGIE_CLI_PATH=/usr/bin/auggie
export AUGGIE_MODEL=sonnet4.5
export AUGGIE_TIMEOUT=180
export PYTHONIOENCODING=utf-8
time python smoke_test.py 2 6 7 8
