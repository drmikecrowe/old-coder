#!/bin/sh
# Controls for hooks/adversary-bash-grammar.py.
#
# TWO HALVES, AND THIS IS ONLY ONE OF THEM.
#
#   this file   the handler decides correctly for the payloads it is given.
#               Runs anywhere, including CI.
#   host probe  Claude Code actually invokes the handler, and the call is
#               denied. Runs only on the host, with a human watching.
#
# A green run here is consistent with a hook the runtime never calls. It is not
# the proof. hooks/probes/RUNBOOK.md carries the half that is.
#
# Non-vacuity. Every case here is run twice by `--stub`: once against the real
# handler, and once against a handler that exits 0 and says nothing. The second
# run MUST fail. A control suite that stays green against a handler which
# allows everything is measuring nothing, which is this repository's oldest
# failure mode.
#
# Usage:
#   sh hooks/test_adversary_bash_grammar.sh           run the cases
#   sh hooks/test_adversary_bash_grammar.sh --stub    prove they can fail
#
# HANDLER overrides the handler under test. The positive control reads
# hooks/harvest/harvest.jsonl and hooks/harvest/expected.tsv and needs jq.

set -u

here=$(dirname -- "$0")
root=$(cd -- "$here/.." && pwd)
HANDLER=${HANDLER:-$root/hooks/adversary-bash-grammar.py}

# Non-vacuity, run first so a broken suite cannot reach the real cases and
# report green. A handler that exits 0 and says nothing allows everything, so
# every `deny` and every `hard` case must fail against it. If this suite still
# passes, it is not testing the handler.
if [ "${1:-}" = "--stub" ]; then
  stub=$(mktemp) || exit 1
  trap 'rm -f "$stub"' EXIT INT TERM
  printf '#!/bin/sh\nexit 0\n' > "$stub"
  chmod +x "$stub"
  if HANDLER="$stub" sh "$0" >/dev/null 2>&1; then
    echo "FAIL: the suite passed against a handler that allows everything" >&2
    exit 1
  fi
  echo "adversary-bash-grammar: non-vacuity proven, the suite fails on a stub"
  exit 0
fi

pass=0
fail=0

# A PreToolUse payload for a Bash call. The command is JSON-encoded by jq so a
# case may contain any quoting the grammar has to survive.
payload_for() {
  jq -n --arg cmd "$1" '{
    hook_event_name: "PreToolUse",
    tool_name: "Bash",
    cwd: "/tmp",
    tool_input: { command: $cmd }
  }'
}

# Classify one handler run: allow, deny, hard, or broken.
#
# The three outcomes come from the hooks reference. Exit 0 with no output is
# "no decision", which lets the normal permission flow continue, and is the
# only way this handler ever permits a command. Exit 0 with the
# hookSpecificOutput JSON is a denial. Exit 2 is a blocking error.
decide() {
  out=$(printf '%s' "$1" | "$HANDLER" 2>/dev/null)
  status=$?
  if [ "$status" -eq 2 ]; then
    echo hard
    return
  fi
  if [ "$status" -ne 0 ]; then
    echo "broken(exit $status)"
    return
  fi
  if [ -z "$out" ]; then
    echo allow
    return
  fi
  case "$out" in
    *'"deny"'*) echo deny ;;
    *) echo "broken(unrecognised output)" ;;
  esac
}

check() {
  name=$1
  expect=$2
  got=$3
  if [ "$expect" = "$got" ]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL: $name: expected $expect, got $got" >&2
  fi
}

# One command through the handler, with the decision it must produce.
case_cmd() {
  check "$1" "$2" "$(decide "$(payload_for "$3")")"
}

# One raw payload through the handler, for the fail-closed paths.
case_raw() {
  check "$1" "$2" "$(decide "$3")"
}

command -v jq >/dev/null 2>&1 || {
  echo "FAIL: jq is required to build the payloads" >&2
  exit 1
}

[ -x "$HANDLER" ] || {
  echo "FAIL: handler $HANDLER is missing or not executable" >&2
  exit 1
}

# ---------------------------------------------------------------- in grammar

case_cmd "plain git diff" allow 'git diff main...HEAD --stat'
case_cmd "git -C" allow 'git -C /tmp/x diff 966bc7f...HEAD'
case_cmd "/usr/bin/git" allow '/usr/bin/git diff main...c6b20af -- src/'
case_cmd "read sequence with ;" allow "sed -n '1,40p' a.py; echo ===; sed -n '90,99p' b.py"
case_cmd "&& chain of reads" allow 'git diff --stat && git log --oneline -5'
case_cmd "pipe into head" allow 'rg -n "a|b" src/ | head -30'
case_cmd "quoted pipe is a word" allow 'rg -n "USERNS_ARG|userns" src/'
case_cmd "|| fallback between reads" allow 'cat CONTRIBUTING.md || echo missing'
case_cmd "stderr to /dev/null" allow 'git log --oneline 2>/dev/null'
case_cmd "stderr merged" allow 'ls -la /tmp 2>&1'
case_cmd "leading cd" allow 'cd /tmp; ls'
case_cmd "find with allowed predicates" allow 'find . -name "*.py" -o -name "*.sh"'
case_cmd "trailing separator is punctuation" allow 'ls /tmp ;'
case_cmd "trailing && is punctuation too" allow 'git diff --stat &&'
case_cmd "tail plain" allow 'tail -n +26 /tmp/x.log'
case_cmd "sha256sum" allow 'sha256sum hooks/adversary-bash-grammar.py'

# ------------------------------------------------------------ excluded: write

case_cmd "sed -i" deny 'sed -i s/a/b/ src/x.py'
case_cmd "sed --in-place" deny 'sed --in-place s/a/b/ src/x.py'
case_cmd "sed script that writes" deny "sed -n '1,5w /tmp/out' src/x.py"
case_cmd "rm behind an allowed head" deny 'git diff && rm -rf /tmp/x'
case_cmd "git commit" deny 'git commit -m x'
case_cmd "git push" deny 'git push'
case_cmd "git checkout" deny 'git checkout -- .'
case_cmd "find -delete" deny 'find . -name "*.pyc" -delete'
case_cmd "find -exec" deny 'find . -name "*.py" -exec rm {} ;'
case_cmd "tee" deny 'git diff | tee /tmp/out'

# --------------------------------------------------------- excluded: redirect

case_cmd "redirect to a file" deny 'git diff > /tmp/out'
case_cmd "append to a file" deny 'git diff >> /tmp/out'
case_cmd "redirect in a later segment" deny 'git diff; ls > /tmp/out'
case_cmd "input redirect" deny 'cat < /etc/passwd'

# ----------------------------------------------------- excluded: substitution

# SC2016 is disabled for this function, and the single quotes are the point.
# These cases must reach the handler as literal `$` and backtick text, exactly
# as the reviewer would have typed them. Expanding them here would test this
# script's shell instead of the grammar.
# shellcheck disable=SC2016
substitution_cases() {
  case_cmd "dollar substitution" deny 'echo $(git push)'
  case_cmd "backtick substitution" deny 'echo `git push`'
  case_cmd "variable expansion" deny 'ls "$HOME"'
  case_cmd "variable assignment" deny 'R=/tmp; ls $R'
  case_cmd "substitution inside quotes" deny 'echo "$(rm -rf /tmp/x)"'
}
substitution_cases

# ------------------------------------------------- excluded: reaching a shell

case_cmd "python3 -c" deny 'python3 -c "print(1)"'
case_cmd "python3 on a repo file" deny 'python3 tools/contract_ids.py'
case_cmd "sh on a script" deny 'sh /tmp/x.sh'
case_cmd "bash -c" deny 'bash -c "rm -rf /tmp/x"'
case_cmd "background operator" deny 'git diff & ls'
case_cmd "subshell" deny '(git diff)'

# ------------------------------------------------ excluded: escapes via flags

case_cmd "git -c reaches a command" deny 'git -c core.pager=touch\ x log'
case_cmd "git --exec-path" deny 'git --exec-path=/tmp diff'
case_cmd "rg --pre" deny 'rg --pre /tmp/x -n foo src/'

# The grammar is exactly the SPEC's table, and these pin its edge. Each of
# these is harmless, and each is outside what was approved. Found by comparing
# the handler against docs/spec-a2-h3.md after a round's coverage note asked
# whether they matched; they did not, and the handler was the wider of the two.
case_cmd "md5sum is not in the approved table" deny 'md5sum /tmp/x'
case_cmd "basename is not in the approved table" deny 'basename /tmp/x'
# -print and -print0 were added to the table by an explicit amendment after the
# round raised them. They change the output separator and reach nothing.
case_cmd "find -print is in the table by amendment" allow 'find . -name x -print'
case_cmd "find -print0 is in the table by amendment" allow 'find . -name x -print0'
# The predicates that stayed out are still out, so the amendment widened the
# table by exactly two entries rather than opening it.
case_cmd "find -prune stayed out" deny 'find . -name x -prune'
case_cmd "find -mindepth stayed out" deny 'find . -mindepth 2 -name x'
case_cmd "tail -f never ends" deny 'tail -f /tmp/x.log'
# From H3's adversarial round: -f was refused by exact match and -F was not.
# These three pin the class rather than the one spelling it found.
case_cmd "tail -F never ends either" deny 'tail -F /tmp/x.log'
case_cmd "tail --follow=name never ends" deny 'tail --follow=name /tmp/x.log'
case_cmd "a clustered follow flag never ends" deny 'tail -fn10 /tmp/x.log'

# ------------------------------------------------------------ malformed input

case_cmd "a leading separator still denies" deny '; ls /tmp'
case_cmd "a gap between two commands still denies" deny 'ls /tmp ;; wc -l'
case_cmd "unbalanced quote" deny 'rg -n "unterminated src/'
case_cmd "empty command" deny ''
case_cmd "only a separator" deny ';'
case_cmd "multiline command" deny 'git diff
rm -rf /tmp/x'

# ------------------------------------------------------- other tools, no view

# The handler decides about Bash and nothing else. A Read must get no decision,
# or this hook would bound a tool it was never scoped to and EX-1's hook would
# be fighting it.
case_raw "a Read gets no decision" allow \
  '{"hook_event_name":"PreToolUse","tool_name":"Read","cwd":"/tmp","tool_input":{"file_path":"/etc/passwd"}}'

# ------------------------------------------------------------- fail closed

# Every unexpected path exits 2. On PreToolUse an ordinary nonzero exit is a
# NON-blocking error and the call proceeds, so nothing here may exit 1 by
# accident.
case_raw "empty payload" hard ''
case_raw "not JSON" hard 'this is not json'
case_raw "JSON but not an object" hard '["PreToolUse"]'
case_raw "object with no tool_name" hard '{"cwd":"/tmp"}'
case_raw "Bash call with no tool_input" hard '{"tool_name":"Bash","cwd":"/tmp"}'
case_raw "command is not a string" hard \
  '{"tool_name":"Bash","cwd":"/tmp","tool_input":{"command":["git","diff"]}}'

# --------------------------------------------- positive control: the harvest

# Every command the reviewer actually ran, with the decision the SPEC says it
# must get. This is the half that stops the grammar from being tightened until
# it denies real work.
harvest="$root/hooks/harvest/harvest.jsonl"
expected="$root/hooks/harvest/expected.tsv"

if [ ! -r "$harvest" ] || [ ! -r "$expected" ]; then
  echo "FAIL: the harvest or its expectations are missing" >&2
  fail=$((fail + 1))
else
  rows=$(grep -c '' "$harvest")
  labels=$(grep -cv '^#' "$expected")
  if [ "$rows" -ne "$labels" ]; then
    echo "FAIL: $rows harvested commands and $labels expectations" >&2
    fail=$((fail + 1))
  fi
  index=0
  while IFS= read -r line; do
    index=$((index + 1))
    want=$(grep -v '^#' "$expected" | awk -F'\t' -v n="$index" '$1 == n { print $2 }')
    if [ -z "$want" ]; then
      echo "FAIL: harvest row $index has no expectation" >&2
      fail=$((fail + 1))
      continue
    fi
    cmd=$(printf '%s' "$line" | jq -r '.command')
    case_cmd "harvest row $index" "$want" "$cmd"
  done < "$harvest"
fi

# ------------------------------------------------------------------- report

echo "adversary-bash-grammar: $pass passed, $fail failed"
[ "$fail" -eq 0 ] || exit 1
exit 0
