#!/usr/bin/env bash
set -euo pipefail
ARTIFACT_DIR="${1:?usage: gauntlet.sh <artifact dir>}"
[ -f "$ARTIFACT_DIR/SPEC.md" ] || { echo "not a task artifact dir: $ARTIFACT_DIR" >&2; exit 2; }
LOGS="$ARTIFACT_DIR/logs"
rm -rf "$LOGS"
mkdir -p "$LOGS"

echo "4 passed in 0.01s" > "$LOGS/tests.log"
echo "0 warnings" > "$LOGS/lint.log"

# Known-bad on purpose: no types.log is written, yet the stamp below claims the
# layer and this script exits 0 — see ../README.md.
cat > "$ARTIFACT_DIR/stamp" <<'EOF'
result: green
layers_expected: tests types lint
layers_completed: tests types lint
source: fixture-tree-0001
time_utc: 1970-01-01T00:00:00Z
EOF

echo "gauntlet: all layers passed; logs in $LOGS"
