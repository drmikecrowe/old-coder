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

The lift requires a parsed `PreToolUse` entry whose matcher names the defeating
tool. Prose in the frontmatter does not earn it, a hook on a different tool
does not earn it, and a hook file that is absent or not executable does not
earn it either: `tools/hooks_registered.py` grades that half, and this sweep
would otherwise credit a bound whose handler was deleted. A check that any
agent can silence by mentioning hooks is not a check.

Fails closed. No agent frontmatter found, or no audit to read, is an error
rather than a pass: a sweep that reads nothing agrees with everything.

Usage: tools/audit_sweep.py [audit-file [agent-root]]

The optional arguments point the sweep at a copy of the audit, and at a tree of
fixture agents, instead of the committed ones. Negative controls need both:
the hook lift cannot be proven non-vacuous without an agent whose frontmatter
declares no hook. Nothing else should pass them.
"""

from __future__ import annotations

import re
import sys
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


def sweep(audit: Path, agents: dict[str, Agent]) -> list[str]:
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
                # The hooks tier: a PreToolUse hook matching every tool that
                # would defeat the bound takes those tools back. Anything less
                # leaves the row overclaimed, and the tools still holding the
                # hole are named so the reader knows which.
                unbounded = sorted(
                    tool for tool in held if not agents[agent].bounds(tool)
                )
                if not unbounded:
                    continue
                failures.append(
                    f"{audit.name}:{number}: {rule_id} reads `enforced` for a "
                    f"{label} bound while {agent} declares "
                    f"{agents[agent].tools} with no PreToolUse hook on "
                    f"{unbounded}"
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
    failures = sweep(audit, agents)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"audit sweep: {len(failures)} unsupported claim(s)", file=sys.stderr)
        return 1
    print(f"audit sweep clean ({len(agents)} agents, {audit.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
