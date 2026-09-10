#!/usr/bin/env python3
"""Read the bundled agents' frontmatter: tool lists and PreToolUse hooks.

Two checks need the same three facts about each agent, so they read them
through here rather than each growing a parser:

  tools/audit_sweep.py        does a hook take back a tool the audit says is
                              bounded
  tools/hooks_registered.py   does every hook a frontmatter names exist and run

**This is not a YAML parser and must not grow into one.** It reads exactly the
shape `CONTRIBUTING.md`'s hooks tier permits, which is the shape the Claude
Code hooks reference documents:

    hooks:
      PreToolUse:
        - matcher: Read
          hooks:
            - type: command
              command: "<path>"

Anything else in the block is ignored rather than guessed at. A frontmatter
that declares hooks in a shape this cannot read reports no hooks, which costs
the agent its lift in the sweep and fails the registration check. That is the
fail-closed direction: an unreadable bound is not credited.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

NAME = re.compile(r"^name:\s*(\S+)$", re.MULTILINE)
TOOLS = re.compile(r"^tools:\s*(.+)$", re.MULTILINE)

TOOLS_ABSENT = "<key absent: inherits all>"


# Matcher semantics, from the Claude Code hooks reference. Three cases, and the
# difference between them is the whole of finding 1 from H2's adversarial round:
#
#   "*", "" or omitted        match every tool
#   only [A-Za-z0-9_- ,|]     exact string, or a list separated by `|` or `,`
#   anything else             an UNANCHORED JavaScript regular expression, so
#                             `Edit.*` fires for `NotebookEdit` and `.*` fires
#                             for everything
#
# Reproducing this faithfully matters because a caller may need to know not just
# whether a matcher fires for a tool, but whether it names that tool exactly.
EXACT_CHARS = re.compile(r"^[A-Za-z0-9_\- ,|]+$")


@dataclass(frozen=True)
class Hook:
    """One `PreToolUse` entry: the tools it matches and the command it runs."""

    matcher: str
    command: str

    @property
    def kind(self) -> str:
        """`all`, `exact` or `regex`, per the reference's three cases."""
        if self.matcher in ("", "*"):
            return "all"
        return "exact" if EXACT_CHARS.match(self.matcher) else "regex"

    def names_exactly(self, tool: str) -> bool:
        """Whether this matcher names `tool` as one of its exact strings.

        Deliberately false for `all` and for every regex matcher, including one
        that happens to fire for the tool. A matcher that fires for everything
        is not a statement about anything, and a bound credited from it is
        credited from a declaration rather than from a decision.
        """
        if self.kind != "exact":
            return False
        return tool in {part.strip() for part in re.split(r"[|,]", self.matcher)}

    def matches(self, tool: str) -> bool:
        """Whether this entry fires for `tool`, as the host would decide it."""
        kind = self.kind
        if kind == "all":
            return True
        if kind == "exact":
            return self.names_exactly(tool)
        try:
            # Unanchored, matching the reference's RegExp.prototype.test.
            return re.search(self.matcher, tool) is not None
        except re.error:
            # A matcher the host would accept and this cannot compile fires for
            # nothing here. Under-crediting a bound is the safe direction.
            return False


@dataclass(frozen=True)
class Agent:
    path: Path
    name: str
    tools: list[str]
    pre_tool_use: list[Hook] = field(default_factory=list)

    def bounds(self, tool: str) -> bool:
        """Whether a declared hook fires on `tool` for this agent."""
        return any(hook.matches(tool) for hook in self.pre_tool_use)

    def names_exactly(self, tool: str) -> list[Hook]:
        """Every declared hook whose matcher names `tool` exactly."""
        return [hook for hook in self.pre_tool_use if hook.names_exactly(tool)]


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_pre_tool_use(front: str) -> list[Hook]:
    """Pull every PreToolUse matcher/command pair out of a frontmatter block."""
    lines = front.splitlines()
    hooks: list[Hook] = []

    inside_hooks = False
    inside_event = False
    matcher = ""
    hooks_root_indent = 0

    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = _indent(line)
        stripped = line.strip()

        if re.fullmatch(r"hooks:\s*", stripped) and indent == 0:
            inside_hooks, inside_event, hooks_root_indent = True, False, indent
            continue
        if inside_hooks and indent <= hooks_root_indent and not stripped.startswith("-"):
            # A sibling top-level key ends the block.
            if not re.fullmatch(r"hooks:\s*", stripped):
                inside_hooks = inside_event = False
                continue

        if not inside_hooks:
            continue

        if re.fullmatch(r"PreToolUse:\s*", stripped):
            inside_event = True
            matcher = ""
            continue
        # Any other event key (PostToolUse, Stop) closes PreToolUse.
        if re.fullmatch(r"[A-Za-z]+:\s*", stripped) and not stripped.startswith(
            ("matcher:", "hooks:", "type:", "command:")
        ):
            inside_event = re.fullmatch(r"PreToolUse:\s*", stripped) is not None
            matcher = ""
            continue

        if not inside_event:
            continue

        found = re.fullmatch(r"-?\s*matcher:\s*(.+)", stripped)
        if found:
            matcher = found.group(1).strip().strip("\"'")
            continue
        found = re.fullmatch(r"-?\s*command:\s*(.+)", stripped)
        if found and matcher:
            hooks.append(Hook(matcher=matcher, command=found.group(1).strip().strip("\"'")))
    return hooks


def read_agents(root: Path, glob: str = "skills/*/agents/*.md") -> dict[str, Agent]:
    """Map every bundled agent's id to what its frontmatter declares.

    An agent with no `tools:` key inherits every tool available to subagents,
    so the absent key is recorded as exactly that rather than as an empty list.
    """
    agents: dict[str, Agent] = {}
    for path in sorted(root.glob(glob)):
        parts = path.read_text(encoding="utf-8").split("---")
        if len(parts) < 3:
            raise SystemExit(f"FAIL: {path} has no frontmatter block")
        front = parts[1]
        name_match = NAME.search(front)
        if name_match is None:
            raise SystemExit(f"FAIL: {path} frontmatter declares no name")
        tools_match = TOOLS.search(front)
        tools = (
            [tool.strip() for tool in tools_match.group(1).split(",")]
            if tools_match
            else [TOOLS_ABSENT]
        )
        agents[name_match.group(1)] = Agent(
            path=path,
            name=name_match.group(1),
            tools=tools,
            pre_tool_use=_parse_pre_tool_use(front),
        )
    return agents
