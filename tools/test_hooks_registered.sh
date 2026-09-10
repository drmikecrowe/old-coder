#!/bin/sh
# Controls for tools/hooks_registered.py.
#
# VE-2: a check must be shown able to fail before its pass counts. Until this
# file existed, `hooks-registered` was a layer nobody had watched fail, and
# demo-rate-limiter/evidence.md credited non-vacuity it could not show. An
# adversarial round said so.
#
# Two properties, and the second is the one an earlier version got wrong:
#   it fails when the tier's handler is deleted, renamed or left non-executable
#   it passes on a host that has not opted in, because the tier is opt-in and a
#   check that reddens for a reader's choice is a check people learn to ignore
# The '${...}' strings below are literal frontmatter content for the check
# under test to expand, never this shell's expansions.
# shellcheck disable=SC2016
set -u
cd "$(dirname "$0")/.." || exit 1
CHECK=tools/hooks_registered.py
PYTHON=${PYTHON:-python3}
WORK=$(mktemp -d) || exit 1
trap 'rm -rf "$WORK"' EXIT

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1" >&2; fails=$((fails + 1)); }

# fixture <dir> <command-value>
fixture() {
  root="$WORK/$1"
  mkdir -p "$root/skills/old-coder/agents" "$root/hooks"
  printf '#!/bin/sh\nexit 0\n' > "$root/hooks/probe-hook.sh"
  chmod +x "$root/hooks/probe-hook.sh"
  {
    echo "---"
    echo "name: probe-agent"
    echo "tools: Read"
    echo "hooks:"
    echo "  PreToolUse:"
    echo "    - matcher: Read"
    echo "      hooks:"
    echo "        - type: command"
    echo "          command: \"$2\""
    echo "---"
    echo "body"
  } > "$root/skills/old-coder/agents/probe.md"
}

expect() {
  want=$1; label=$2; shift 2
  "$@" >/dev/null 2>&1
  got=$?
  if [ "$got" -eq "$want" ]; then pass "$label"; else fail "$label (wanted exit $want, got $got)"; fi
}

fixture good '${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/probe-hook.sh'
expect 0 "a present, executable handler passes" \
  "$PYTHON" "$CHECK" "$WORK/good"

# The property the earlier version broke. No CLAUDE_CONFIG_DIR, no symlink:
# exactly this repository's CI.
expect 0 "a host that never opted in still passes" \
  env -u CLAUDE_CONFIG_DIR HOME="$WORK/nowhere" "$PYTHON" "$CHECK" "$WORK/good"

fixture deleted '${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/probe-hook.sh'
rm "$WORK/deleted/hooks/probe-hook.sh"
expect 1 "a deleted handler fails" \
  "$PYTHON" "$CHECK" "$WORK/deleted"

fixture unexec '${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/probe-hook.sh'
chmod -x "$WORK/unexec/hooks/probe-hook.sh"
expect 1 "a non-executable handler fails" \
  "$PYTHON" "$CHECK" "$WORK/unexec"

fixture renamed '${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/typo-hook.sh'
expect 1 "a frontmatter naming a handler that is not in hooks/ fails" \
  "$PYTHON" "$CHECK" "$WORK/renamed"

fixture outside '/bin/true'
expect 1 "a hook pointing at an arbitrary binary fails" \
  "$PYTHON" "$CHECK" "$WORK/outside"

fixture emptycmd ''
expect 1 "an empty command fails" \
  "$PYTHON" "$CHECK" "$WORK/emptycmd"

mkdir -p "$WORK/noagents"
expect 1 "an agent tree with no frontmatter is an error, not a pass" \
  "$PYTHON" "$CHECK" "$WORK/noagents"

if [ "$fails" -ne 0 ]; then
  echo "hooks-registered controls: $fails failure(s)" >&2
  exit 1
fi
echo "hooks-registered controls: all green (8 cases)"
