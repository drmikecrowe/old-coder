#!/usr/bin/env python3
"""PreToolUse handler for old-coder-adversary: bound `Bash` to a read grammar.

VE-1, EX-5 and EX-7 in docs/loop-alignment.md are one gap seen from three
rules. The reviewer declares `Read, Bash, Grep, Glob`, and `Bash` is a general
write path: `sed -i`, `git checkout`, `git commit`, `git push`. Its brief says
"reach for `Bash` only for git". That is an instruction, and EX-1 in the same
audit says scope is absent capability, not instruction. This makes it a bound,
on the one host that has the mechanism.

WHY AN ALLOWLIST IS NOT THE THING THE CEILING RULED OUT.
`references/ceiling.md` says bounding this shell would mean deciding whether an
arbitrary shell string writes, and that a blocklist over shell syntax is not a
bound. Both sentences are correct and neither is what happens here. This
handler never decides what a string does. It decides whether a string is one of
a small number of shapes, and refuses everything else, including every string
whose effect it cannot determine. "Does this write" is undecidable in general.
"Is this `git diff` with plain arguments" is a pattern match.

THE GRAMMAR IS MEASURED, NOT IMAGINED.
`hooks/harvest/` holds every Bash command this reviewer ran across eight
recorded sessions, 57 of them, and `hooks/harvest/expected.tsv` says which the
grammar must admit. 44 pass. The 13 denials are 7 `python3`, 4 commands using
shell variables, 1 wrapper, and no accidents. An allowlist written from
imagination denies legitimate reads mid-review, which is the right failure and
a disruptive one to meet in production. docs/spec-a2-h3.md argues the shape
from those rows; the object's original sketch, git only with no metacharacter,
would have admitted 8 of 57.

WHAT THIS DOES NOT BOUND, stated because a bound that hides its edge is worse
than no bound.

**Read reach.** The reviewer may still read any file the host lets it read.
VE-1, EX-5 and EX-7 are about write capability; read scoping is EX-1's shape and
a different object.

**Code reached through git's own configuration.** `git diff` honours
`diff.external` and the textconv filters named by `.gitattributes`, both of
which are read from the repository being examined. A repository that configures
either runs that program when the reviewer diffs it, and the string this handler
judges says only `git diff`. The grammar cannot see it, because the code is not
in the command.

That matters here specifically: this reviewer exists to read repositories
somebody else wrote, so that configuration is attacker-controlled in the general
case. `-c` and `--exec-path` are refused below, which closes the spelling where
the command carries the configuration. It does not close the spelling where the
repository carries it. Closing that needs `-c core.attributesFile=/dev/null
-c diff.external=` and friends forced on every git invocation, which is a
handler that rewrites tool calls rather than one that decides about them, and
`hooks/README.md` clause 1 puts rewriting outside this directory. So it is
recorded as a limit rather than papered over, and it is unchanged from the
situation before this hook existed.

Contract, from the Claude Code hooks reference:
  deny  = print the hookSpecificOutput JSON and exit 0. The reason is shown to
          the reviewer, so it explains rather than just refuses.
  allow = print nothing and exit 0. That is "no decision"; the normal
          permission flow continues. This handler never returns "allow",
          because an explicit allow would skip permission rules the user set.
  fail  = exit 2. On PreToolUse that is a blocking error, and stderr becomes
          the reason. Every unexpected path lands here.

What it cannot do: if this file is missing, unreadable, or not executable,
Claude Code logs the failure and carries on. A hook can fail closed on its
inputs. It cannot fail closed on its own absence. tools/hooks_registered.py is
the CI half that catches deletion, and it is not a substitute for the host
probes in hooks/README.md.
"""

import json
import re
import shlex
import sys
from typing import NoReturn

# The four operators the grammar composes with. A sequence of reads is a read,
# which is the whole argument for admitting them, and each segment is checked
# on its own so `git diff && rm -rf x` dies on the second one.
#
# `;` is here on evidence. 22 of the 57 harvested commands use it, every one to
# read two things in a row. Excluding it as a syntax class would have denied
# more real work than every other exclusion combined.
OPERATORS = frozenset({";", "&&", "||", "|"})

# Characters that only ever appear in an operator token. A token made up
# entirely of these and not in OPERATORS is a redirect, a subshell or a
# background operator.
OPERATOR_CHARS = frozenset("<>()&;|")

# The only redirect forms in the grammar, as literal spellings, removed before
# tokenizing. `/dev/null` is a fixed sink and `2>&1` is a descriptor dup:
# neither can reach a file the allowlist did not approve. 16 of the 57
# harvested commands discard stderr this way. Every other use of `>` or `<`
# denies, `>>` included.
STDERR_ONLY = re.compile(r"(?:\d?>\s*/dev/null|2>&1)")

# git subcommands that read. Deliberately short: it is the observed set plus
# the neighbours that cannot write. Adding one is a decision, not a convenience.
GIT_READ = frozenset({
    "diff", "show", "log", "status", "blame", "cat-file",
    "ls-files", "ls-tree", "rev-parse", "describe", "shortlog",
})

# `git -c` sets configuration for one command, and `core.pager` or an alias
# turns that into "run this program". `--exec-path` moves where git looks for
# its own subcommands. Both reach a command, from inside a subcommand that
# reads.
GIT_ESCAPES = frozenset({"-c", "--exec-path"})

# sed writes with `w file` and `s///w file`, so a general script is a write
# path. The grammar takes line-range printing and nothing else, which is the
# whole of the observed use.
SED_SCRIPT = re.compile(r"^\d+(?:,\d+)?p(?:;\d+(?:,\d+)?p)*$")

# find executes with -exec, -execdir and -ok, and writes with -delete,
# -fprintf, -fprint and -fls. An allowlist of predicates is the only safe shape.
FIND_PREDICATES = frozenset({
    "-name", "-iname", "-type", "-maxdepth", "-mindepth", "-path", "-ipath",
    "-o", "-a", "-not", "-prune", "-print",
})

# Commands whose every flag reads. No allowlist of arguments, because none of
# their flags reach a file for writing or a program for running.
PLAIN_READERS = frozenset({
    "cat", "head", "ls", "wc", "file", "sha256sum", "md5sum", "stat", "echo",
    "basename", "dirname", "true", "pwd", "date",
})


def fail_closed(reason: str) -> NoReturn:
    """Exit 2, which on PreToolUse is a blocking error.

    Any exit that is not an explicit decision must land here. An ordinary
    nonzero exit is a NON-blocking error and the tool call proceeds, which is
    the fail-open this whole tier exists to prevent.
    """
    print(f"adversary-bash-grammar: {reason}; denying Bash", file=sys.stderr)
    raise SystemExit(2)


def deny(reason: str) -> NoReturn:
    """Print the denial decision and exit 0."""
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    raise SystemExit(0)


def check_segment(words: list[str]) -> str | None:
    """The reason this segment is outside the grammar, or None if it is inside.

    Deny by default: every arm that returns None is a shape written down here,
    and the function ends in a refusal.
    """
    if not words:
        return "an empty command between two operators"
    head, args = words[0], words[1:]

    if head == "/usr/bin/git":
        head = "git"

    if head == "cd":
        if len(args) != 1:
            return "`cd` takes exactly one plain argument in this grammar"
        return None

    if head == "git":
        index = 0
        while index < len(args):
            if args[index] == "-C" and index + 1 < len(args):
                index += 2
                continue
            if args[index] == "--no-pager":
                index += 1
                continue
            break
        if index >= len(args):
            return "`git` with no subcommand"
        subcommand = args[index]
        if subcommand not in GIT_READ:
            return (
                f"`git {subcommand}` is not a read subcommand. The grammar "
                f"allows: {' '.join(sorted(GIT_READ))}"
            )
        for argument in args:
            if argument in GIT_ESCAPES or argument.startswith("--exec-path"):
                return f"`git {argument}` can run a command"
            if argument.startswith("--output"):
                return f"`{argument}` writes a file"
        return None

    if head in ("rg", "grep"):
        for argument in args:
            if argument.startswith("--pre") or argument in ("-f", "--file"):
                return f"`{head} {argument}` runs or reads a program"
        return None

    if head == "sed":
        script_seen = False
        for argument in args:
            if argument == "-n":
                continue
            if argument.startswith("-"):
                return (
                    f"`sed {argument}` is not in the grammar, which takes `-n` "
                    f"and a line-range print and nothing else"
                )
            if not script_seen:
                if not SED_SCRIPT.match(argument):
                    return (
                        f"`{argument}` is not a line-range print. A general sed "
                        f"script writes with `w`, so the grammar takes only "
                        f"forms like '1,40p' or '10,20p;90,99p'"
                    )
                script_seen = True
        if not script_seen:
            return "`sed` with no line-range print script"
        return None

    if head == "find":
        for argument in args:
            if argument.startswith("-") and argument not in FIND_PREDICATES:
                return (
                    f"`find {argument}` is not in the grammar. `-exec`, `-ok` "
                    f"and `-delete` run or write, so predicates are an allowlist"
                )
        return None

    if head == "tail":
        for argument in args:
            if argument == "-f" or argument.startswith("--follow"):
                return "`tail -f` never terminates"
        return None

    if head in PLAIN_READERS:
        return None

    return (
        f"`{head}` is not in the read grammar. This reviewer's shell is bounded "
        f"to reading: git read subcommands, rg, grep, sed -n, find, and plain "
        f"readers. Anything that can run a program or write a file is refused, "
        f"`python3` and `sh` included."
    )


def check(command: str) -> str | None:
    """The reason this command is outside the grammar, or None if inside."""
    if not command.strip():
        return "an empty command"
    if "\n" in command:
        return (
            "the grammar is one line. A multiline command is almost always a "
            "program being fed to an interpreter"
        )

    # Remove the two permitted stderr forms first, so the checks below can
    # treat every remaining `>` or `<` as a redirect to refuse.
    stripped = STDERR_ONLY.sub(" ", command)

    try:
        lexer = shlex.shlex(stripped, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError as error:
        # An unbalanced quote. The shell would read this differently from any
        # reading available here, so there is nothing to be confident about.
        return f"could not tokenize the command ({error})"

    segments: list[list[str]] = [[]]
    for token in tokens:
        if token in OPERATORS:
            segments.append([])
            continue
        # Quotes are consumed by the lexer, so a quoted `|` arrives as part of
        # a word and a bare `|` arrives as its own token. That is how the shell
        # reads them too, and it is why `rg -n "a|b"` is one read rather than a
        # pipe. Only a token made entirely of operator characters is an
        # operator.
        if token and not (set(token) - OPERATOR_CHARS):
            return (
                f"`{token}` is a redirect, subshell or background operator. The "
                f"grammar composes with `;`, `&&`, `||` and `|` only"
            )
        if "$" in token:
            return (
                f"`{token}` carries a `$`. Command substitution and parameter "
                f"expansion both reach text this grammar cannot see"
            )
        if "`" in token:
            return f"`{token}` carries a backtick substitution"
        segments[-1].append(token)

    # A trailing separator is punctuation, not a command. `ls /tmp ;` is an
    # ordinary thing to type and there is nothing after the `;` to run, so
    # refusing it would be a denial with no security value. Only the LAST
    # segment may be empty: `; ls` and `ls ;; wc` still deny, because in both
    # the gap sits between two things and the parse is not one this handler
    # should be confident about.
    if segments and not segments[-1]:
        segments.pop()
    if not segments:
        return "no command"

    for segment in segments:
        reason = check_segment(segment)
        if reason is not None:
            return reason
    return None


def main() -> None:
    try:
        raw = sys.stdin.read()
    except OSError:
        fail_closed("could not read the hook payload from stdin")

    # Empty stdin is not "no decision to make". Without this the tool name
    # reads empty, the Bash guard below declines, and the call proceeds.
    if not raw.strip():
        fail_closed("the hook payload was empty")

    try:
        payload = json.loads(raw)
    except ValueError:
        fail_closed("the hook payload is not valid JSON")

    if not isinstance(payload, dict):
        fail_closed("the hook payload is not a JSON object")

    tool = payload.get("tool_name")
    if not isinstance(tool, str) or not tool:
        fail_closed("the hook payload carried no tool_name")

    # Only Bash is in scope. Anything else gets no decision from this handler,
    # so it never fights the Read bound EX-1's hook holds.
    if tool != "Bash":
        raise SystemExit(0)

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        fail_closed("the Bash payload carried no readable tool_input")

    command = tool_input.get("command")
    if not isinstance(command, str):
        fail_closed("the Bash payload's command is not a string")

    reason = check(command)
    if reason is not None:
        deny(
            f"This Bash call is outside the reviewer's read grammar: {reason}. "
            f"You review a change; you never repair it. Use `git diff`, `rg`, "
            f"`sed -n` and the plain readers. If you cannot verify something "
            f"within the grammar, report it unproven rather than working "
            f"around the bound."
        )
    raise SystemExit(0)


if __name__ == "__main__":
    main()
