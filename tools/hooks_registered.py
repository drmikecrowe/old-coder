#!/usr/bin/env python3
"""Check that every hook an agent frontmatter names exists and can run.

This is the CI half of the hooks tier's control, and it is written down here
as half so that nobody reads it as the proof.

**What it catches.** A frontmatter that points at a handler which was renamed,
deleted, or never made executable. Claude Code does not deny in that case: it
logs the failure and the normal permission flow continues, which is the same as
no hook at all. That failure is silent from inside the run, so it needs a check
outside the run.

**It grades the repository's copy, and reports the install as a note.** The
handler in `hooks/` is the source of truth and every clone has it, so a missing
or non-executable file there is a failure. Whether it is installed into the
config directory is host-specific and opt-in, and CI never installs it, so that
is a note. Making it a failure would redden this repository's own CI on every
push and turn the layer into something people learn to ignore.

The note is not decoration. **An uninstalled handler is the single most common
reason a hook does nothing**, and nothing else in this tier reports it: the
handler's own controls pass, the frontmatter is correct, and the tool call
proceeds anyway. So the note prints the exact two commands that fix it.

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


def handler_path(root: Path, command: str) -> Path:
    """The tier-local handler a hook command names, by basename.

    Deliberately basename-only. The frontmatter path is host-specific by
    design; what must exist in every clone is the file in `hooks/`.
    """
    return root / "hooks" / Path(command.split()[0]).name


def check(root: Path) -> tuple[list[str], list[str]]:
    """Return (failures, notes) for every frontmatter hook."""
    failures: list[str] = []
    notes: list[str] = []
    agents = read_agents(root, AGENT_GLOB)
    if not agents:
        raise SystemExit(f"FAIL: no agent frontmatter under {root / AGENT_GLOB}")

    for name, agent in sorted(agents.items()):
        for hook in agent.pre_tool_use:
            where = f"{agent.path.name}: {name} PreToolUse[{hook.matcher}]"
            if not hook.command:
                failures.append(f"{where} declares an empty command")
                continue

            handler = handler_path(root, hook.command)
            if not handler.exists():
                failures.append(
                    f"{where} names {handler.name}, which is not in hooks/. "
                    f"A hook in this tier lives in hooks/ and is graded there"
                )
                continue
            if not handler.is_file():
                failures.append(f"{where} points at {handler}, which is not a file")
                continue
            if not os.access(handler, os.X_OK):
                failures.append(f"{where} points at {handler}, which is not executable")
                continue

            # The install is a note, never a failure. The tier is opt-in and
            # CI does not install it, so a host that has not installed is a
            # reader's choice rather than a defect. It is still the single
            # most common reason a hook does nothing, so the note says exactly
            # how to fix it rather than merely reporting the state.
            resolved = expand(hook.command, root)
            deployed = Path(resolved.split()[0]) if "$" not in resolved else None
            if deployed is not None and deployed.exists():
                notes.append(f"{where} is installed at {deployed}")
            elif deployed is not None:
                notes.append(
                    f"{where} is NOT installed. The handler exists at "
                    f"{handler} but nothing is at {deployed}, so the hook will "
                    f"not run and the tool call will proceed. Install it with:"
                    f"\n    mkdir -p {deployed.parent}"
                    f"\n    ln -s {handler} {deployed}"
                )
            else:
                notes.append(
                    f"{where} address does not resolve in this environment "
                    f"({resolved}), so whether it is installed cannot be said "
                    f"from here"
                )
    return failures, notes


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else ROOT
    failures, notes = check(root)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(f"hooks registered: {len(failures)} unusable hook(s)", file=sys.stderr)
        return 1
    agents = read_agents(root, AGENT_GLOB)
    total = sum(len(agent.pre_tool_use) for agent in agents.values())
    for note in notes:
        print(f"note: {note}")
    print(
        f"hooks registered: {total} handler(s) across {len(agents)} agents are "
        f"present and executable in hooks/ (this does not prove the host calls "
        f"them)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
