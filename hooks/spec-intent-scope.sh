#!/bin/sh
# PreToolUse handler for old-coder-spec-intent: bound `Read` to the spec's own
# directory.
#
# Scope is read from `<artifact root>/scope`, a one-line pointer the SPEC step
# writes when it creates the task's artifact directory. See hooks/README.md.
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

readlink -f -- / >/dev/null 2>&1 || deny_hard "readlink -f is unavailable, so paths cannot be resolved"

# Deny by default, allow by path. The allow is a single resolved-prefix test,
# never a list of directories someone thought of.
#
# The scope comes from the artifact root, not from the environment. A hook
# inherits the environment of the `claude` process, which is fixed before the
# session starts, and the task's artifact directory is named at SPEC time
# inside the session. An environment variable therefore cannot express the one
# directory this bound is about. It can only express a directory somebody
# pre-created and exported by hand, which is a probe setup rather than a
# workflow.
cwd=$(printf '%s' "$payload" | jq -r '.cwd // ""' 2>/dev/null) \
  || deny_hard "the payload carried no readable cwd"
[ -n "$cwd" ] || deny_hard "the payload carried no cwd, so the artifact root cannot be found"

# The cwd must be absolute. `readlink -f` resolves a relative path against THIS
# process's working directory, which is wherever the agent runtime was launched
# from, not the reviewer's location. A payload carrying "." would then find the
# launch directory's artifact root and enforce some other task's scope.
case "$cwd" in
  /*) ;;
  *) deny_hard "the payload's cwd '$cwd' is not absolute, so the artifact root cannot be located" ;;
esac

# Walk up for `.old-coder/`, the way git finds `.git`. Terminates at the root.
artifact_root=""
dir=$(readlink -f -- "$cwd") || deny_hard "could not resolve the payload cwd"
while [ -n "$dir" ]; do
  if [ -d "$dir/.old-coder" ]; then
    artifact_root="$dir/.old-coder"
    break
  fi
  [ "$dir" = "/" ] && break
  dir=$(dirname -- "$dir")
done

# Two absences, deliberately distinguished. They mean different things to
# whoever reads the transcript: nobody started a task, versus somebody started
# one and the pointer step was skipped.
[ -n "$artifact_root" ] || deny "No \`.old-coder/\` artifact root at or above '$cwd', so no old-coder task is in progress and nothing is in scope. The spec reviewer reads the request and the SPEC, nothing else."

pointer="$artifact_root/scope"
[ -r "$pointer" ] || deny "The artifact root $artifact_root has no readable scope pointer, so this task's SPEC directory was never recorded. The SPEC step writes it when it creates the artifact directory."

# One line, one path. Anything richer would need a parser, and a parser inside
# a fail-closed handler is a second thing that can be wrong.
scope=$(sed -e 's/[[:space:]]*$//' "$pointer" 2>/dev/null | sed -e '/^$/d' | head -n 1)
[ -n "$scope" ] || deny "The scope pointer at $pointer is empty, so nothing is in scope."
[ -d "$scope" ] || deny "The scope pointer at $pointer names '$scope', which is not a directory."

# Resolve both sides before comparing. A prefix test on unresolved paths is
# defeated by `..` and by a symlink.
#
# Every component is resolved, the final one included. Resolving only the
# parent directory leaves a hole: a symlink sitting inside the spec directory
# and pointing at a source file passes the prefix test while reading the file
# the bound exists to hide. That hole was open in the first draft of this
# handler and is the reason this comment is here.
real_scope=$(readlink -f -- "$scope") && [ -n "$real_scope" ] \
  || deny_hard "could not resolve the scope pointer's target"
real_path=$(readlink -f -- "$path") && [ -n "$real_path" ] \
  || deny "'$path' does not resolve to a location this reviewer may read."

case "$real_path" in
  "$real_scope"/*) exit 0 ;;
  "$real_scope") exit 0 ;;
esac

deny "Read of '$path' is outside the spec directory. You are the spec-intent reviewer: the request and the SPEC are the whole world, and there is no implementation yet that can answer your question. Re-read the intent you were given instead."
