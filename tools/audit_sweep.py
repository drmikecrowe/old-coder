#!/usr/bin/env python3
"""Check that `docs/loop-alignment.md` credits no bound its agents cannot hold.

An audit row that reports enforcement nothing enforces is the defect class this
repository exists to catch. Two failures, both mechanical:

  unattributed  a row asserts a capability bound ("read/inspect only", "must
                not reach the codebase") without naming the agent id it
                constrains, so no tool list can be checked against the claim
  overclaimed   a row reads `enforced` while the agent it names declares a tool
                that defeats the bound

Fails closed. No agent frontmatter found, or no audit to read, is an error
rather than a pass: a sweep that reads nothing agrees with everything.

Usage: tools/audit_sweep.py [audit-file]

The optional argument points the sweep at a copy of the audit instead of the
committed one. Negative controls need it; nothing else should pass it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

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

NAME = re.compile(r"^name:\s*(\S+)$", re.MULTILINE)
TOOLS = re.compile(r"^tools:\s*(.+)$", re.MULTILINE)


def read_agents(root: Path) -> dict[str, list[str]]:
    """Map every bundled agent's id to the tool list its frontmatter declares.

    An agent with no `tools:` key inherits every tool available to subagents,
    so the absent key is recorded as exactly that rather than as an empty list.
    """
    agents: dict[str, list[str]] = {}
    for path in sorted(root.glob(AGENT_GLOB)):
        parts = path.read_text(encoding="utf-8").split("---")
        if len(parts) < 3:
            raise SystemExit(f"FAIL: {path} has no frontmatter block")
        front = parts[1]
        name_match = NAME.search(front)
        if name_match is None:
            raise SystemExit(f"FAIL: {path} frontmatter declares no name")
        tools_match = TOOLS.search(front)
        if tools_match is None:
            agents[name_match.group(1)] = ["<key absent: inherits all>"]
        else:
            agents[name_match.group(1)] = [
                tool.strip() for tool in tools_match.group(1).split(",")
            ]
    return agents


def row_fields(line: str) -> tuple[str, str] | None:
    """Return a table row's rule id and status, or None if it is not one."""
    if not line.startswith("|"):
        return None
    cells = line.split("|")
    if len(cells) < 5:
        return None
    return cells[1].strip(), cells[3].strip()


def sweep(audit: Path, agents: dict[str, list[str]]) -> list[str]:
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
            failures.extend(
                f"{audit.name}:{number}: {rule_id} reads `enforced` for a "
                f"{label} bound while {agent} declares {agents[agent]}"
                for agent in named
                if defeated_by & set(agents[agent]) and status == "enforced"
            )
    return failures


def main(argv: list[str]) -> int:
    audit = Path(argv[1]).resolve() if len(argv) > 1 else AUDIT
    if not audit.is_file():
        raise SystemExit(f"FAIL: no audit to sweep at {audit}")
    agents = read_agents(ROOT)
    if not agents:
        raise SystemExit(f"FAIL: no agent frontmatter under {ROOT / AGENT_GLOB}")
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
