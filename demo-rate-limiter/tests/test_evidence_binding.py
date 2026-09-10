"""Negative controls for the evidence/review binding check (REVISION 9).

Every test drives the checker through a fake source-state command, so none of
these touch git. The checker's contract is that only that command produces a
binding, which makes the fake the whole environment it can see.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
CHECKER = TOOLS / "evidence_binding.py"

DERIVED = "5a0eefa64a2cc101"
STALE = "0000000000000000"


def _fake_source_state(tmp_path: Path, tree: str = DERIVED, rc: int = 0) -> Path:
    """A stand-in for tools/source_state.sh with a pinned answer."""
    script = tmp_path / "fake_source_state.sh"
    script.write_text(
        "#!/bin/sh\n"
        "echo 'head:          abc1234'\n"
        "echo 'source commit: def5678'\n"
        f"echo 'tree:          {tree}'\n"
        f"exit {rc}\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _report(
    tmp_path: Path,
    *,
    verdict: str = "PASSED WITH LIMITS",
    tree: str = DERIVED,
    review: str = f"tree `{DERIVED}`",
    name: str = "evidence.md",
) -> Path:
    report = tmp_path / name
    report.write_text(
        "# Evidence Report\n\n"
        "## Orientation\n"
        f"- **Verdict:** **{verdict}.** Prose the checker must not need.\n"
        f"- Source state: source commit `def5678`; sha256 tree hash\n"
        f"  `{tree}` — reproduce with `./tools/source_state.sh`.\n"
        f"- Review binding: {review}\n",
        encoding="utf-8",
    )
    return report


def _run(report: Path, source_state: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["EVIDENCE_REPORT"] = str(report)
    env["EVIDENCE_SOURCE_STATE_CMD"] = str(source_state)
    return subprocess.run(
        ["python3", str(CHECKER)],
        capture_output=True,
        text=True,
        env=env,
    )


def test_current_binding_under_a_limited_verdict_passes(tmp_path: Path) -> None:
    result = _run(_report(tmp_path), _fake_source_state(tmp_path))
    assert result.returncode == 0, result.stderr


def test_bare_passed_over_a_current_review_passes(tmp_path: Path) -> None:
    report = _report(tmp_path, verdict="PASSED")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 0, result.stderr


def test_stale_report_binding_fails(tmp_path: Path) -> None:
    """The report cites a tree the source-state command did not produce."""
    report = _report(tmp_path, tree=STALE)
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert STALE in result.stderr
    assert DERIVED in result.stderr


def test_bare_passed_over_a_stale_review_fails(tmp_path: Path) -> None:
    """A round bound to an older state cannot carry an unqualified PASSED."""
    report = _report(tmp_path, verdict="PASSED", review=f"tree `{STALE}`")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    # Naming both hashes is what distinguishes this failure from every other
    # message that happens to contain the word PASSED.
    assert STALE in result.stderr
    assert DERIVED in result.stderr
    assert "caps the verdict" in result.stderr


def test_stale_review_under_a_limited_verdict_passes(tmp_path: Path) -> None:
    """A declared downgrade is exactly what an older round is allowed to be."""
    report = _report(tmp_path, review=f"tree `{STALE}`")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 0, result.stderr


def test_unavailable_review_binding_cannot_carry_bare_passed(tmp_path: Path) -> None:
    report = _report(tmp_path, verdict="PASSED", review="unavailable (no verifier ran)")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1


def test_missing_review_binding_field_fails(tmp_path: Path) -> None:
    """A checker that cannot find the field it grades reports nothing wrong."""
    report = tmp_path / "evidence.md"
    report.write_text(
        "# Evidence Report\n\n"
        "- **Verdict:** **PASSED WITH LIMITS.**\n"
        f"- Source state: source commit `def5678`; sha256 tree hash\n"
        f"  `{DERIVED}` — reproduce with `./tools/source_state.sh`.\n",
        encoding="utf-8",
    )
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "review binding" in result.stderr.lower()


def test_missing_source_state_field_fails(tmp_path: Path) -> None:
    report = tmp_path / "evidence.md"
    report.write_text(
        "# Evidence Report\n\n"
        "- **Verdict:** **PASSED WITH LIMITS.**\n"
        f"- Review binding: tree `{DERIVED}`\n",
        encoding="utf-8",
    )
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "source state" in result.stderr.lower()


def test_missing_verdict_fails(tmp_path: Path) -> None:
    report = tmp_path / "evidence.md"
    report.write_text(
        "# Evidence Report\n\n"
        f"- Source state: source commit `def5678`; sha256 tree hash\n"
        f"  `{DERIVED}`.\n"
        f"- Review binding: tree `{DERIVED}`\n",
        encoding="utf-8",
    )
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "verdict" in result.stderr.lower()


def test_absent_report_fails(tmp_path: Path) -> None:
    result = _run(tmp_path / "nowhere.md", _fake_source_state(tmp_path))
    assert result.returncode == 1


def test_failing_source_state_command_fails_closed(tmp_path: Path) -> None:
    """No binding means no verdict, never a pass on an unchecked report."""
    report = _report(tmp_path)
    result = _run(report, _fake_source_state(tmp_path, rc=2))
    assert result.returncode == 1
    assert "source-state" in result.stderr.lower()


def test_source_state_without_a_tree_line_fails_closed(tmp_path: Path) -> None:
    script = tmp_path / "silent.sh"
    script.write_text("#!/bin/sh\necho 'head:  abc1234'\n", encoding="utf-8")
    script.chmod(0o755)
    result = _run(_report(tmp_path), script)
    assert result.returncode == 1


def _duplicated(tmp_path: Path, extra: str) -> Path:
    """A report carrying a second copy of a graded field, above the real one."""
    report = tmp_path / "evidence.md"
    report.write_text(
        "# Evidence Report\n\n"
        "## Honest notes\n"
        f"{extra}\n\n"
        "## Orientation\n"
        "- **Verdict:** **PASSED.** The claim actually being graded.\n"
        "- Source state: source commit `def5678`; sha256 tree hash\n"
        f"  `{DERIVED}` — reproduce with `./tools/source_state.sh`.\n"
        f"- Review binding: tree `{STALE}`\n",
        encoding="utf-8",
    )
    return report


def test_a_second_verdict_is_ambiguous_not_a_tiebreak(tmp_path: Path) -> None:
    """First-match-wins would read the earlier verdict and skip the real check."""
    report = _duplicated(tmp_path, "An earlier **verdict:** **PASSED WITH LIMITS.**")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "ambiguous" in result.stderr
    assert "verdict" in result.stderr


def test_a_second_report_binding_is_ambiguous(tmp_path: Path) -> None:
    report = _duplicated(
        tmp_path, f"A quoted sha256 tree hash\n  `{DERIVED}` from an old run."
    )
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "ambiguous" in result.stderr
    assert "source state" in result.stderr


def test_a_second_review_binding_is_ambiguous(tmp_path: Path) -> None:
    report = _duplicated(tmp_path, f"Review binding: tree `{DERIVED}` (round 1)")
    result = _run(report, _fake_source_state(tmp_path))
    assert result.returncode == 1
    assert "ambiguous" in result.stderr
    assert "review binding" in result.stderr
