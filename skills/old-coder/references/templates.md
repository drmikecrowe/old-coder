# SPEC and EVIDENCE Templates

The two artifacts the human actually reads. Both live in the task's artifact
directory (naming and layout in `setup.md`); the layers they reference are
defined in `gauntlet.md`.

## SPEC template (for the SPEC step)

`SPEC.md` is written into the task's artifact directory (see `setup.md`) at
SPEC time, before any implementation file is touched.

```markdown
# SPEC — <task name>

- Tier: <1|2|3>
- Issue: <tracker id, or "none"> <!-- optional; no dependency on any tracker -->
- Artifact dir: <artifacts>/<YYYYMMDD-HHMMSS>-<slug>/
- Isolation: <worktree | branch | none> — <one line of why>
- Setup plan:
  - Tools to install: <or "none">
  - Git: <init? checkpoint commit cadence? commit_args the repo mandates>
  - Files the gauntlet will add, **by path**: `tools/mutants.py` (mutation
    layer), `tools/gauntlet.sh` (entry point) — mark either "already exists,
    reused" — plus any fixture or harness file
  - New dependencies: <each with a one-line justification, or "none">

## Scenarios
<Gherkin below>

## Must NOT
- <negative constraint / invariant that must survive>

## Revisions
- <appended only; each entry says what changed and why>
```

Commit `SPEC.md` at approval (subject to the `commit` setting). Once the
approved spec is a commit, later drift is literally a `git diff` — that is what
turns "append-only" and "revise it visibly" from promises into mechanisms.
Without a durable spec, a compaction loses the approved contract while the code
it authorized remains, and nobody can check whether a scenario was quietly
dropped from the EVIDENCE mapping.

**If the human rejects the spec**, keep the directory and the file: revise
`SPEC.md` in place, add the reason to `## Revisions`, and re-request approval.
Do not delete it and start clean — what the human turned down, and why, is the
most useful thing in the file. Nothing is committed until a spec is approved, so
a rejected spec costs one directory and no history.

### Gherkin scenario template

```gherkin
Feature: <capability in user language>
  Scenario: <one concrete behavior>
    Given <concrete starting state>
    When  <concrete action with concrete input>
    Then  <concrete observable outcome, exact values>

  Scenario: <the error case>
    Given ...
    When  <invalid/hostile input>
    Then  <exact error type/message/status, and what state must NOT change>
```

Each scenario maps 1:1 to at least one automated test; name the test after the
scenario so the evidence report's spec→test mapping is mechanical.

## Evidence report template (for the EVIDENCE step)

Written to `EVIDENCE.md` in the task's artifact directory, alongside the
`SPEC.md` it answers.

```markdown
## Evidence Report — <task name> (Tier <1|2|3>)

- Spec: <artifacts>/<task dir>/SPEC.md (<committed as SHA | uncommitted>)
- Spec approval: <obtained from user | not obtained (autonomous run) —
  confidence downgraded; spec is the artifact to review after the fact>
- Source state: <commit SHA | uncommitted work, tree hash <sha256>> — persist
  the computation as a script (e.g. tools/source_state.sh); a hash recipe
  written in prose is working-directory-sensitive and will fail to reproduce
- Isolation: <worktree | branch | none> <; fallback reason if a worktree could
  not run the gauntlet>
- Config: <.old-coder.toml values in effect; note any tracked-file loosening
  that was ignored>
- Toolchain: <pinned versions file, e.g. requirements-dev.txt>
- Entry point: <single command that reruns every layer>
- Gauntlet cost: <total wall-clock; per-layer in the table below>
- Logs: <artifacts>/<task dir>/logs/
- Tracker: <issue id — roll-up posted | roll-up written to ROLLUP.md, not posted
  (tracker = propose, no approver) | none: SPEC named no issue>

### Spec → Test mapping
Status is one of: **pass / fail / unverified / n-a**. A row mapped to
"skipped: <reason>" must carry unverified or n-a — never pass.

| Scenario | Test | Status |
|---|---|---|
| <scenario name> | <test file>::<test name> | pass |
| Must NOT: <negative constraint> | <test / layer / skipped: reason> | pass \| unverified |

### Gauntlet (final fresh run)
Every command was redirected to the log named in the last column; the numbers
here are read from those logs. Cite only logs that were actually written — where
one command covers several layers, repeat that log on each row; where no script
can run the layer, write `manual`. A path to a file that does not exist is a
fabricated citation.

**Status is one of five, and the vocabulary is closed:**

| Status | Means | Required detail |
|---|---|---|
| `PASSED` | the layer's own instrument ran and was satisfied | the numbers |
| `FAILED` | it ran and was not satisfied | verbatim failure; you are not done |
| `N-A` | this project has no such surface — nothing to run, ever | why the surface does not exist |
| `UNAVAILABLE` | the surface exists, the tool does not | which tool, and that nothing was run in its place |
| `SUBSTITUTED` | something else was run instead of the specified instrument | what ran, **and what it cannot detect** |

`SUBSTITUTED` may never be written as a pass. Two repeat runs in place of
randomized order is not "suite health: stable" — it is
`SUBSTITUTED (2 repeat runs + 3-module cross-order — cannot detect whole-suite
order dependence)`. A reader who cannot tell a substitute from the real layer
will read "found nothing" where the truth is "did not look with that
instrument". `N-A` and `UNAVAILABLE` are likewise distinct: three `N-A` layers
describe the project, not a degraded run, and EVIDENCE should say so rather than
leaving a reader to count empty rows.

| Layer | Command | Status + result | Wall-clock | Log |
|---|---|---|---|---|
| Tests | <cmd> | PASSED — <N> passed, 0 failed | <mm:ss> | logs/tests.log |
| Types | <cmd> | PASSED — 0 errors (or `N-A: no type checker in this project — untyped codebase, no CI job`) | <mm:ss> | logs/types.log |
| Lint + format | <cmd> | PASSED — 0 warnings | <mm:ss> | logs/lint.log |
| Changed-line coverage | <cmd> | PASSED — <covered>/<total> changed lines (list any misses) | <mm:ss> | logs/coverage.log |
| Mutation | **required: the command**, e.g. `python tools/mutants.py` | PASSED — <killed>/<total> killed | <mm:ss> | logs/mutation.log |
| Property-based | <cmd> | PASSED — <N> properties, <examples/property> examples each | <mm:ss> | logs/property.log |
| Complexity budget | <cmd or "manual review"> | PASSED — <max function length / cyclomatic score, or "reviewed: N new functions, all single-purpose"> | <mm:ss> | logs/complexity.log \| manual |
| Real execution | <cmd> | PASSED — <observed output> | <mm:ss> | logs/run.log |
| Supply chain & secrets | <cmd> | PASSED — 0 known vulns; new deps: none (or list, each ↔ SPEC justification) | <mm:ss> | logs/supply-chain.log |
| Suite health | <cmd> | PASSED — randomized order (seed <n>), all passed (or `SUBSTITUTED: <what ran> — cannot detect <blind spot>`) | <mm:ss> | logs/suite-health.log |
| Integration-tree verification | <cmd, run in the integration tree, diff applied uncommitted then reverted> | PASSED — <N> passed, 0 failed; tree reverted clean (`git status` empty) (or `N-A: branch isolation, same tree`) | <mm:ss> | logs/integration.log (redirected by hand — outside the script, which runs in one tree) |
| Adversarial review | <model + agent type, e.g. "fresh general-purpose subagent, no inherited context, model X"> | PASSED — <N> findings: <N> CONFIRMED (resolved, numbers above are from a run post-dating the fixes), <N> dismissed (each with the check that disproves it), round <1|2> (or `N-A: Tier <1|2>, author wrote the code` / "abandoned after round 2") | <mm:ss> | logs/review.log † |

The **mutation row has no prose form.** "12/12 killed, mutants listed below for
manual re-application" is an incomplete row, not a passing one — the command is
part of the claim. If no script was persisted, the honest status is
`SUBSTITUTED (hand-applied edits — the score is not re-runnable)`.

Wall-clock is per layer, from the log or a wrapper timer, so the tier map can be
tuned by evidence rather than by feel. An estimate marked as one is fine; a
blank column is not.

† Unlike every other log here, `review.log` is written by the agent under
review, not by a tool. It records what the reviewer reported; it is not
independent evidence that a reviewer ran. Weight this layer below the
tool-generated ones, and ask for the reviewer's full transcript if its findings
matter to your decision.

If the change was **abandoned** after round 2, every other layer reads
`n-a: change abandoned`. An abandoned change has no green result; report the
findings that drove the decision and stop.

### Layers not run as specified
Split by status, because they mean different things to a reader:
- **N-A (this project has no such surface):** <layer — why it does not exist here>
- **UNAVAILABLE (tool missing):** <layer — which tool, nothing run in its place>
- **SUBSTITUTED:** <layer — what ran instead, and what that cannot detect>
- (or "none")

### Dismissed review findings
Fixes are self-evidencing; dismissals are not. One line each:
- <finding> — dismissed because <the command / file:line / test that disproves
  it>. <If the argument is "no alternative exists": which call sites it covers,
  and which it does not.>
- (or "none — every finding was fixed or accepted as a known limit")

### Structural blind spot
- <the layer this project cannot run at all, e.g. "the suite never exercises the
  container runtime, so nothing here is evidence about deployment behavior">

### Honest notes
- <failures hit during the task and how they were resolved; spec revisions; anything reducing confidence>
- <bugs found in relocated code: filed, not fixed here>
```

## Tracker roll-up (only when the SPEC names an issue)

Tracker linkage is **bidirectional and tracker-agnostic**: the SPEC header
carries an issue ID, and on completion a short roll-up goes back to that issue.
No hard dependency on any particular tracker — if the SPEC's `Issue` field says
`none`, this step does not exist.

Write it to `ROLLUP.md` in the task's artifact directory. Post it to the issue
only if `tracker = "allow"` or an approver says so in-task; with `propose` and
nobody present, leave it in the directory and say so in EVIDENCE. A hosted
tracker notifies people and cannot be un-sent, so it gets the same gate as a
commit.

```markdown
- Built: <one or two lines — what now exists that did not before>
- Left undone: <deliberate omissions, and why they were deliberate>
- Traps for the next task: <the thing that will bite whoever picks this up>
- Evidence: <artifacts>/<task dir>/  (SPEC.md, EVIDENCE.md, logs/)
```

**Why it is short, and why it is not a copy of EVIDENCE.** The two serve
different readers, and keeping them distinct is what stops them drifting into
rival sources of truth:

| | Reader | Obligation |
|---|---|---|
| EVIDENCE | the human reviewing **this** change | complete — every layer, every number, every limit |
| Tracker roll-up | whoever picks up the **next** task | short — what changed the ground under them, and where to find the rest |

A tracker whose notes are append-only by API gives the spec's no-silent-drift
property for free: an earlier note cannot be quietly rewritten to match a later
story. Where the tracker permits editing, that property is not there and the
git-commit-at-SPEC mechanism remains the enforcement — the roll-up is a
convenience for the next reader, never the authoritative record.
