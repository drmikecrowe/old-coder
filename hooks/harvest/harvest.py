#!/usr/bin/env python3
"""Harvest every Bash command `old-coder-adversary` ran, from recorded sessions.

Step zero for track A2 object H3. The grammar in
`hooks/adversary-bash-grammar.py` is an allowlist, so it is only as good as the
evidence of what the reviewer actually does. Guessing produces a grammar that
matches the plan and denies the reviewer mid-review.

Where the evidence is. Claude Code writes one JSONL transcript per subagent run
under `<projects>/<project slug>/<session>/subagents/`, beside a `.meta.json`
naming the agent. Selecting on that metadata is what makes this a census rather
than a sample: it needs no guess about which prompt belongs to which reviewer,
and it finds runs spawned as teammates as well as ones spawned through the
Agent tool.

Output is one JSON object per call: the session file, the run's description,
and the command verbatim. `redact.py` rewrites home paths before the result is
committed; nothing else about a command is altered.

Usage: harvest.py <projects-root> <destination.jsonl>

On Claude Code the projects root is `~/.claude/projects`, or the `projects`
directory under `CLAUDE_CONFIG_DIR` where that is set.
"""

import json
import os
import sys
from collections import Counter

TARGET = "old-coder-adversary"


def sessions(root: str) -> list[tuple[str, str]]:
    """Every adversary transcript under `root`, as (path, description)."""
    found: list[tuple[str, str]] = []
    for dirpath, _dirs, files in os.walk(root):
        if os.path.basename(dirpath) != "subagents":
            continue
        for name in files:
            if not name.endswith(".meta.json"):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as handle:
                    meta = json.load(handle)
            except (OSError, ValueError):
                continue
            # Either key can carry the agent type: `agentType` when the run was
            # spawned directly, `customAgentType` when a named teammate wraps it.
            if TARGET not in (meta.get("agentType"), meta.get("customAgentType")):
                continue
            transcript = os.path.join(dirpath, name[: -len(".meta.json")] + ".jsonl")
            if os.path.exists(transcript):
                found.append((transcript, meta.get("description", "")))
    return found


def bash_calls(transcript: str, description: str) -> list[dict[str, str]]:
    """Every Bash tool_use block in one transcript, in order."""
    rows: list[dict[str, str]] = []
    with open(transcript, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            content = (record.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_use" or block.get("name") != "Bash":
                    continue
                rows.append(
                    {
                        "session": os.path.basename(transcript),
                        "desc": description,
                        "command": (block.get("input") or {}).get("command", ""),
                    }
                )
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    root, destination = argv[1], argv[2]
    if not os.path.isdir(root):
        print(f"FAIL: no projects root at {root}", file=sys.stderr)
        return 2
    found = sessions(root)
    if not found:
        # An empty harvest is a failure, not a clean run. A grammar written
        # against no evidence is the thing step zero exists to prevent.
        print(f"FAIL: no {TARGET} transcripts under {root}", file=sys.stderr)
        return 1
    rows = [row for transcript, desc in found for row in bash_calls(transcript, desc)]
    with open(destination, "w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row) + "\n")
    print(f"adversary sessions: {len(found)}")
    for transcript, description in sorted(found):
        print(f"  {os.path.basename(transcript)}  {description}")
    print(f"total Bash calls: {len(rows)}")
    heads: Counter[str] = Counter()
    for row in rows:
        words = row["command"].strip().split()
        heads[words[0] if words else "(empty)"] += 1
    for head, count in heads.most_common():
        print(f"{count:5d}  {head}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
