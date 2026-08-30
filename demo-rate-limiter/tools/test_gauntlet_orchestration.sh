#!/bin/sh
# Negative controls for the gauntlet's layer-completion contract.
cd "$(dirname "$0")/.." || { echo "FAIL: cannot enter demo root" >&2; exit 2; }

failures=0

expect_rc() {
  want=$1; got=$2; what=$3
  if [ "$got" -eq "$want" ]; then
    echo "  ok: $what (rc=$got)"
  else
    echo "  NOT OK: $what (want rc $want, got rc $got)"
    failures=$((failures + 1))
  fi
}

expect_contains() {
  output=$1; needle=$2; what=$3
  case "$output" in
    *"$needle"*) echo "  ok: $what" ;;
    *)
      echo "  NOT OK: $what (missing: $needle)"
      failures=$((failures + 1))
      ;;
  esac
}

expect_absent() {
  output=$1; needle=$2; what=$3
  case "$output" in
    *"$needle"*)
      echo "  NOT OK: $what (unexpected: $needle)"
      failures=$((failures + 1))
      ;;
    *) echo "  ok: $what" ;;
  esac
}

# 1. Omitting an expected layer must make the final audit fail and name it.
output=$({
  . tools/gauntlet_layers.sh
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    [ "$layer" = mutation ] || run_layer "$layer" true
  done
  finish_gauntlet
} 2>&1)
rc=$?
expect_rc 1 "$rc" "omitted layer fails the final audit"
expect_contains "$output" "missing layer 'mutation'" "omitted layer is named"
expect_absent "$output" "all layers green" "omitted layer cannot report green"

# 2. A broken command must preserve its status, name its layer and stop before
#    later work. This specifically guards against relying on set -e through an
#    AND-list or another conditional context.
output=$(sh -c '
  set -e
  . tools/gauntlet_layers.sh
  run_layer mutation sh -c "exit 7"
  echo LATER-LAYER-RAN
' 2>&1)
rc=$?
expect_rc 7 "$rc" "failed command status is preserved"
expect_contains "$output" "layer 'mutation' failed (rc=7)" "failed layer is named"
expect_absent "$output" "LATER-LAYER-RAN" "failed command stops later work"
expect_absent "$output" "all layers green" "failed command cannot report green"

# 3. A typo in a layer name must not create a new, unrequired layer.
output=$(sh -c '
  . tools/gauntlet_layers.sh
  run_layer mutatoin true
' 2>&1)
rc=$?
expect_rc 2 "$rc" "unknown layer fails"
expect_contains "$output" "unknown layer 'mutatoin'" "unknown layer is named"

# 4. Re-running one cheap layer must not stand in for a missing layer.
output=$(sh -c '
  . tools/gauntlet_layers.sh
  run_layer mutation true
  run_layer mutation true
' 2>&1)
rc=$?
expect_rc 2 "$rc" "duplicate layer fails"
expect_contains "$output" "duplicate layer 'mutation'" "duplicate layer is named"

# 5. The controls are not a script that can only fail: one successful command
#    for every expected layer reaches the one legitimate all-green message.
output=$({
  . tools/gauntlet_layers.sh
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    run_layer "$layer" true
  done
  finish_gauntlet
} 2>&1)
rc=$?
expect_rc 0 "$rc" "complete manifest passes"
expect_contains "$output" "=== gauntlet: all layers green ===" "complete manifest reports green"

# Scenarios 6-11 exercise the exit trap: the completion stamp written on every
# path, and the exit vocabulary (0 green, 2 layer verdict, 3 orchestration
# failure, anything else a crash passed through).
stampdir=$(mktemp -d)
fake_state="$stampdir/fake_state.sh"
printf '#!/bin/sh\necho "source commit abc123"\n' > "$fake_state"
chmod +x "$fake_state"

# 6. A complete run through the trap exits 0 and is stamped green, carrying
#    the binding its source-state command produced.
stamp="$stampdir/green.txt"
output=$(GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD="$fake_state" sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    run_layer "$layer" true
  done
  finish_gauntlet
' 2>&1)
rc=$?
expect_rc 0 "$rc" "green run exits 0 through the trap"
expect_contains "$output" "=== gauntlet: all layers green ===" "green run still reports green"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "result: green" "green run is stamped green"
expect_contains "$stamp_content" "source_state: source commit abc123" "green stamp carries the binding"

# 7. A failed layer exits with the layer-verdict code and is stamped with the
#    layer's name and its own preserved status.
stamp="$stampdir/layer-failed.txt"
output=$(GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD="$fake_state" sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  run_layer mutation sh -c "exit 7"
' 2>&1)
rc=$?
expect_rc 2 "$rc" "failed layer exits with the layer-verdict code"
expect_contains "$output" "layer 'mutation' failed (rc=7)" "failed layer is still named on stderr"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "result: layer-failed (mutation, rc=7)" "failed layer is stamped with name and status"
expect_absent "$stamp_content" "result: green" "failed layer cannot be stamped green"

# 8. An omitted layer is an orchestration failure: exit 3, stamped as such,
#    naming what is missing.
stamp="$stampdir/omitted.txt"
output=$(GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD="$fake_state" sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    [ "$layer" = mutation ] || run_layer "$layer" true
  done
  finish_gauntlet
' 2>&1)
rc=$?
expect_rc 3 "$rc" "omitted layer exits with the orchestration-failure code"
expect_contains "$output" "missing layer 'mutation'" "omitted layer is still named"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "result: orchestration-error" "omitted layer is stamped as an orchestration error"
expect_contains "$stamp_content" "mutation" "the missing layer is named in the stamp"

# 9. A failure outside any layer is a crash: its status passes through
#    unchanged, and the stamp says crash rather than inventing a verdict.
stamp="$stampdir/crash.txt"
GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD="$fake_state" sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  run_layer mutation true
  exit 9
' > /dev/null 2>&1
rc=$?
expect_rc 9 "$rc" "a crash keeps its own status"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "result: crash (rc=9)" "a crash is stamped as one"

# 10. Exiting 0 before the completion audit must not read as success: the
#     trap remaps it and the stamp says incomplete.
stamp="$stampdir/incomplete.txt"
GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD="$fake_state" sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  run_layer mutation true
  exit 0
' > /dev/null 2>&1
rc=$?
expect_rc 3 "$rc" "exit 0 before the audit is remapped to the orchestration-failure code"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "result: incomplete" "exit 0 before the audit is stamped incomplete"
expect_absent "$stamp_content" "result: green" "exit 0 before the audit cannot be stamped green"

# 11. A stamp never carries a binding its source-state command did not
#     produce; the failure is recorded as unavailable, not guessed.
stamp="$stampdir/no-binding.txt"
output=$(GAUNTLET_STAMP="$stamp" GAUNTLET_SOURCE_STATE_CMD=false sh -c '
  set -e
  . tools/gauntlet_layers.sh
  install_gauntlet_exit_trap
  for layer in $GAUNTLET_EXPECTED_LAYERS; do
    run_layer "$layer" true
  done
  finish_gauntlet
' 2>&1)
rc=$?
expect_rc 0 "$rc" "an unavailable binding does not fail the run by itself"
expect_contains "$output" "=== gauntlet: all layers green ===" "the layers still report green"
stamp_content=$(cat "$stamp" 2>/dev/null)
expect_contains "$stamp_content" "source_state: unavailable" "a failed source-state command is stamped unavailable"
expect_absent "$stamp_content" "abc123" "no binding content is invented"

rm -rf "${stampdir:?}"

if [ "$failures" -ne 0 ]; then
  echo "FAIL: $failures orchestration expectation(s) violated"
  exit 1
fi
echo "orchestration self-test clean"
