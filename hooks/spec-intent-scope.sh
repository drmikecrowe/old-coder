#!/bin/sh
# PreToolUse handler for old-coder-spec-intent: bound `Read` to the spec's own
# directory.
#
# EX-1 in docs/loop-alignment.md: scope is absent capability, not instruction.
# The reviewer declares `tools: Read`, already the host's floor, and `Read`
# opens any file. Its brief says "do not go looking for the codebase". That is
# an instruction. This makes it a bound, on the one host that has the mechanism.
#
# Contract, from the Claude Code hooks reference:
#   deny  = print the hookSpecificOutput JSON and exit 0. The reason is shown
#           to the reviewer, so it explains rather than just refuses.
#   allow = print nothing and exit 0. That is "no decision"; the normal
#           permission flow continues. This handler never returns "allow",
#           because an explicit allow would skip permission rules the user set.
#   fail  = exit 2. On PreToolUse that is a blocking error, and stderr becomes
#           the reason. Every unexpected path lands here.
#
# What it cannot do, stated because a bound that hides a hole is worse than no
# bound: if this file is missing, unreadable, or not executable, Claude Code
# does not deny. It logs and carries on. A hook can fail closed on its inputs.
# It cannot fail closed on its own absence. tools/hooks_registered.py is the
# CI half that catches that, and it is not a substitute for the host probes in
# hooks/README.md.

set -u

# Any exit that is not an explicit decision is a denial. Without this, a
# `command not found` exits 127, which Claude Code treats as a non-blocking
# error, and the tool call proceeds: the fail-open this whole tier exists to
# prevent.
deny_hard() {
  echo "spec-intent-scope: $1; denying Read" >&2
  exit 2
}

command -v jq >/dev/null 2>&1 || deny_hard "jq is not on PATH, so the payload cannot be parsed"

payload=$(cat) || deny_hard "could not read the hook payload from stdin"

# Empty stdin is not "no decision to make". jq exits 0 on empty input and
# prints nothing, so without this the tool name reads empty, the Read guard
# below declines, and the call proceeds. Found by the control, not by review.
[ -n "$payload" ] || deny_hard "the hook payload was empty"

tool=$(printf '%s' "$payload" | jq -r 'if type == "object" then (.tool_name // "") else error("not an object") end' 2>/dev/null) \
  || deny_hard "the hook payload is not valid JSON"

# Only Read is in scope. Anything else gets no decision from this handler.
[ "$tool" = "Read" ] || exit 0

path=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // ""' 2>/dev/null) \
  || deny_hard "the payload carried no readable tool_input"

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }' || deny_hard "could not encode the denial"
  exit 0
}

[ -n "$path" ] || deny "This Read carried no file_path. The spec reviewer reads the request and the SPEC, nothing else."

# Deny by default, allow by path. The allow is a single resolved-prefix test,
# never a list of directories someone thought of.
scope=${OLD_CODER_SPEC_DIR:-}
[ -n "$scope" ] || deny "OLD_CODER_SPEC_DIR is not set, so no path is in scope. The spec reviewer reads the request and the SPEC, nothing else. Set it to the task's artifact directory before spawning the reviewer."
[ -d "$scope" ] || deny "OLD_CODER_SPEC_DIR is set to '$scope', which is not a directory, so no path is in scope."

# Resolve both sides before comparing. A prefix test on unresolved paths is
# defeated by `..` and by a symlink.
#
# Every component is resolved, the final one included. Resolving only the
# parent directory leaves a hole: a symlink sitting inside the spec directory
# and pointing at a source file passes the prefix test while reading the file
# the bound exists to hide. That hole was open in the first draft of this
# handler and is the reason this comment is here.
readlink -f -- / >/dev/null 2>&1 || deny_hard "readlink -f is unavailable, so paths cannot be resolved"

real_scope=$(readlink -f -- "$scope") && [ -n "$real_scope" ] \
  || deny_hard "could not resolve OLD_CODER_SPEC_DIR"
real_path=$(readlink -f -- "$path") && [ -n "$real_path" ] \
  || deny "'$path' does not resolve to a location this reviewer may read."

case "$real_path" in
  "$real_scope"/*) exit 0 ;;
  "$real_scope") exit 0 ;;
esac

deny "Read of '$path' is outside the spec directory. You are the spec-intent reviewer: the request and the SPEC are the whole world, and there is no implementation yet that can answer your question. Re-read the intent you were given instead."
