#!/bin/sh
# Controls for hooks/spec-intent-scope.sh.
#
# What these prove: the handler decides correctly for the inputs Claude Code
# would hand it. Deny by default, allow by resolved path, fail closed.
#
# What these DO NOT prove, and no amount of them ever will: that Claude Code
# actually calls the handler. Only a recorded host probe proves that. See
# hooks/README.md. A green run here is not evidence that the reviewer is
# bounded; it is evidence that the script would bound it if invoked.
set -u
cd "$(dirname "$0")" || exit 1
HOOK=./spec-intent-scope.sh
WORK=$(mktemp -d) || exit 1
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/spec"
echo "# SPEC" > "$WORK/spec/SPEC.md"
echo "source the reviewer must not reach" > "$WORK/outside.txt"
ln -s "$WORK/outside.txt" "$WORK/spec/innocent.md"

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1" >&2; fails=$((fails + 1)); }

# Run the handler on a payload. Echoes "<exit>:<decision>", where decision is
# `deny`, `none` (no decision printed, the normal flow continues), or `hard`.
# $1 is the scope directory, or the literal UNSET to remove the variable.
decide() {
  if [ "$1" = "UNSET" ]; then
    out=$(printf '%s' "$2" | env -u OLD_CODER_SPEC_DIR sh "$HOOK" 2>/dev/null)
  else
    out=$(printf '%s' "$2" | env OLD_CODER_SPEC_DIR="$1" sh "$HOOK" 2>/dev/null)
  fi
  status=$?
  if [ "$status" -eq 2 ]; then echo "2:hard"; return; fi
  case "$out" in
    *'"permissionDecision": "deny"'*) echo "$status:deny" ;;
    "") echo "$status:none" ;;
    *) echo "$status:other" ;;
  esac
}

check() {
  got=$(decide "$2" "$3")
  if [ "$got" = "$4" ]; then pass "$1"; else fail "$1 (wanted $4, got $got)"; fi
}

S="$WORK/spec"

check "a source file outside the scope is denied" \
  "$S" '{"tool_name":"Read","tool_input":{"file_path":"/etc/hostname"}}' "0:deny"

check "a file inside the scope gets no decision" \
  "$S" "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$WORK/spec/SPEC.md\"}}" "0:none"

check "an unset scope denies what it would otherwise allow" \
  "UNSET" "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$WORK/spec/SPEC.md\"}}" "0:deny"

check "a scope pointing at no directory denies" \
  "$WORK/nope" "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$WORK/spec/SPEC.md\"}}" "0:deny"

check "dot-dot out of the scope is denied" \
  "$S" "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$WORK/spec/../outside.txt\"}}" "0:deny"

# The hole that was open in the first draft. A blocklist or a parent-only
# resolve lets this through while reading the file the bound exists to hide.
check "a symlink inside the scope pointing out is denied" \
  "$S" "{\"tool_name\":\"Read\",\"tool_input\":{\"file_path\":\"$WORK/spec/innocent.md\"}}" "0:deny"

check "a Read with no file_path is denied" \
  "$S" '{"tool_name":"Read","tool_input":{}}' "0:deny"

check "malformed input fails closed" \
  "$S" 'not json' "2:hard"

check "an empty payload fails closed" \
  "$S" '' "2:hard"

check "a non-object payload fails closed" \
  "$S" '"a string"' "2:hard"

check "another tool is left to the normal flow" \
  "$S" '{"tool_name":"Glob","tool_input":{"pattern":"**/*.py"}}' "0:none"

# Non-vacuity: the driver must be able to report a failure. If this control
# passed, `check` is comparing nothing and every ok above is decoration.
got=$(decide "$S" '{"tool_name":"Read","tool_input":{"file_path":"/etc/hostname"}}')
if [ "$got" = "0:none" ]; then
  fail "non-vacuity: the driver reported allow for a denied read"
else
  pass "non-vacuity: a deny is distinguishable from an allow ($got)"
fi

if [ "$fails" -ne 0 ]; then
  echo "spec-intent-scope controls: $fails failure(s)" >&2
  exit 1
fi
echo "spec-intent-scope controls: all green (host probes are still required; see hooks/README.md)"
