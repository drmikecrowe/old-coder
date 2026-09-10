#!/usr/bin/env python3
"""Keep the published ceiling and the internal audit from drifting apart.

`docs/loop-alignment.md` is the audit. `skills/old-coder/references/ceiling.md`
is what the skill tells its readers it does not enforce. Both are prose tables,
and neither parses the other, so a row corrected in one and forgotten in the
other drifts silently. A published ceiling that has drifted tells readers the
skill enforces something it does not, which is the exact overclaim the skill is
about.

Two gradings, both set comparisons:

  membership  every rule id the audit does not mark `enforced` appears in the
              ceiling, and every id in the ceiling is one the audit does not
              mark `enforced`. A difference in either direction fails
  agreement   for each shared id, the two files name the same end state

Fails closed: a file it cannot read, or a table it finds no rule ids in, is an
error rather than a pass.

Usage: tools/ceiling_ids.py [audit-file] [ceiling-file]

The optional arguments point the check at copies. Negative controls need them;
nothing else should pass them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "docs" / "loop-alignment.md"
CEILING = ROOT / "skills" / "old-coder" / "references" / "ceiling.md"

RULE_ID = re.compile(r"^(IN|EX|VE|CO|DR)-\d+$")


def read_rows(path: Path, state_column: int) -> dict[str, str]:
    """Map rule id to end state for every rule row in a markdown table."""
    if not path.is_file():
        raise SystemExit(f"FAIL: no file to read at {path}")
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) <= state_column:
            continue
        rule_id = cells[1].strip()
        if not RULE_ID.match(rule_id):
            continue
        if rule_id in rows:
            raise SystemExit(f"FAIL: {path.name} lists {rule_id} more than once")
        rows[rule_id] = cells[state_column].strip()
    if not rows:
        raise SystemExit(f"FAIL: no rule rows found in {path}; nothing was compared")
    return rows


def family(state: str) -> str:
    """The end state without its destination, so the two tables can be compared.

    The audit writes `delegated -> \\`repo\\` VE-1` in one cell; the ceiling puts
    the destination in a column of its own. Only the state itself is shared.
    """
    words = state.split()
    if len(words) >= 3 and words[0] == "n-a" and words[1] == "by":
        return "n-a by scope"
    return words[0] if words else ""


def compare(audit: dict[str, str], ceiling: dict[str, str]) -> list[str]:
    """Return every disagreement between the two tables, worst first."""
    unenforced = {i: s for i, s in audit.items() if family(s) != "enforced"}
    failures: list[str] = []

    for rule_id in sorted(set(unenforced) - set(ceiling)):
        failures.append(
            f"{rule_id} is `{unenforced[rule_id]}` in the audit and is missing "
            f"from the published ceiling"
        )
    for rule_id in sorted(set(ceiling) - set(unenforced)):
        known = audit.get(rule_id)
        reason = "is `enforced` in the audit" if known else "is not an audit row"
        failures.append(f"{rule_id} appears in the published ceiling but {reason}")
    for rule_id in sorted(set(unenforced) & set(ceiling)):
        want, got = family(unenforced[rule_id]), family(ceiling[rule_id])
        if want != got:
            failures.append(
                f"{rule_id} is `{want}` in the audit and `{got}` in the ceiling"
            )
    return failures


def main(argv: list[str]) -> int:
    audit_path = Path(argv[1]).resolve() if len(argv) > 1 else AUDIT
    ceiling_path = Path(argv[2]).resolve() if len(argv) > 2 else CEILING
    failures = compare(read_rows(audit_path, 3), read_rows(ceiling_path, 3))
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(
            f"ceiling ids: {len(failures)} disagreement(s) with {audit_path.name}",
            file=sys.stderr,
        )
        return 1
    print(f"ceiling ids agree with {audit_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
