# SPEC and EVIDENCE Templates

The two artifacts the human actually reads. Both live in the task's artifact
directory (naming and layout in `setup.md`); the layers they reference are
defined in `gauntlet.md`.

## SPEC template (for the SPEC step)

`SPEC.md` is written into the task's artifact directory (see `setup.md`) at
SPEC time, before any implementation file is touched.

```markdown
# SPEC — <task name>

## TL;DR
- **Change:** <one sentence — what is different once this is done>
- **Why:** <the problem, not the solution restated>
- **Touches:** <files and subsystems in blast radius, or "new file only">
- **Decide:** <the 1-3 calls most likely to be wrong, that you want ruled on>

The contract below, in brief — enough to tell a reader which scenarios to read
closely, never a substitute for reading them:

- **Covers:** <the scenario groups, one bullet each — "the happy path", "input
  validation", "concurrency", "the boundary cases">
- **Must NOT:** <the invariants that must survive, in a phrase each>
- **Out of scope:** <what a reader might reasonably expect and will not get>

- Tier: <1|2|3>
- Issue: <tracker id, or "none"> <!-- optional; no dependency on any tracker -->
- Artifact dir: <artifacts>/<YYYYMMDD-HHMMSS>-<slug>/
- Isolation: <worktree | branch | none> — <one line of why>
- Artifacts: file only <| + tracker comment | + PR body> — <where a projection
  goes, if anywhere; the file is always written>
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

**The TL;DR orients; the scenarios are the contract.** A human who approves the
summary has approved nothing — the four bullets are there to tell them which
scenarios to read closely, and `Decide:` is where you name the calls you want
overruled rather than burying them in a Given/When/Then. If the summary and the
scenarios ever disagree, the scenarios win and the summary is a defect: fix it
and say so in `## Revisions`.

Commit `SPEC.md` at approval (subject to the commit grant). Once the
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

## TL;DR
- **Verdict:** <PASSED | PASSED WITH LIMITS | FAILED | ABANDONED>
- **Delivered:** <one sentence — the behavior now in the tree>
- **Proven:** <N/N scenarios mapped and passing> — <the layers carrying the most weight>
- **Not proven:** <every substituted or not-run layer, and the known limits — or
  "nothing: every layer ran as specified">
- **Read first:** <the one section a skeptical reader should open>

The writeup below, in brief — one bullet per section, each carrying that
section's headline rather than its title:

- **Spec → test mapping:** <N mapped, N pass, N unverified/n-a — and which>
- **Gauntlet:** <the numbers that matter: tests, coverage, mutation score> —
  <any layer that is not PASSED, named>
- **Review / verification:** <rounds run, findings CONFIRMED vs dismissed, what
  the last round said, whether the shipped state was reviewed>
- **Known limits:** <the gaps a reader must carry forward>
- **Honest notes:** <the one or two entries that change how much to trust this>

- Spec: <artifacts>/<task dir>/SPEC.md (<committed as SHA | uncommitted>)
- Spec approval: <obtained from user | not obtained (autonomous run) —
  confidence downgraded; spec is the artifact to review after the fact>
- Spec intent review: <`spec-intent` ran — <N> points, <what changed in the spec>,
  <what you disagreed with and why> | not run — reason>
- Source state: <commit SHA | uncommitted work, tree hash <sha256>> — persist
  the computation as a script (e.g. tools/source_state.sh); a hash recipe
  written in prose is working-directory-sensitive and will fail to reproduce
- Isolation: <worktree | branch | none> <; fallback reason if a worktree could
  not run the gauntlet>
- Grants in effect: <which permissions were standing, and from which scope; note
  any loosening instruction ignored because it was found in project rules>
- Toolchain: <pinned versions file, e.g. requirements-dev.txt>
- Entry point: <single command that reruns every layer>
- Independent verification: <not performed | passed | failed | blocked>
  **against the final source state** — a state no verifier saw is
  `not performed` however many rounds preceded it (Tier 3 option; protocol in
  `verifier.md`)
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
| Adversarial review | <agent + model, e.g. "`adversary`, fresh, no inherited context, model X"; note any deviation from its declared tools/budget> | PASSED — <N> findings: <N> CONFIRMED (resolved, numbers above are from a run post-dating the fixes), <N> dismissed (each with the check that disproves it), round <1|2> (or `N-A: Tier <1|2>, author wrote the code` / "abandoned after round 2") | <mm:ss> | logs/review.log † |

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

### Independent verification (omit only when it was not run at all; see verifier.md)
This is not a gauntlet layer and gets no row in the table above — it is prose a
human graded. Keep it out of the layer table and record it here.
- Verifier: <host / model family>; fresh context; which inputs it received;
  what correlation that breaks and what it does not.
- Rounds: <n> (cap <m>); verdict per round, each against the state it saw.
- Grading: who classified each finding behavioural vs description, and who
  approved stopping.
- Attacked: <what was tried, not only what was found>.
- Findings: behavioural (fixed, then re-verified in a new context) vs
  description/mapping (fixed and disclosed, no new round).
- Fixed after the last verified state, therefore unverified: <list | none>.

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

**Write the TL;DR last, from the tables, never from memory.** It is the only part
of this report most readers will finish, which makes it the one place overstating
the result actually pays — so it is held to the strictest version of the rule the
rest of the report already follows. The mapping table and the gauntlet table are
authoritative; the summary is a reading of them. A `PASSED` verdict above a table
containing a `fail`, an `unverified`, or a `SUBSTITUTED` layer is not a summary,
it is the report lying to the reader who stopped at the top — anti-gaming rule 5
applies to it exactly as it applies to a fabricated layer.

Two consequences worth stating plainly:

- **`PASSED WITH LIMITS` is the honest verdict far more often than `PASSED`.**
  Any substituted layer, any `unverified` row, any accepted known limit puts the
  report there. Reserve `PASSED` for a run where `Not proven:` reads "nothing".
- **`Not proven:` is the load-bearing bullet.** A reader deciding how much to
  trust this change is really deciding how much weight the missing layers carried.
  If that bullet is empty while the sections below list limits, the summary is
  wrong and the tables are right.

## Projections — publishing an artifact outward

`SPEC.md` and `EVIDENCE.md` are always written to the artifact directory. A
**destination** declared in the SPEC says whether a *projection* of one of them is
also published to a tracker or a PR body. It is per-task and declared where the
human approves it, not inherited from a setting nobody re-reads — the same reason
the isolation mechanism is declared there.

Publishing is never a move. A published copy cannot carry `logs/`, binds to no
SHA, and stays editable after review, so the file in the artifact directory stays
the artifact and the projection stays a rendering of it.

Three rules govern every projection, whatever its surface:

- **It is derived, never authored.** Build it from the file, and rebuild it when
  the source state moves. A projection nobody regenerates is stale the moment the
  next commit lands, and it will not look stale.
- **It is short.** It names the verdict and points at the artifact. Pasting a
  full Tier 3 EVIDENCE into a PR body is both over the surface's size cap and the
  wrong obligation for that reader.
- **It carries the source state.** Every projection ends with the SHA and the
  artifact path, so a reader who doubts it can go to the authoritative copy.

### Tracker roll-up (only when the SPEC names an issue)

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

### SPEC projection (destination: tracker)

Post the SPEC's **TL;DR** to the issue as a **comment**, never into the issue
description. The distinction is load-bearing: comments are append-only by API on
most trackers, so a revised spec becomes a second comment and the history stays
readable. An issue description is edited in place, which reproduces exactly the
silent drift the commit-at-approval rule exists to prevent.

```markdown
**SPEC — <task name>** (Tier <1|2|3>) · approval requested

<the SPEC TL;DR block verbatim>

Full contract (scenarios, Must NOT, failure model): `<artifacts>/<task dir>/SPEC.md`
<committed as <sha> | uncommitted>
```

Each revision is a **new comment** naming what changed and why, mirroring
`## Revisions`. Never edit an earlier one.

**Approval recorded here is stronger than approval in chat.** A comment or label
from a named human at a known time survives compaction and is checkable by
someone who was not present — which chat approval is not. Where the tracker
carries the approval, EVIDENCE cites it (`spec approval: obtained — <issue>#<comment>`)
and the autonomous-run downgrade does not apply. This is the one place these
settings make the loop stronger rather than merely more flexible.

### EVIDENCE projection (destination: PR body)

Only into a PR that **already exists**, and only a draft one unless a rule says
otherwise. This skill does not open pull requests in any configuration — the human
opens the PR, the skill fills it. Without a user-scope grant, or with no PR open,
write this block to `PR_BODY.md` in the artifact directory and say so in
EVIDENCE — that is the expected outcome, not a failure.

```markdown
<the EVIDENCE TL;DR block verbatim — verdict, delivered, proven, not proven,
and the section-by-section digest>

---
Source state: `<sha>` · Reviewed: `<sha the adversarial review read>`
Full evidence and logs: `<artifacts>/<task dir>/` (EVIDENCE.md, SPEC.md, logs/)
Reruns every layer: `<entry point command>`
```

**Regenerate it on every push.** A PR body describing an earlier commit is worse
than an absent one, because the reader has no way to tell. If the projection
cannot be refreshed, replace its verdict line with
`STALE — describes <sha>, HEAD is <sha>` rather than leaving the old verdict
standing. The adversarial review's SHA-binding rule (`gauntlet.md`) applies here
unchanged: a review is a claim about a commit, and a PR body is the easiest place
to lose track of which one.
