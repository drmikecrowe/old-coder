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

# A project tree with an artifact root, as the skill would leave it.
PROJ="$WORK/proj"
mkdir -p "$PROJ/.old-coder/20260911-101500-widget" "$PROJ/src/deep/deeper"
SPECDIR="$PROJ/.old-coder/20260911-101500-widget"
echo "# SPEC" > "$SPECDIR/SPEC.md"
echo "source the reviewer must not reach" > "$PROJ/src/impl.py"
ln -s "$PROJ/src/impl.py" "$SPECDIR/innocent.md"
printf '%s\n' "$SPECDIR" > "$PROJ/.old-coder/scope"

# A project with no artifact root at all.
BARE="$WORK/bare"
mkdir -p "$BARE"

# A project whose artifact root has no pointer.
NOPTR="$WORK/noptr"
mkdir -p "$NOPTR/.old-coder"

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1" >&2; fails=$((fails + 1)); }

# Run the handler on a payload. Echoes "<exit>:<decision>", where decision is
# `deny`, `none` (no decision printed, the normal flow continues), or `hard`.
# $1 is the cwd the payload reports; the handler walks up from it.
decide() {
  out=$(printf '%s' "$2" | sh "$HOOK" 2>/dev/null)
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

# payload <cwd> <file_path>
payload() {
  printf '{"tool_name":"Read","cwd":"%s","tool_input":{"file_path":"%s"}}' "$1" "$2"
}

check "a source file outside the scope is denied" \
  "" "$(payload "$PROJ" "$PROJ/src/impl.py")" "0:deny"

check "a file inside the scope gets no decision" \
  "" "$(payload "$PROJ" "$SPECDIR/SPEC.md")" "0:none"

# The case an environment variable could not express: the artifact directory
# is named inside the session, long after the claude process took its env.
check "a directory created after the session started is in scope" \
  "" "$(payload "$PROJ" "$SPECDIR/SPEC.md")" "0:none"

check "a cwd deep inside the project still finds the artifact root" \
  "" "$(payload "$PROJ/src/deep/deeper" "$SPECDIR/SPEC.md")" "0:none"

check "no artifact root anywhere above cwd denies" \
  "" "$(payload "$BARE" "$BARE/anything.txt")" "0:deny"

check "an artifact root with no pointer denies" \
  "" "$(payload "$NOPTR" "$NOPTR/anything.txt")" "0:deny"

# The two absences must be told apart by anyone reading a transcript.
no_root=$(printf '%s' "$(payload "$BARE" "$BARE/x")" | sh "$HOOK" 2>/dev/null)
no_ptr=$(printf '%s' "$(payload "$NOPTR" "$NOPTR/x")" | sh "$HOOK" 2>/dev/null)
case "$no_root" in
  *"no old-coder task is in progress"*)
    case "$no_ptr" in
      *"never recorded"*) pass "the two absences give different reasons" ;;
      *) fail "the two absences give different reasons (pointer case wrong)" ;;
    esac ;;
  *) fail "the two absences give different reasons (no-root case wrong)" ;;
esac

printf '' > "$PROJ/.old-coder/scope"
check "an empty pointer denies" \
  "" "$(payload "$PROJ" "$SPECDIR/SPEC.md")" "0:deny"

printf '%s\n' "$SPECDIR/SPEC.md" > "$PROJ/.old-coder/scope"
check "a pointer naming a file rather than a directory denies" \
  "" "$(payload "$PROJ" "$SPECDIR/SPEC.md")" "0:deny"

printf '%s   \n\n' "$SPECDIR" > "$PROJ/.old-coder/scope"
check "a pointer with trailing whitespace still resolves" \
  "" "$(payload "$PROJ" "$SPECDIR/SPEC.md")" "0:none"

printf '%s\n' "$SPECDIR" > "$PROJ/.old-coder/scope"

check "dot-dot out of the scope is denied" \
  "" "$(payload "$PROJ" "$SPECDIR/../../src/impl.py")" "0:deny"

# The hole that was open in H2's first draft.
check "a symlink inside the scope pointing out is denied" \
  "" "$(payload "$PROJ" "$SPECDIR/innocent.md")" "0:deny"

check "a Read with no file_path is denied" \
  "" "{\"tool_name\":\"Read\",\"cwd\":\"$PROJ\",\"tool_input\":{}}" "0:deny"

check "a payload with no cwd fails closed" \
  "" '{"tool_name":"Read","tool_input":{"file_path":"/etc/hostname"}}' "2:hard"

check "malformed input fails closed" \
  "" 'not json' "2:hard"

check "an empty payload fails closed" \
  "" '' "2:hard"

check "a non-object payload fails closed" \
  "" '"a string"' "2:hard"

check "another tool is left to the normal flow" \
  "" "{\"tool_name\":\"Glob\",\"cwd\":\"$PROJ\",\"tool_input\":{\"pattern\":\"**/*.py\"}}" "0:none"

# Non-vacuity: the driver must be able to report a failure. If this control
# passed, `check` is comparing nothing and every ok above is decoration.
got=$(decide "" "$(payload "$PROJ" "$PROJ/src/impl.py")")
if [ "$got" = "0:none" ]; then
  fail "non-vacuity: the driver reported allow for a denied read"
else
  pass "non-vacuity: a deny is distinguishable from an allow ($got)"
fi

if [ "$fails" -ne 0 ]; then
  echo "spec-intent-scope controls: $fails failure(s)" >&2
  exit 1
fi
echo "spec-intent-scope controls: all green, 18 cases (host probes are still required; see hooks/README.md)"
