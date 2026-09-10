#!/usr/bin/env python3
"""Keep the published verification contract and the gauntlet from drifting apart.

The contract in `demo-rate-limiter/spec.md` tells a reader which layers will
run before any of them has run. That is the point of publishing it at SPEC
approval rather than describing the run afterwards: a reader who knows the
layer list in advance can tell a missing layer from a layer that never existed.
A contract nobody checks decays into a description of what the harness used to
do, and it decays silently, because both files read as prose and neither parses
the other.

Two gradings, both set comparisons over layer names:

  missing   a layer the contract promises that `tools/gauntlet.sh` never runs
  unpromised a layer the gauntlet runs that the contract does not name

Fails closed. A contract section with no rows, a gauntlet with no `run_layer`
calls, and an absent file are each an error rather than a pass: a check that
compares nothing agrees with everything.

Usage: tools/contract_ids.py [spec-file] [gauntlet-file]

The optional arguments point the check at copies. Negative controls need them;
nothing else should pass them.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo-rate-limiter"
SPEC = DEMO / "spec.md"
GAUNTLET = DEMO / "tools" / "gauntlet.sh"

CONTRACT_HEADING = "## Verification contract"
LAYER_NAME = re.compile(r"^[a-z][a-z0-9-]*$")
RUN_LAYER = re.compile(r"^run_layer\s+([a-z][a-z0-9-]*)")


def read_text(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"FAIL: no file to read at {path}")
    return path.read_text(encoding="utf-8")


def contract_layers(spec: str) -> list[str]:
    """Layer names from the contract's own table, and from no other table.

    Scoped to the section rather than matched across the whole document: a spec
    is full of tables whose first cell looks like a layer name, and grading a
    row that was never part of the contract is the same defect as missing one.
    """
    lines = spec.splitlines()
    try:
        start = lines.index(CONTRACT_HEADING) + 1
    except ValueError:
        raise SystemExit(
            f"FAIL: no '{CONTRACT_HEADING}' section in the spec; nothing was compared"
        ) from None
    names: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip().strip("`")
        if LAYER_NAME.match(cell):
            names.append(cell)
    return names


def gauntlet_layers(script: str) -> list[str]:
    return [
        match.group(1)
        for line in script.splitlines()
        if (match := RUN_LAYER.match(line.strip())) is not None
    ]


def duplicates(names: list[str]) -> list[str]:
    counts = Counter(names)
    return sorted(name for name, count in counts.items() if count > 1)


def compare(promised: list[str], run: list[str]) -> list[str]:
    """Return every disagreement between contract and harness, worst first."""
    failures: list[str] = []
    for name in duplicates(promised):
        failures.append(f"the contract names `{name}` more than once")
    for name in duplicates(run):
        failures.append(f"the gauntlet runs `{name}` more than once")
    for name in sorted(set(promised) - set(run)):
        failures.append(
            f"the contract promises `{name}` and the gauntlet never runs it"
        )
    for name in sorted(set(run) - set(promised)):
        failures.append(f"the gauntlet runs `{name}` and the contract does not name it")
    return failures


def main(argv: list[str]) -> int:
    spec_path = Path(argv[1]).resolve() if len(argv) > 1 else SPEC
    gauntlet_path = Path(argv[2]).resolve() if len(argv) > 2 else GAUNTLET

    promised = contract_layers(read_text(spec_path))
    if not promised:
        raise SystemExit(
            f"FAIL: the '{CONTRACT_HEADING}' section in {spec_path.name} names "
            f"no layers; nothing was compared"
        )
    run = gauntlet_layers(read_text(gauntlet_path))
    if not run:
        raise SystemExit(
            f"FAIL: no run_layer calls found in {gauntlet_path.name}; "
            f"nothing was compared"
        )

    failures = compare(promised, run)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(
            f"verification contract: {len(failures)} disagreement(s) between "
            f"{spec_path.name} and {gauntlet_path.name}",
            file=sys.stderr,
        )
        return 1
    print(f"verification contract matches the gauntlet ({len(run)} layers)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
