#!/usr/bin/env python3
"""Check that every hook an agent frontmatter names exists and can run.

This is the CI half of the hooks tier's control, and it is written down here
as half so that nobody reads it as the proof.

**What it catches.** A frontmatter that points at a handler which was renamed,
deleted, or never made executable. Claude Code does not deny in that case: it
logs the failure and the normal permission flow continues, which is the same as
no hook at all. That failure is silent from inside the run, so it needs a check
outside the run.

**What it does not catch, and never will.** Whether Claude Code actually calls
the handler. Only a recorded host probe closes that, and `hooks/README.md`
carries the procedure. A green run here means the wiring is present, not that
the bound holds.

`tools/audit_sweep.py` credits a `PreToolUse` hook when it lifts an audit row
to `enforced`. This check is what stops that credit from outliving the file it
depends on.

Fails closed: a hook whose command cannot be resolved to a readable, executable
file is a failure, not a skip.

Usage: tools/hooks_registered.py [agent-root]
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_frontmatter import read_agents  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AGENT_GLOB = "skills/*/agents/*.md"

# `${NAME:-fallback}` and `${NAME}` and `$NAME`, which is the whole of what a
# hook command path is allowed to interpolate here. Anything else is reported
# rather than guessed at: a path this cannot resolve is a path this cannot
# vouch for.
PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def expand(command: str, root: Path) -> str:
    """Resolve the placeholders a hook command may use, fallbacks included."""

    def one(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(3)
        default = match.group(2) or ""
        if name == "CLAUDE_PROJECT_DIR":
            return os.environ.get(name, str(root))
        value = os.environ.get(name, "")
        if value:
            return value
        # Recurse so `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` resolves its own
        # fallback rather than being reported as an unresolved path.
        return PLACEHOLDER.sub(one, default) if default else ""

    return PLACEHOLDER.sub(one, command)


def check(root: Path) -> list[str]:
    """Report every frontmatter hook that would not run."""
    failures: list[str] = []
    agents = read_agents(root, AGENT_GLOB)
    if not agents:
        raise SystemExit(f"FAIL: no agent frontmatter under {root / AGENT_GLOB}")

    for name, agent in sorted(agents.items()):
        for hook in agent.pre_tool_use:
            where = f"{agent.path.name}: {name} PreToolUse[{hook.matcher}]"
            if not hook.command:
                failures.append(f"{where} declares an empty command")
                continue
            resolved = expand(hook.command, root)
            if "$" in resolved:
                failures.append(
                    f"{where} command has an unresolved placeholder: {resolved}"
                )
                continue
            path = Path(resolved.split()[0])
            if not path.exists():
                failures.append(f"{where} points at {path}, which does not exist")
                continue
            if not path.is_file():
                failures.append(f"{where} points at {path}, which is not a file")
                continue
            if not os.access(path, os.X_OK):
                failures.append(f"{where} points at {path}, which is not executable")
    return failures


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else ROOT
    failures = check(root)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"hooks registered: {len(failures)} unusable hook(s)", file=sys.stderr)
        return 1
    agents = read_agents(root, AGENT_GLOB)
    total = sum(len(agent.pre_tool_use) for agent in agents.values())
    print(
        f"hooks registered: {total} hook(s) across {len(agents)} agents resolve "
        f"and are executable (this does not prove the host calls them)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
