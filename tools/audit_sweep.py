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
  not a shell  a hook never lifts a shell tool. Bounding one means deciding
              whether an arbitrary shell string writes, and `ceiling.md` says
              plainly that a blocklist over shell syntax is not a bound. If a
              future object bounds a shell by an allowlist grammar, it changes
              this rule deliberately and says so
  probed      a recorded host probe must exist for the handler. Only a probe
              proves a hook denies; the CI half proves the wiring resolves.
              This is the rule that stops a no-op handler from lifting anything

Prose in the frontmatter does not earn it, and neither does a hook file that is
absent or not executable: `tools/hooks_registered.py` grades that half.

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


def recorded_probes(root: Path) -> set[str]:
    """Handler stems that have a recorded host probe.

    A probe file is `hooks/probes/<handler stem>-<anything>.md`. The stem is the
    handler's filename without its extension, so `spec-intent-scope.sh` is
    proven by `hooks/probes/spec-intent-scope-<tree hash>.md`.
    """
    stems: set[str] = set()
    for path in (root / "hooks" / "probes").glob("*.md"):
        if path.name in ("README.md", "RUNBOOK.md"):
            continue
        stems.add(path.stem)
    return stems


def lifted(agent: Agent, tool: str, probes: set[str]) -> bool:
    """Whether a hook genuinely takes `tool` back from this agent."""
    if tool in SHELL:
        return False
    for hook in agent.names_exactly(tool):
        stem = Path(hook.command.split()[0]).stem if hook.command else ""
        if any(probe == stem or probe.startswith(f"{stem}-") for probe in probes):
            return True
    return False


def sweep(audit: Path, agents: dict[str, Agent], probes: set[str]) -> list[str]:
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
                    tool for tool in held if not lifted(agents[agent], tool, probes)
                )
                if not unbounded:
                    continue
                failures.append(
                    f"{audit.name}:{number}: {rule_id} reads `enforced` for a "
                    f"{label} bound while {agent} declares "
                    f"{agents[agent].tools} with no probed, exact PreToolUse "
                    f"hook on {unbounded}"
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
    failures = sweep(audit, agents, recorded_probes(root))
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"audit sweep: {len(failures)} unsupported claim(s)", file=sys.stderr)
        return 1
    print(f"audit sweep clean ({len(agents)} agents, {audit.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
