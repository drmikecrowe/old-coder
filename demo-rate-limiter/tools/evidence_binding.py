#!/usr/bin/env python3
"""One identity function for the evidence report and the reviews it counts.

`source_state.py` hashes the tracked manifest and fails closed. Everything else
in `evidence.md` used to be a value a human typed, and nothing compared the two.
A report could cite a clean commit over a dirty tree, or keep a binding three
source commits stale, with every layer green. REVISION 9 closes that.

Two gradings:

  report binding   the tree hash the report gives for its own gauntlet run must
                   equal the one the source-state command derives now
  review binding   a verification round may bind to an older state, because a
                   declared downgrade is exactly that. It may not do so under a
                   bare `PASSED`

Only the source-state command produces a binding. This file never hashes
anything itself: a second implementation of the identity function is the defect
being closed, reintroduced. It also never reads `gauntlet-stamp.txt`, which the
exit trap writes after every layer has run, so a layer reading it would grade
the previous run. The stamp carries this same command's output by REVISION 8,
so the two cannot disagree.

Environment:
  EVIDENCE_REPORT           report to grade (default: the demo's evidence.md)
  EVIDENCE_SOURCE_STATE_CMD command that derives the binding
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent
REPORT = Path(os.environ.get("EVIDENCE_REPORT") or DEMO / "evidence.md")
SOURCE_STATE_CMD = os.environ.get("EVIDENCE_SOURCE_STATE_CMD") or str(
    DEMO / "tools" / "source_state.sh"
)

# `- **Verdict:** **PASSED WITH LIMITS.**` — the closed set, longest first so
# `PASSED WITH LIMITS` cannot be read as a bare `PASSED`.
VERDICT = re.compile(
    r"\*\*Verdict:\*\*\s*\*\*(PASSED WITH LIMITS|PASSED|FAILED)", re.IGNORECASE
)
# The field wraps across lines in real reports, so match past the newline.
REPORT_BINDING = re.compile(r"sha256 tree hash\s*`?\s*\n?\s*`([0-9a-f]{8,})`")
# `- Review binding: tree \`<hash>\`` or `- Review binding: unavailable (why)`
REVIEW_BINDING = re.compile(r"Review binding:\s*(?:tree\s*`([0-9a-f]{8,})`|(\S.*))")
DERIVED_TREE = re.compile(r"^tree:\s*(\S+)$", re.MULTILINE)


def derive_tree() -> str:
    """Return the tree hash the source-state command produces, or fail closed."""
    try:
        run = subprocess.run(
            [SOURCE_STATE_CMD],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise SystemExit(f"FAIL: source-state command unusable: {error}") from error
    if run.returncode != 0:
        raise SystemExit(
            f"FAIL: source-state command exited {run.returncode}; "
            f"no binding, so nothing is graded"
        )
    match = DERIVED_TREE.search(run.stdout)
    if match is None:
        raise SystemExit("FAIL: source-state command emitted no tree line")
    return match.group(1)


def read_report(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"FAIL: no evidence report at {path}")
    return path.read_text(encoding="utf-8")


def sole_match(pattern: re.Pattern[str], text: str, field: str) -> re.Match[str] | str:
    """Return the report's one match for a field, or the reason there is not one.

    Grading the first of several matches grades whichever the author happened to
    write first, in a report that is hundreds of lines of prose full of hashes
    and verdicts. So more than one is a failure, not a tiebreak: the report has
    to say which one it means.
    """
    matches = list(pattern.finditer(text))
    if not matches:
        return f"no {field} field found in the report"
    if len(matches) > 1:
        lines = ", ".join(str(text.count("\n", 0, m.start()) + 1) for m in matches)
        return (
            f"{field} field is ambiguous: {len(matches)} matches (lines {lines}). "
            f"A checker that grades the first of several grades the wrong one"
        )
    return matches[0]


def grade(text: str, derived: str) -> list[str]:
    """Return every failing row, worst first. Empty means the report agrees."""
    failures: list[str] = []

    verdict_match = sole_match(VERDICT, text, "verdict")
    if isinstance(verdict_match, str):
        return [verdict_match]
    verdict = verdict_match.group(1).upper()

    report_match = sole_match(REPORT_BINDING, text, "source state")
    if isinstance(report_match, str):
        failures.append(report_match)
    elif report_match.group(1) != derived:
        failures.append(
            f"report binding is stale: report says `{report_match.group(1)}`, "
            f"the source-state command derives `{derived}`"
        )

    review_match = sole_match(REVIEW_BINDING, text, "review binding")
    if isinstance(review_match, str):
        failures.append(review_match)
    elif verdict == "PASSED":
        review = review_match.group(1)
        if review is None:
            failures.append(
                f"verdict is a bare PASSED over a review binding of "
                f"'{review_match.group(2).strip()}'; an unbound review caps the "
                f"verdict at PASSED WITH LIMITS"
            )
        elif review != derived:
            failures.append(
                f"verdict is a bare PASSED over a review bound to `{review}`, "
                f"not the current `{derived}`; a stale review caps the verdict "
                f"at PASSED WITH LIMITS"
            )
    return failures


def main() -> int:
    derived = derive_tree()
    failures = grade(read_report(REPORT), derived)
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        print(
            f"evidence binding: {len(failures)} disagreement(s) with {derived}",
            file=sys.stderr,
        )
        return 1
    print(f"evidence binding agrees with the source state ({derived})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
