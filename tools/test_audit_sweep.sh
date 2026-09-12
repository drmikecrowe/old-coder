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

# Counted rather than written down. A hard-coded total goes stale the first
# time someone adds a case, and a control suite that misreports its own size
# is the shape of defect this file exists to catch.
fails=0
passes=0
pass() { echo "  ok   $1"; passes=$((passes + 1)); }
fail() { echo "  FAIL $1" >&2; fails=$((fails + 1)); }

# probe <dir> <handler-stem> [hash-override]: record a host probe naming the
# handler's sha256. A record that names no hash, or a stale one, must not lift.
probe() {
  mkdir -p "$WORK/$1/hooks/probes"
  if [ -n "${3:-}" ]; then
    sha=$3
  else
    sha=$(sha256sum "$WORK/$1/hooks/$2.sh" | cut -d" " -f1)
  fi
  printf 'handler sha256: %s\n' "$sha" > "$WORK/$1/hooks/probes/$2-deadbeef.md"
}

# agent <dir> <name> <tools> [matcher]
agent() {
  mkdir -p "$WORK/$1/skills/old-coder/agents" "$WORK/$1/hooks"
  printf '#!/bin/sh\nexit 0\n' > "$WORK/$1/hooks/probe-hook.sh"
  chmod +x "$WORK/$1/hooks/probe-hook.sh"
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
expect 1 "an unlisted handler never lifts a shell tool, whatever it matches" \
  "$WORK/shellrow" "$WORK/shell-hook"

# ---------------------------------------------------------- the shell lift
#
# A2 object H3 changed the shell rule from "never" to "only by a handler this
# module names". Four conditions, all required. These cases are one per
# condition, because a lift that cannot be watched refusing is a lift that
# writes `enforced` next to any agent whose frontmatter mentions a shell.
#
# The stem is the real one on purpose. ALLOWLIST_SHELL_HANDLERS is matched by
# name, so a fixture using a made-up stem would prove the constant is consulted
# and nothing about what happens when it matches.

# grammar_agent <dir> <matcher>: an agent declaring Bash, with a hook whose
# handler carries the stem the sweep names as an allowlist grammar.
grammar_agent() {
  mkdir -p "$WORK/$1/skills/old-coder/agents" "$WORK/$1/hooks"
  printf '#!/bin/sh\nexit 0\n' > "$WORK/$1/hooks/adversary-bash-grammar.sh"
  chmod +x "$WORK/$1/hooks/adversary-bash-grammar.sh"
  {
    echo "---"
    echo "name: probe-agent"
    echo "tools: Read, Bash"
    echo "hooks:"
    echo "  PreToolUse:"
    echo "    - matcher: $2"
    echo "      hooks:"
    echo "        - type: command"
    echo "          command: adversary-bash-grammar.sh"
    echo "---"
    echo "body"
  } > "$WORK/$1/skills/old-coder/agents/probe-agent.md"
}

# grammar_probe <dir> <with-grammar-line> [hash-override]
grammar_probe() {
  mkdir -p "$WORK/$1/hooks/probes"
  if [ -n "${3:-}" ]; then
    sha=$3
  else
    sha=$(sha256sum "$WORK/$1/hooks/adversary-bash-grammar.sh" | cut -d" " -f1)
  fi
  record="$WORK/$1/hooks/probes/adversary-bash-grammar-deadbeef.md"
  printf 'handler sha256: %s\n' "$sha" > "$record"
  if [ "$2" = "yes" ]; then
    printf 'grammar: allowlist\n' >> "$record"
  fi
}

# The audit row asserts a read-only bound, which Bash defeats, so the row can
# only read `enforced` if the shell is genuinely lifted.
audit shellwrite enforced "holds no write capability"

grammar_agent lift-ok Bash
grammar_probe lift-ok yes
expect 0 "all four conditions hold: the shell is lifted" \
  "$WORK/shellwrite" "$WORK/lift-ok"

grammar_agent lift-nogrammar Bash
grammar_probe lift-nogrammar no
expect 1 "a record without the grammar declaration does not lift a shell" \
  "$WORK/shellwrite" "$WORK/lift-nogrammar"

grammar_agent lift-stale Bash
grammar_probe lift-stale yes \
  0000000000000000000000000000000000000000000000000000000000000000
expect 1 "a stale record does not lift a shell" \
  "$WORK/shellwrite" "$WORK/lift-stale"

grammar_agent lift-wildcard ".*"
grammar_probe lift-wildcard yes
expect 1 "a wildcard matcher does not lift a shell even for a named handler" \
  "$WORK/shellwrite" "$WORK/lift-wildcard"

# The grammar line alone is not a lift: the handler still has to be one this
# module names. Same record, unlisted stem.
agent lift-unlisted probe-agent "Read, Bash" Bash
mkdir -p "$WORK/lift-unlisted/hooks/probes"
printf 'handler sha256: %s\ngrammar: allowlist\n' \
  "$(sha256sum "$WORK/lift-unlisted/hooks/probe-hook.sh" | cut -d" " -f1)" \
  > "$WORK/lift-unlisted/hooks/probes/probe-hook-deadbeef.md"
expect 1 "the grammar declaration does not lift an unlisted handler" \
  "$WORK/shellwrite" "$WORK/lift-unlisted"

# A Python handler is resolved too. The grammar handler is Python, so a lookup
# that only tried .sh would refuse the real one and this suite would be green
# against a sweep that cannot see the thing it is meant to credit.
grammar_agent lift-python Bash
mv "$WORK/lift-python/hooks/adversary-bash-grammar.sh" \
  "$WORK/lift-python/hooks/adversary-bash-grammar.py"
sed -i 's/adversary-bash-grammar\.sh/adversary-bash-grammar.py/' \
  "$WORK/lift-python/skills/old-coder/agents/probe-agent.md"
mkdir -p "$WORK/lift-python/hooks/probes"
printf 'handler sha256: %s\ngrammar: allowlist\n' \
  "$(sha256sum "$WORK/lift-python/hooks/adversary-bash-grammar.py" | cut -d" " -f1)" \
  > "$WORK/lift-python/hooks/probes/adversary-bash-grammar-deadbeef.md"
expect 0 "a Python handler is found and lifts" \
  "$WORK/shellwrite" "$WORK/lift-python"

# From H3's adversarial round. The frontmatter names one extension and only the
# other exists. tools/hooks_registered.py resolves by full basename and would go
# red; this module must not disagree with it and credit a lift for a file the
# runtime will never run.
grammar_agent lift-mismatch Bash
mv "$WORK/lift-mismatch/hooks/adversary-bash-grammar.sh" \
  "$WORK/lift-mismatch/hooks/adversary-bash-grammar.py"
mkdir -p "$WORK/lift-mismatch/hooks/probes"
printf 'handler sha256: %s\ngrammar: allowlist\n' \
  "$(sha256sum "$WORK/lift-mismatch/hooks/adversary-bash-grammar.py" | cut -d" " -f1)" \
  > "$WORK/lift-mismatch/hooks/probes/adversary-bash-grammar-deadbeef.md"
expect 1 "a frontmatter naming .sh does not lift when only .py exists" \
  "$WORK/shellwrite" "$WORK/lift-mismatch"

agent unprobed probe-agent Read Read
expect 1 "an exact hook with no recorded probe does not lift" \
  "$WORK/enforced.md" "$WORK/unprobed"

# The hole this object found: a probe that graded a different version of the
# handler. "Rebind on every hook change" was prose until this refused.
agent stale probe-agent Read Read
probe stale probe-hook 0000000000000000000000000000000000000000000000000000000000000000
expect 1 "a probe naming a different handler hash does not lift" \
  "$WORK/enforced.md" "$WORK/stale"

# A superseded record that merely MENTIONS the current hash. The graded hash is
# something else, so it is not evidence about the current handler.
agent mention probe-agent Read Read
mkdir -p "$WORK/mention/hooks/probes"
cur=$(sha256sum "$WORK/mention/hooks/probe-hook.sh" | cut -d" " -f1)
{
  echo "handler sha256: 0000000000000000000000000000000000000000000000000000000000000000"
  echo "sha256 is now $cur"
} > "$WORK/mention/hooks/probes/probe-hook-legacy.md"
expect 1 "a record that mentions the current hash without grading it does not lift" \
  "$WORK/enforced.md" "$WORK/mention"

# Two declared hashes: it cannot be said which handler was graded.
agent ambiguous probe-agent Read Read
mkdir -p "$WORK/ambiguous/hooks/probes"
cur=$(sha256sum "$WORK/ambiguous/hooks/probe-hook.sh" | cut -d" " -f1)
{
  echo "handler sha256: $cur"
  echo "handler sha256: 1111111111111111111111111111111111111111111111111111111111111111"
} > "$WORK/ambiguous/hooks/probes/probe-hook-x.md"
expect 1 "a record declaring two different hashes does not lift" \
  "$WORK/enforced.md" "$WORK/ambiguous"

# The metadata block uses bullets, so the declaration may be one.
agent bullet probe-agent Read Read
mkdir -p "$WORK/bullet/hooks/probes"
cur=$(sha256sum "$WORK/bullet/hooks/probe-hook.sh" | cut -d" " -f1)
printf -- '- handler sha256: %s\n' "$cur" > "$WORK/bullet/hooks/probes/probe-hook-x.md"
expect 0 "a declaration written as a list item lifts" \
  "$WORK/enforced.md" "$WORK/bullet"

agent nohash probe-agent Read Read
mkdir -p "$WORK/nohash/hooks/probes"
echo "a probe record that names no hash at all" > "$WORK/nohash/hooks/probes/probe-hook-x.md"
expect 1 "a probe naming no hash does not lift" \
  "$WORK/enforced.md" "$WORK/nohash"

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
echo "audit-sweep controls: all green ($passes cases)"
