---
name: old-coder
description: Evidence-first development — surround the implementation with an executable spec and a gauntlet of constraints (tests, types, coverage, mutation) so line-by-line review becomes optional. Use when the user explicitly asks for high-assurance or evidence-first work ("reliable", "TDD", "prove it works", "I won't read the code"), or when the change touches high-stakes domains (money, auth, data loss, concurrency, public API). Work happens in an isolated branch or worktree and ends at an evidence report — this skill never pushes, opens a PR, or publishes, except an optional tracker roll-up, and only where explicitly granted. For routine changes where the user just wants normal tests, write good tests directly instead of invoking this loop.
---

# Old Coder: Reliable Coding Under Constraint and Test

The human will NOT read your implementation. Their confidence comes entirely from
two artifacts you produce: (1) an **executable specification** they approve before
you write code, and (2) an **evidence report** proving the code ran the gauntlet.
Your job is to make those two artifacts trustworthy enough that line-by-line
review becomes optional within the spec's boundaries.

This inverts the normal review model: **trust moves from inspection to
constraints.** Be honest about what that buys: the gauntlet proves the code
satisfies every constraint the spec expresses — it cannot prove the spec
expresses everything that matters. That is exactly why the human approves the
SPEC (the one artifact that breaks the everything-authored-by-the-same-agent
correlation), and why EVIDENCE reports layered, auditable confidence, never
absolute proof. Every shortcut you take against the gauntlet destroys the only
basis of trust.

## Where this skill stops

**It ends at EVIDENCE.** It does not push, open a pull request, or publish. It
writes code, verifies it, and hands the human a report; they decide what happens
next. One exception, and only one: the tracker roll-up posts to an issue when
the human has set `tracker = "allow"` on that machine. Default is `propose` —
write the note, post nothing.

So with the default config, nothing this skill does is outward-facing and an
unattended run cannot cause external harm. The confidence downgrade for
autonomous mode is therefore about **evidence quality** — the spec was never
reviewed by an independent party — not about blast radius. Granting
`tracker = "allow"` is the one setting that trades that property away, which is
why it cannot be granted by a committed config file.

## The Loop

```
SPEC → (human approves spec, not code) → RED → GREEN → REFACTOR → GAUNTLET → EVIDENCE
                                          ↑_____________________|
                                              repeat per behavior
```

### 1. SPEC — the only thing the human reads before code

Turn the request into **executable acceptance criteria** before touching
implementation files:

- Write behaviors as Gherkin-style scenarios or a named test list — concrete
  inputs, concrete expected outputs, edge cases, and error cases. "Handles bad
  input" is not a spec; `divide(1, 0) raises ZeroDivisionError with message X` is.
- Include what the change must NOT do (invariants that must survive: existing
  tests, public API signatures, performance budgets if stated). These negative
  constraints are contract clauses like any scenario: each must end up mapped
  in EVIDENCE to a test, a gauntlet layer, or an explicit skipped-with-reason
  line — never silently absent from the mapping.
- The spec doubles as the authorization point: include the **setup plan** —
  tools to install, git usage (init? checkpoint commit cadence?), **the files
  the gauntlet will add, named individually** (the mutation script and the
  gauntlet entry point are files: list them by path, because a script nobody
  authorized is a script nobody writes), and **every new dependency with a
  one-line justification**
  (prefer the standard library and deps already present; an unjustified
  package is a spec defect) — so approving the spec authorizes the environment
  changes in one step instead of N interruptions, and the human can veto a
  risky package before it is ever installed.
- Show the spec to the human in plain language and get approval **before writing
  implementation**. In autonomous mode, state the spec in your response and
  proceed — but the correlation-breaking review never happened, so EVIDENCE
  must record `spec approval: not obtained (autonomous run)` and claim
  correspondingly lower confidence; the spec becomes the artifact the human
  reviews after the fact.
- The spec is append-only during the task. If implementation reveals the spec was
  wrong, say so explicitly and revise it visibly — never silently drift.
- **The spec is a file, not a message.** Create the task's artifact directory
  now — `<artifacts>/<YYYYMMDD-HHMMSS>-<slug>/`, UTC, one per *task* — and write
  `SPEC.md` there, with a tracker issue ID in the header if one exists (layout:
  `references/setup.md`; template: `references/templates.md`). **Commit it at
  approval** — subject to `commit`, and only possible if the artifact directory
  is *not* gitignored: once the approved spec is a commit, later drift is
  literally a `git diff`, which makes "append-only" a mechanism rather than a
  promise. Gitignore the directory and that mechanism is gone, not merely
  weakened (`references/setup.md`).
- Declare the **isolation mechanism** (worktree / branch / none, and why) in the
  spec, so the human can see and veto it before work starts.

### 2. RED — prove each test can fail

Write the test for one behavior. **Run it and watch it fail** before writing the
implementation. A test you never saw fail proves nothing — it may be testing
nothing. Details that matter in practice:

- If the module under test doesn't exist yet, create a stub that raises
  (e.g. `NotImplementedError`) so the test fails on behavior, not on import —
  a collection error is a weaker RED than an assertion failure.
- Related behaviors may share one RED run, as long as each new test is
  individually observed failing.
- If a new test passes immediately, it is either vacuous (fix it) or the
  behavior already exists. **Don't just assert which — prove it**: break the
  implementation with a one-off throwaway mutant, watch the test fail, restore.
  Then record it as pre-existing behavior kept as regression armor.

**A pure move has no RED.** Relocating code introduces no behavior, so there is
no failing test to write, and inventing one produces a test that asserts the
refactor happened rather than asserting behavior — a failure class the
adversarial reviewer is briefed to hunt. Substitute two checks instead, and say
in EVIDENCE that you did:

1. **Byte-identity of the moved block**, mechanically, not by eye — extract the
   original from git and `diff` it against the new location
   (`git show <base>:<old path>` piped through the line range, diffed against
   the new file). Any surviving difference is a behavior change and belongs back
   in SPEC.
2. **Mutation on the relocated code**, because tests that patch a symbol *by
   location* silently stop applying once it moves and keep passing while
   asserting nothing (`references/gauntlet.md`, "mutation testing on relocated
   code"). A green suite immediately after a move is the case most likely to be
   hollow.

A change that both moves and modifies gets split: move first, prove identity,
then run the normal loop on the behavior change.

### 3. GREEN — minimal implementation

Write the least code that makes the failing test pass. Run the full suite, not
just the new test.

### 4. REFACTOR — clean up under green, assertions frozen

Minimal code is often ugly code. While the suite is green, improve names,
extract duplication, and simplify structure. What is frozen is **behavioral
assertions**, not test files wholesale:

- Implementation refactors touch no test files at all.
- Test-structure refactors (extracting helpers and fixtures, deduplicating
  setup) are allowed as a **separate step**: assertions unchanged, suite green
  before and after, then rerun mutation to confirm the restructured tests
  still kill — a refactor that blunts the tests is a silent hole in the
  gauntlet.
- Anything that requires editing an assertion isn't refactoring, it's a
  behavior change and belongs back in SPEC.

Run the suite after each refactor. Repeat RED→GREEN→REFACTOR per behavior.

### 5. GAUNTLET — the constraint stack

After all spec behaviors are green, run every applicable layer. Scale to the task
(see "Calibration"), but never skip a layer silently — every layer resolves to
one of the five statuses in the EVIDENCE section below, and three of them
require stating what was *not* verified.

| Layer | What it catches | How |
|---|---|---|
| Full test suite | regressions | project's test command, zero NEW failures (baseline note below) |
| Static types | whole classes of bugs | tsc / mypy / etc., zero new errors |
| Lint + format | latent bugs, drift | project's linter, zero new warnings |
| Coverage on changed lines | untested code paths | every changed/added line executed by a test; branch coverage where the tool supports it. Global % is vanity — changed-line coverage is the constraint |
| Mutation testing | tests that assert nothing | see `references/gauntlet.md`. No mutation tool? Do manual mutation **as a persisted script** (e.g. `tools/mutants.py`) holding 3–5 plausible bugs as data — flip a comparison, off-by-one a bound, drop a condition, return early — which applies each, runs the suite, restores, and verifies the restore with `git diff`. The suite must kill every one. Hand-editing the source N times is not this layer: it leaves no re-runnable command and no proof the tree came back clean |
| Property-based tests | edge cases you didn't imagine | for parsing, math, serialization, anything with invariants (round-trip, idempotence, ordering) — add hypothesis/fast-check properties |
| Complexity budget | unmaintainable output | new functions small and single-purpose; if a function needs a paragraph to explain, split it |
| Real execution | "passes tests, doesn't run" | actually run the app/CLI/endpoint once on a realistic input, not only the test harness |
| Supply chain & secrets | vulnerable/unnecessary deps, leaked credentials | when the dependency set changed: audit it (pip-audit / npm audit / govulncheck / cargo-audit) and check licenses; scan the diff for secrets; every new dependency must trace back to its SPEC justification. Also eyeball the capability diff: did the change start using network / subprocess / filesystem / env it didn't before? |
| Suite health | flaky or order-dependent tests | run the suite in randomized order (pytest-randomly etc.); repeat suspected flakes. Every EVIDENCE number rests on the suite being deterministic — a flaky suite quietly invalidates the report |
| Integration-tree verification | "green in isolation, broken on merge" | whenever the isolated tree and the tree the change lands in differ by ignored or untracked content, rerun the suite in the landing tree — by **applying the diff uncommitted and reverting**, never by merging, rebasing, or committing there (exact recipe in `references/gauntlet.md`). A green run in a tree that lacks the main tree's `.env`, build outputs, or installed deps is not evidence about the main tree |
| Adversarial review | reasoning the author cannot audit | a **fresh general-purpose subagent with no inherited context**, briefed to falsify the claim that the change is correct. Procedure, failure-class list, and the two-round limit in `references/gauntlet.md` |

Redirect every layer to its own log under the task's `logs/` dir and read a
bounded slice — `cmd > log 2>&1`, never `tee` (`references/gauntlet.md`).
EVIDENCE cites the log path beside each number, so every claim traces to a run.

Baseline note — on a repo with pre-existing failures, record the baseline
first (which tests already fail, verbatim) and hold the line at zero NEW
failures. Fixing unrelated pre-existing failures is scope creep: surface them,
don't silently "improve" them.

Mutation caveat — **kills are attributed to whichever test fails first**, so a
7/7 kill score validates the suite as a whole, not every layer in it. In Tier 3,
rerun the mutants against the property suite alone before claiming the
properties verify anything; survivors there mean the invariants have blind
spots (a common one: a one-sided invariant like "never exceeds limit" cannot
catch fail-closed bugs — pair it with the opposite bound).

Equivalent-mutant note — with a mutation tool, a survivor is not automatically
a failure: some mutants are semantically equivalent to the original and cannot
be killed. Classify such survivors as "equivalent, because <reason>" in
EVIDENCE rather than adding a meaningless test to kill them — that would
violate anti-gaming rule 4. Hand-written mutants (the manual procedure) get no
such excuse: you chose them, so choose real bugs.

### 6. EVIDENCE — the only thing the human reads after code

End with a report the human can trust without opening a single source file
(template in `references/templates.md`):

- The approved spec, with each behavior mapped to the test that verifies it.
- Each gauntlet layer: the command run, and its actual result (pasted numbers,
  not adjectives). "All 47 tests pass, changed-line coverage 100% (31/31 lines),
  5/5 manual mutants killed" — never "tests look good".
- **Every layer resolves to exactly one status**, and the vocabulary is closed:
  `PASSED` · `FAILED` · `N-A (<why this project has no such surface>)` ·
  `UNAVAILABLE (<tool missing / not configured>)` · `SUBSTITUTED (<what was run
  instead> — cannot detect <blind spot>)`. A substitute is never a pass: if the
  instrument the layer specifies never ran, the layer did not find nothing, it
  looked with a different instrument, and EVIDENCE must say what that instrument
  is blind to. `N-A` and `UNAVAILABLE` are also distinct — a project with no
  type checker is not a degraded run, a project whose type checker you skipped
  is.
- The mutation row must carry a **command**, not prose. A score with no
  runnable command beside it is an incomplete row, not a quiet footnote.
- All numbers must come from one final fresh run executed after the last code
  edit — results from mid-task runs are stale and must not be reported.
- The report must be reproducible from the repo alone: every command it cites
  (including the mutation script) must exist as a persisted file in the repo,
  not in a scratch directory or only in the conversation. Reproducible means:
  dev-tool versions pinned or recorded, one entry-point command that reruns
  every layer, and the source state identified (commit SHA, or a source-tree
  hash when git is absent).
- Layers not run as specified, grouped by which of the three non-passing
  statuses they carry (`N-A` / `UNAVAILABLE` / `SUBSTITUTED`), and why.
- **Findings dismissed rather than fixed**, each with the check that disproves
  it (`references/gauntlet.md`).
- **What the gauntlet cost** — wall-clock per layer at minimum. This skill adds
  layers, and the tier map is meant to be tuned by evidence; a layer that costs
  minutes and finds nothing across several tasks is a candidate for demotion,
  but only if somebody wrote the number down. Unmeasured cost makes the tier map
  unfalsifiable.
- **Your structural blind spot** — the layer this project cannot run at all
  (for example, a suite that never exercises the container runtime). Name it in
  every report, not once in a README: knowing which claims are unverifiable is
  what lets a reader judge how far to trust the rest.
- Anything that failed and how it was resolved, honestly. A gauntlet you passed
  on the first try and a gauntlet you fixed your way through are equally fine;
  a gauntlet you quietly weakened is the only failure.

Write it to `EVIDENCE.md` in the task artifact directory beside `SPEC.md`, show
it to the human, and stop — see "Where this skill stops".

**Tracker roll-up**, only if the SPEC named an issue: a short note back to it —
what was built, what was deliberately left undone, traps for the next task, the
artifact path. Never a copy of EVIDENCE; the two have different readers, and
keeping them distinct is what stops them becoming rival sources of truth.
EVIDENCE must be complete for whoever reviews *this* change; the note must be
short for whoever takes the *next* one. Gated by `tracker` — with `propose`,
write the note and let the human post it (`references/templates.md`).

## Anti-Gaming Rules (absolute)

The gauntlet only creates trust if it cannot be gamed. These are hard rules:

1. **Never weaken a test to make it pass.** Don't broaden assertions, add skips,
   raise tolerances, or delete a failing test. If a test seems wrong, that's a
   spec conversation — surface it, don't bury it.
2. **Never edit a test and the implementation in the same step to reach green.**
   Change one, run, then the other. Simultaneous edits let you accidentally
   redefine correctness to match your bug.
3. **Never mock the unit under test** or mock so much that the test only
   exercises the mocks. Mock boundaries (network, clock, filesystem), not logic.
4. **Never chase the coverage number.** Coverage is a detector of untested code,
   not a target. A test added only to touch lines, with no meaningful assertion,
   is gaming — mutation testing exists precisely to catch this, including yours.
5. **Never report a layer you didn't run**, and never let a substitute wear a
   pass. Use the closed status vocabulary above: an honest
   `SUBSTITUTED (2 repeat runs + a 3-module cross-order run — cannot detect
   whole-suite order dependence; pytest-randomly not installed)` preserves
   trust. The same row written as "stable — passed" is a fabricated layer even
   though every number in it is real, because it claims the specified
   instrument found nothing when the instrument never ran.
6. **Failing gauntlet blocks done.** You are not finished while any layer fails.
   If you're genuinely blocked, report the failure verbatim as the outcome.

## Calibration

Scale effort to blast radius, and say which tier you chose:

- **Tier 1 — trivial** (typo, comment, config value): full suite + lint. No new
  tests required, but state why the change is untestable or already covered.
- **Tier 2 — normal** (bug fix, small feature): full loop. Bug fixes MUST start
  with a RED test reproducing the bug — the fix is not done until yesterday's
  bug is tomorrow's regression test.
- **Tier 3 — high stakes** (money, auth, data loss, concurrency, public API):
  start with a short **failure model**: list the ways this specific change can
  hurt (race condition, partial write, hostile input, overflow, unbounded
  growth, failed rollback…), and for each mode add a layer that can actually
  catch it — race/stress tests for concurrency, fuzzing for parsers, rollback
  rehearsal for migrations, benchmarks for latency budgets, API-compatibility
  checks for public libraries, contract tests for service boundaries,
  logging/metric assertions where silent production failure is a mode
  (full menu in `references/gauntlet.md`). Mutation and
  coverage cannot substitute for these; the generic gauntlet is the floor, not
  the ceiling. Then: full loop + property-based tests + mutation testing
  (tool-based if available) + a hostile-input pass against your own
  implementation + **adversarial review by an independent agent**. Failure modes
  deliberately not covered go in EVIDENCE as known limits.

Where the newer layers attach:

| Layer | From |
|---|---|
| Isolation (branch or worktree) | Tier 2 up |
| Integration-tree verification | whenever the isolated and landing trees differ by ignored/untracked content |
| Adversarial review by an independent agent | Tier 3, **or any change to code you did not write** |

## Setup and configuration

Optional per-repo config lives in `.old-coder.toml` — `isolation`, `install`,
`commit`, `commit_args`, `tracker`, `artifacts`, `[commands]`. **Never block on
it.** Absent,
use restrictive defaults (permission keys = `propose`, `isolation` = `auto`,
`artifacts` = `.old-coder`) and mention `references/setup.md` once. It is
gitignored by default so *grants* stay local; a **tracked** copy is honored only
where it tightens (`propose` yes, `allow` and `isolation = "none"` ignored).

**Use the project's configured or detected commands**, not the ecosystem tables
in `references/gauntlet.md` — those are fallbacks for when nothing is found. A
guessed command produces confident, wrong evidence.

The permission rule, once: **an operation proceeds if policy permits it AND (it
is reversible OR an approver is present).** Policy can grant standing
permission; it cannot manufacture a human. Writing tests and running the
gauntlet are reversible and proceed unattended. Installs, commits, and tracker
posts are not: they need the matching key set to `allow`, or an in-task approval.
**With `propose` and no approver present, skip the operation, record the
consequence in EVIDENCE, and continue** — never block on a human who is not
there. A run that halts on configuration produces neither code nor evidence.

**Isolation.** The invariant, not the mechanism: *do not mutate the user's
working tree to do your work, and verify in the tree that will actually receive
the merge.* Default from Tier 2 up; Tier 1 edits in place, which is why Tier 1
is capped at changes whose blast radius is a typo. Branch or worktree — pick
with the detection chain in `references/setup.md`, declare it in the SPEC. The
trap: **a fresh worktree contains no gitignored content**, so the gauntlet often
cannot run there until dependencies are rebuilt. Rebuild, or fall back to a
branch and record why. Never report green from a tree that never ran the suite.

If the project has no test runner, no linter, or no type checking, set up the
minimal standard toolchain for the language **first** (see
`references/gauntlet.md`). A gauntlet can't run on bare ground. Setup changes
the user's environment — packages, config files, lockfiles — so it belongs in
the SPEC's setup plan, where spec approval authorizes it in one step; record
every environment change actually made in the evidence report. If the user
forbids adding tooling, fall back to manual layers (manual mutation, manual
execution) and record the reduced confidence honestly.

If the directory is not a git repository, propose `git init` in the SPEC's
setup plan. Version control is itself a gauntlet layer: commit at SPEC and at
each GREEN/REFACTOR checkpoint, so mutant restores are verifiable with
`git diff` (not by eyeball), a bad refactor is rolled back instead of debugged,
and the final diff shows exactly what changed. Checkpoint commits happen only
under that spec-approved authorization (or an explicit user request) — never
impose a commit cadence on a repo whose owner hasn't agreed to it (`commit`
governs this — see above). Where the repo *mandates* a commit style — signing,
a required trailer — that is `commit_args`, and it is not optional: a commit the
repo's own rules reject is worse than no commit. Detect it at setup and name it
in the SPEC's setup plan (`references/setup.md`).

Checkpoint commits are also **load-bearing for evidence reproducibility**:
EVIDENCE must identify a source state the human can return to and rerun. A
report that names only a dirty working tree becomes unverifiable at exactly the
moment the human is relying on it *instead of* reading the code. If
`commit = "propose"` and the human declines, or git is unavailable, record that
in EVIDENCE — mutant restores then rest on rerunning the suite, a weaker
guarantee — say plainly that the work is uncommitted, and identify the state by
tree hash instead of a SHA.
