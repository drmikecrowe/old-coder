#!/usr/bin/env python3
"""Check that `docs/loop-alignment.md` credits no bound its agents cannot hold.

An audit row that reports enforcement nothing enforces is the defect class this
repository exists to catch. Two failures, both mechanical:

  unattributed  a row asserts a capability bound ("read/inspect only", "must
                not reach the codebase") without naming the agent id it
                constrains, so no tool list can be checked against the claim
  overclaimed   a row reads `enforced` while the agent it names declares a tool
                that defeats the bound, and no hook takes that tool back

The hook clause is the A2 hooks tier, and it is narrow on purpose. A tool list
is not the only bound available on every host: a `PreToolUse` hook declared in
an agent's own frontmatter fires on that agent's tool calls and can deny them.
So an agent may hold `Read` and still be unable to reach the source tree.

The lift is narrow on three axes, and each one closes a way of earning it by
declaration rather than by behaviour. An adversarial round defeated an earlier
version with a `matcher: .*` and a handler that did nothing but `exit 0`,
silencing the sweep for VE-1 and EX-7, which are the two rows this repository
says a hook cannot close at all.

  exact       the matcher must NAME the tool. Per the hooks reference a matcher
              is match-all, an exact string or list, or an unanchored regex;
              only the exact form is a statement about a specific tool. `.*`
              fires for everything and therefore asserts nothing
  grammared   a shell tool is lifted ONLY by a handler this module names in
              ALLOWLIST_SHELL_HANDLERS, and only when the probe record also
              declares `grammar: allowlist`. See "The shell rule" below: this
              condition used to read "never", and A2 object H3 is the object
              the old rule said would change it
  probed      a recorded host probe must exist for the handler, AND it must
              name the handler's current sha256. Only a probe proves a hook
              denies; the CI half proves the wiring resolves. Requiring the
              hash is what stops a probe from outliving the code it graded:
              without it, editing the handler leaves yesterday's record
              standing and the row keeps reading `enforced` on the strength of
              a run against different code. "Rebind on every hook change" was
              prose until this check existed

Prose in the frontmatter does not earn it, and neither does a hook file that is
absent or not executable: `tools/hooks_registered.py` grades that half.

THE SHELL RULE, AND WHY IT CHANGED.

This module used to refuse every shell lift outright, with a note saying a
future object that bounds a shell by an allowlist grammar would change the rule
deliberately and say so. A2 object H3 is that object, and this is it saying so.

The old reason was sound and is not discarded: bounding a shell by deciding
whether an arbitrary string writes is undecidable, and a blocklist over shell
syntax is not a bound. An allowlist over a tiny grammar makes a different claim.
It never decides what a string does. It decides whether a string is one of a
small number of written-down shapes and refuses everything else, including every
string whose effect it cannot determine.

So the refusal moves from "a shell, ever" to "a shell, unless this module names
the handler". Four conditions, all required, and `lifted` enforces them.

**What ALLOWLIST_SHELL_HANDLERS proves, and what it does not.** This module
cannot read a handler and decide whether it is an allowlist rather than a
blocklist. Nothing short of executing it could, and a sweep that executes
handlers is a worse idea than the one it replaces. So the constant is a human
assertion, and `grammar: allowlist` in the probe record is the same assertion
made a second time somewhere else. Neither stops a contributor who means to
mislead: someone who edits this constant can assert anything.

What they do stop is an accident. A shell cannot be lifted by adding a hook
block, or by a permissive matcher, or by a handler that does nothing, because
none of those routes passes through this file. And the sha256 condition binds
both assertions to one version of the handler, so the two humans who wrote them
were looking at the same code.

Fails closed. No agent frontmatter found, or no audit to read, is an error
rather than a pass: a sweep that reads nothing agrees with everything.

Usage: tools/audit_sweep.py [audit-file [agent-root]]

The optional arguments point the sweep at a copy of the audit, and at a tree of
fixture agents, instead of the committed ones. Negative controls need both:
the hook lift cannot be proven non-vacuous without an agent whose frontmatter
declares no hook. Nothing else should pass them.
"""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_frontmatter import Agent, read_agents  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "docs" / "loop-alignment.md"
AGENT_GLOB = "skills/*/agents/*.md"

# A tool that can write, and a tool that can read the source tree. Bash is in
# both: it is a general-purpose shell, which is the whole point of VE-1.
SHELL = frozenset({"Bash", "Shell", "Terminal", "Execute", "PowerShell"})
READER = SHELL | frozenset({"Read", "Grep", "Glob"})

# Handlers this repository asserts are allowlist grammars over a shell. See
# "The shell rule" above for what the assertion is worth and what it is not.
#
# ONE ENTRY IS THE DESIGN, not a coincidence of there being one hook so far.
# This is not a mechanism for lifting shells in general: a second entry is a
# second object, with its own grammar, its own controls and its own host probe.
ALLOWLIST_SHELL_HANDLERS = frozenset({"adversary-bash-grammar"})

# A shell lift needs the probe record to declare the grammar's shape as well as
# the handler's hash. Same fixed form as the hash line, same reason: a record
# that merely mentions the word somewhere in its prose has not declared
# anything.
GRAMMAR_DECLARED = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?grammar:[ \t]*allowlist[ \t]*$",
    re.MULTILINE,
)

# A handler may be a shell script or a Python program. The grammar handler is
# Python because its core is quote-aware tokenization, and hand-writing that
# lexer in POSIX sh would put a second thing that can be wrong inside a
# fail-closed handler.
HANDLER_SUFFIXES = (".sh", ".py")

# Each bound, the tools that defeat it, and the prose that asserts it.
BOUNDS: tuple[tuple[str, frozenset[str], re.Pattern[str]], ...] = (
    (
        "read-only",
        SHELL,
        re.compile(
            r"read[-/ ]?(?:only|inspect)|no write|cannot write"
            r"|holds no write|write path",
            re.IGNORECASE,
        ),
    ),
    (
        "no-codebase",
        READER,
        re.compile(
            r"must not reach|cannot reach|no codebase access"
            r"|not reach the codebase|no source access",
            re.IGNORECASE,
        ),
    ),
)

def row_fields(line: str) -> tuple[str, str] | None:
    """Return a table row's rule id and status, or None if it is not one."""
    if not line.startswith("|"):
        return None
    cells = line.split("|")
    if len(cells) < 5:
        return None
    return cells[1].strip(), cells[3].strip()


# The hash must be DECLARED on its own line, in one fixed form. An earlier
# version searched for "sha256" followed by any 64 hex characters within a
# short window, which meant a superseded record that merely MENTIONED the
# current hash counted as having graded it. "sha256 is now <current>" in a
# record whose graded hash was something else lifted the row.
#
# A record that declares more than one distinct hash is ambiguous about what it
# graded, so it contributes nothing rather than contributing all of them.
# An optional list marker is allowed, because every other field in a probe
# record's metadata block is a bullet and the hash belongs with them. It does
# not loosen the attribution: the line must still consist of the key and one
# hash and nothing else.
SHA_DECLARED = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?handler sha256:[ \t]*([0-9a-fA-F]{64})[ \t]*$",
    re.MULTILINE,
)


def handler_sha256(path: Path) -> str:
    """The handler's content hash, or "" when it cannot be read."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


@dataclass(frozen=True)
class Probe:
    """What one probe record declares about the handler it graded."""

    hashes: frozenset[str]
    # True only when the record declares `grammar: allowlist` on its own line.
    # Required for a shell lift and ignored for every other tool.
    allowlist: bool


def handler_path(root: Path, stem: str) -> Path | None:
    """The handler file for `stem`, or None when no candidate exists."""
    for suffix in HANDLER_SUFFIXES:
        candidate = root / "hooks" / f"{stem}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def recorded_probes(root: Path) -> dict[str, Probe]:
    """Handler stem to what its probe records declare.

    A probe file is `hooks/probes/<handler stem>-<anything>.md` and must declare
    the handler it graded on a line reading `handler sha256: <64 hex>`. A record
    that declares no hash contributes nothing: it cannot be matched to any
    version of the code, so it cannot be evidence about one. A record declaring
    two different hashes contributes nothing either, for the same reason.
    """
    hashes: dict[str, set[str]] = {}
    allowlist: dict[str, bool] = {}
    for path in (root / "hooks" / "probes").glob("*.md"):
        if path.name in ("README.md", "RUNBOOK.md"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        declared = {match.group(1).lower() for match in SHA_DECLARED.finditer(text)}
        if len(declared) > 1:
            # Ambiguous: it cannot be said which handler this record graded.
            declared = set()
        hashes.setdefault(path.stem, set()).update(declared)
        # A record that declares no usable hash declares nothing at all, the
        # grammar line included. Otherwise an ambiguous record could still
        # carry the shell assertion for a sibling record's hash.
        if declared and GRAMMAR_DECLARED.search(text):
            allowlist[path.stem] = True
    return {
        stem: Probe(frozenset(found), allowlist.get(stem, False))
        for stem, found in hashes.items()
    }


def lifted(agent: Agent, tool: str, probes: dict[str, Probe], root: Path) -> bool:
    """Whether a hook genuinely takes `tool` back from this agent."""
    for hook in agent.names_exactly(tool):
        if not hook.command:
            continue
        stem = Path(hook.command.split()[0]).stem
        # A shell is lifted only by a handler this module names. The tool list
        # is not the bound here; the grammar is, and this repository has to
        # have looked at that grammar for the lift to be available at all.
        if tool in SHELL and stem not in ALLOWLIST_SHELL_HANDLERS:
            continue
        path = handler_path(root, stem)
        if path is None:
            continue
        current = handler_sha256(path)
        if not current:
            continue
        for recorded_stem, probe in probes.items():
            if recorded_stem != stem and not recorded_stem.startswith(f"{stem}-"):
                continue
            if current not in probe.hashes:
                continue
            # The record must make the shell assertion too. One human editing
            # ALLOWLIST_SHELL_HANDLERS is not two humans agreeing, and the
            # record is where the person who ran the probe says what they
            # believed they were probing.
            if tool in SHELL and not probe.allowlist:
                continue
            return True
    return False


def sweep(
    audit: Path, agents: dict[str, Agent], probes: dict[str, Probe], root: Path
) -> list[str]:
    """Report every row that credits a bound its named agent cannot hold."""
    failures: list[str] = []
    for number, line in enumerate(audit.read_text(encoding="utf-8").splitlines(), 1):
        fields = row_fields(line)
        if fields is None:
            continue
        rule_id, status = fields
        named = [agent for agent in agents if agent in line]
        for label, defeated_by, pattern in BOUNDS:
            if pattern.search(line) is None:
                continue
            if not named:
                failures.append(
                    f"{audit.name}:{number}: {rule_id} asserts a {label} bound "
                    f"and names no agent id"
                )
                continue
            if status != "enforced":
                continue
            for agent in named:
                held = defeated_by & set(agents[agent].tools)
                if not held:
                    continue
                unbounded = sorted(
                    tool for tool in held if not lifted(agents[agent], tool, probes, root)
                )
                if not unbounded:
                    continue
                failures.append(
                    f"{audit.name}:{number}: {rule_id} reads `enforced` for a "
                    f"{label} bound while {agent} declares "
                    f"{agents[agent].tools} with no probed, exact PreToolUse "
                    f"hook on {unbounded} whose recorded probe names the handler's "
                    f"current sha256"
                )
    return failures


def main(argv: list[str]) -> int:
    audit = Path(argv[1]).resolve() if len(argv) > 1 else AUDIT
    if not audit.is_file():
        raise SystemExit(f"FAIL: no audit to sweep at {audit}")
    root = Path(argv[2]).resolve() if len(argv) > 2 else ROOT
    agents = read_agents(root, AGENT_GLOB)
    if not agents:
        raise SystemExit(f"FAIL: no agent frontmatter under {root / AGENT_GLOB}")
    failures = sweep(audit, agents, recorded_probes(root), root)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"audit sweep: {len(failures)} unsupported claim(s)", file=sys.stderr)
        return 1
    print(f"audit sweep clean ({len(agents)} agents, {audit.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
