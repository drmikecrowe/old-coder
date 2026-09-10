#!/bin/sh
# Controls for tools/audit_sweep.py, and specifically for the hooks-tier lift.
#
# The lift lets an audit row read `enforced` for a bound its agent's tool list
# would otherwise defeat, when a PreToolUse hook in that agent's frontmatter
# matches the defeating tool. A lift nobody has watched refuse is not a lift:
# it is a way to write `enforced` next to any agent that mentions hooks.
#
# Each case builds a fixture agent tree, so the controls never depend on what
# the real agents happen to declare today.
set -u
cd "$(dirname "$0")/.." || exit 1
SWEEP=tools/audit_sweep.py
# Deliberately not named PY: the gauntlet exports PY as a *directory*
# (.venv/bin), and inheriting it here executes a directory and exits 126.
PYTHON=${PYTHON:-python3}
WORK=$(mktemp -d) || exit 1
trap 'rm -rf "$WORK"' EXIT

fails=0
pass() { echo "  ok   $1"; }
fail() { echo "  FAIL $1" >&2; fails=$((fails + 1)); }

# probe <dir> <handler-stem>: record a host probe for that handler
probe() {
  mkdir -p "$WORK/$1/hooks/probes"
  echo "recorded" > "$WORK/$1/hooks/probes/$2-deadbeef.md"
}

# agent <dir> <name> <tools> [matcher]
agent() {
  mkdir -p "$WORK/$1/skills/old-coder/agents"
  {
    echo "---"
    echo "name: $2"
    echo "tools: $3"
    if [ -n "${4:-}" ]; then
      echo "hooks:"
      echo "  PreToolUse:"
      echo "    - matcher: $4"
      echo "      hooks:"
      echo "        - type: command"
      echo "          command: probe-hook.sh"
    fi
    echo "---"
    echo "body"
  } > "$WORK/$1/skills/old-coder/agents/$2.md"
}

# audit <file> <status> <evidence>
audit() {
  {
    echo "| Id | Rule | Status | Evidence |"
    echo "|---|---|---|---|"
    echo "| EX-1 | scope is absent capability | $2 | \`probe-agent\` $3 |"
  } > "$WORK/$1"
}

expect() {
  want=$1; shift
  label=$1; shift
  "$PYTHON" "$SWEEP" "$@" >/dev/null 2>&1
  got=$?
  if [ "$got" -eq "$want" ]; then pass "$label"; else fail "$label (wanted exit $want, got $got)"; fi
}

audit enforced.md enforced "cannot reach the codebase"
audit accepted.md accepted "cannot reach the codebase"
audit unattributed.md enforced "cannot reach the codebase"
# Strip the agent id so the row names nobody. The backticks are literal
# markdown, not a command substitution.
# shellcheck disable=SC2016
sed -i 's/`probe-agent` //' "$WORK/unattributed.md"

agent no-hook probe-agent Read
agent read-hook probe-agent Read Read
agent bash-hook probe-agent Read Bash
agent multi probe-agent "Read, Grep" Read
agent multi-both probe-agent "Read, Grep" "Read|Grep"

for d in read-hook multi-both; do probe "$d" probe-hook; done

expect 1 "no hook: enforced is still an overclaim" \
  "$WORK/enforced.md" "$WORK/no-hook"

expect 0 "a PreToolUse hook on Read lifts the overclaim" \
  "$WORK/enforced.md" "$WORK/read-hook"

expect 1 "a hook on a different tool does not lift it" \
  "$WORK/enforced.md" "$WORK/bash-hook"

expect 1 "a hook covering only one of two defeating tools does not lift it" \
  "$WORK/enforced.md" "$WORK/multi"

expect 0 "a hook covering both defeating tools lifts it" \
  "$WORK/enforced.md" "$WORK/multi-both"

# The attack that defeated the first version of the lift: a matcher that fires
# for every tool, plus a handler that does nothing, silencing the rows this
# repository says a hook cannot close at all.
agent wildcard probe-agent "Read, Bash" ".*"
probe wildcard probe-hook
expect 1 "a wildcard matcher does not lift anything" \
  "$WORK/enforced.md" "$WORK/wildcard"

agent shell-hook probe-agent "Read, Bash" "Read|Bash"
probe shell-hook probe-hook
audit shellrow enforced "cannot reach the codebase"
expect 1 "a hook never lifts a shell tool, whatever it matches" \
  "$WORK/shellrow" "$WORK/shell-hook"

agent unprobed probe-agent Read Read
expect 1 "an exact hook with no recorded probe does not lift" \
  "$WORK/enforced.md" "$WORK/unprobed"

expect 0 "a row that does not read enforced is not graded on tools" \
  "$WORK/accepted.md" "$WORK/no-hook"

expect 1 "a row naming no agent is still unattributed" \
  "$WORK/unattributed.md" "$WORK/read-hook"

# Fail-closed paths. A sweep that reads nothing agrees with everything.
expect 1 "a missing audit is an error, not a pass" \
  "$WORK/nosuch.md" "$WORK/read-hook"

mkdir -p "$WORK/empty"
expect 1 "an agent tree with no frontmatter is an error, not a pass" \
  "$WORK/enforced.md" "$WORK/empty"

if [ "$fails" -ne 0 ]; then
  echo "audit-sweep controls: $fails failure(s)" >&2
  exit 1
fi
echo "audit-sweep controls: all green (12 cases)"
