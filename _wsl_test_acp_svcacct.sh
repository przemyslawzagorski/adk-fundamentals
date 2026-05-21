#!/bin/bash
# End-to-end ACP test on WSL with Windows service account session
set +e
echo "=== STEP 1: Backup user session, copy Windows service account session ==="
cp ~/.augment/session.json ~/.augment/session.json.user-backup 2>/dev/null
cp /mnt/c/Users/NBPZAGORSKI/.augment/session.json ~/.augment/session.json
chmod 600 ~/.augment/session.json
python3 -c "import json; d=json.load(open('/home/mfcadmin/.augment/session.json')); print('  tenant:', d.get('tenantURL')); print('  scopes:', d.get('scopes'))"

echo
echo "=== STEP 2: Direct CLI test (--print --quiet) ==="
auggie --print "Reply with single word: pong" --quiet --model sonnet4.5
echo "  exit=$?"

echo
echo "=== STEP 3: ACP via SDK (smoke_test 6 7 8, no AUGGIE_USE_CLI) ==="
cd ~/adk23-test/module_23_auggie_integration
source .venv/bin/activate
unset AUGGIE_USE_CLI
export AUGGIE_MODEL=sonnet4.5
export AUGGIE_TIMEOUT=180
export PYTHONIOENCODING=utf-8
time python smoke_test.py 6 7 8
echo "  exit=$?"
