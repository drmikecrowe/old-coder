---
name: old-coder
description: Surround an implementation with an executable spec and a gauntlet of constraints (tests, types, coverage, mutation) so line-by-line review becomes optional. Load when the user asks for high-assurance work — "reliable", "TDD", "prove it works", "I won't read the code". Load unasked when a change touches money, auth, data loss, concurrency, a public API, or a hand-rolled parser or config-format reader; then offer the loop in one sentence and stop — but only when a reply is possible; an autonomous run records the domain and proceeds under the autonomous rules rather than stalling. Skip it when the user wants ordinary tests — write those directly. Runs in an isolated branch or worktree, ends at an evidence report, and never pushes or opens a PR.
---

# Old Coder: Reliable Coding Under Constraint and Test

## First: was this loop asked for?

This loop is expensive. It starts with a spec file, an approval, and a tools
audit. That cost is correct when it was asked for. It is waste when what was
wanted is a small fix.

- **It was asked for.** The skill was named, or words like "reliable", "TDD",
  "prove it works", or "I will not read the code" were used. **The asker does
  not have to be a live human**: a scheduled wake, a cron job, a loop prompt, or
  another agent's task description that names this skill is the ask, made in
  advance by whoever configured it. Start at step 1 below and do not re-offer
  what has already been requested.
- **Nobody asked, and you loaded this because the change looks
  high-stakes** — money, auth, data loss, concurrency, a public API, or a
  hand-rolled parser or config-format reader. Your
  first act is an OFFER, and it is your only act. Write one or two sentences.
  Name the domain you saw. Give two choices: the full loop, or a normal fix with
  good tests. Then stop and wait.

**An offer needs someone to answer it.** If this is an autonomous or looped run
with no one to reply, do not stop with an offer into an empty room — that stalls
the wake and delivers nothing. Record the domain you saw and run the loop, under
the autonomous-mode rules that already govern it: spec and RED tests are yours
to write, the step-2 approval gate still stands, and EVIDENCE says the spec was
never independently reviewed. OFFER-and-stop is for when a reply is actually
possible.

**A wake re-enters; it does not restart.** Before starting step 1 on a configured
wake, look for this task's artifact directory. An `EVIDENCE.md` with a verdict
means the task is done: report that standing state in one line and stop — a
finished task named again is not a fresh draft. A standing escalation — `FAILED`,
`blocked`, or an abandonment — is a wall, not a queue entry: only a human clears
it, so stop and point at it rather than silently retrying. Whenever you skip for
either reason, say so out loud in one line; to someone watching the wake, silence
reads as a hang.

**Create nothing before the answer.** No artifact directory, no `SPEC.md`, no
tools audit, no branch, no worktree. A wrong guess must cost one sentence, not a
document nobody wanted. This applies to the offer path only — once the loop has
been asked for, by a person or by a configured wake, step 1 starts immediately.

**This offer is not spec approval.** A yes here authorizes the loop only. The
spec still needs its own approval at step 2.

If they choose the normal fix, leave this skill. Write good tests directly. Do
not run a partial version of the loop.

## What you are doing — read this before anything else

Five steps, in order. Do not skip one, reorder them, or run two at once.

1. **WRITE THE SPEC FIRST.** Turn the request into executable acceptance
   criteria — concrete inputs, concrete outputs, and what must not change. Touch
   no implementation file until it exists.
2. **GET THE SPEC APPROVED.** The human approves the spec, never the code. That
   approval authorizes everything after it. Autonomous mode does not skip this
   step. In autonomous mode you can write the spec and the RED tests. **Change
   no implementation file until you have approval.** Tests are reversible
   evidence. The implementation is what the spec authorizes. Record in EVIDENCE
   that you did not get approval.

   **An answer to a question is not an approval.** If you asked the human to
   decide something, they answered that question and nothing else. Their answer
   is an INPUT to the spec. It also CHANGES the spec, so any approval you had
   before the question is now void. Revise the spec, show it again, and ask for
   approval as a separate act. "They picked the options I recommended, so the
   spec stands" is the failure this paragraph exists to stop.
3. **IMPLEMENT THE SPEC, AND TEST INTENT — NOT CODE.** Every test asserts the
   behavior the spec promises, phrased in the spec's terms. A test that asserts
   *how* the code works is a defect: it passes on wrong behavior and cements the
   implementation. **If a behavior-preserving refactor would break the test,
   rewrite the test.**
4. **RUN THE GAUNTLET, ADVERSARIAL REVIEW INCLUDED. FIX EVERY CONFIRMED
   FINDING.** Then run the gauntlet again, before you push. Green means green on
   the final code. A result from before the fixes does not count. A layer you
   skipped on the last pass is a layer that did not run.
5. **WRITE EVIDENCE LAST.** EVIDENCE proves **the finished product implements
   the spec, and why** — every scenario mapped to the proof that it holds. It is
   a report on the product, not on the review. Do not start it while a confirmed
   finding is open, and cite only numbers produced by the final code.

Everything below is the detail of these five. If detail ever seems to license
skipping one, you have misread it.

The human will NOT read your implementation. Their confidence comes entirely from
two artifacts you produce: (1) an **executable specification** they approve before
you write code, and (2) an **evidence report** proving the code ran the gauntlet.
Your job is to make those two artifacts trustworthy enough that line-by-line
review becomes optional within the spec's boundaries.

This inverts the normal review model: **trust moves from inspection to
constraints.** Be honest about what that buys: the gauntlet turns the
constraints the spec expresses into executable evidence — it cannot show the
spec expresses everything that matters, and it is not self-authenticating,
because a checker can be unsound and a mapping can claim more than it
demonstrates. That is exactly why the human approves the
SPEC (the one artifact that breaks the everything-authored-by-the-same-agent
correlation), and why EVIDENCE reports layered, auditable confidence, never
absolute proof. Every shortcut you take against the gauntlet destroys the only
basis of trust.

**Composition with `old-coder-api`:** when both skills apply, this skill owns
workflow order, SPEC approval, the gauntlet, and EVIDENCE; `old-coder-api` owns
the HTTP/JSON contract. Run its scope check and API gates while drafting SPEC,
turn the surviving constraints and risks into acceptance criteria and checks,
then map those checks into EVIDENCE. Do not run two parallel workflows.

## Where this skill stops

**It ends at EVIDENCE.** It writes code, verifies it, and hands the human a
report; they decide what happens next. **It never pushes, and it never opens a
pull request** — not in any configuration, with or without a grant. Those two
are not gated, they are absent.

Two things can be published, both off by default, both writing into a place the
human already made:

- the **tracker roll-up**, posting to an issue when a user-scope rule grants it;
- a **projection** of SPEC or EVIDENCE, when the SPEC declares a destination and
  a user-scope rule grants that surface. A PR projection fills the body of a PR
  the human already opened — draft only, unless a rule says otherwise.

Both default to asking: build the text, write it to the artifact directory, post
nothing.

So with no grants in effect, nothing this skill does is outward-facing and an
unattended run cannot cause external harm. The confidence downgrade for
autonomous mode is therefore about **evidence quality** — the spec was never
reviewed by an independent party — not about blast radius. A tracker grant and a
PR-body grant are what trade that property away, which is why neither is honored
from a committed file — only from your own user-scope rules.

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
- **Collect the invariants that the code states about itself.** Before you invent constraints, read
  what the edit site declares: docstrings, threat-model IDs, existing limits, and nearby guards.
  Carry each one into the spec as a negative constraint. The rule that you are about to break is
  usually written within fifty lines of your change. A rule that the codebase states about itself
  outranks a rule that you inferred.
- Include what the change must NOT do (invariants that must survive: existing
  tests, public API signatures, performance budgets if stated). These negative
  constraints are contract clauses like any scenario: each must end up mapped
  in EVIDENCE to a test, a gauntlet layer, or an explicit skipped-with-reason
  line — never silently absent from the mapping.
- The spec doubles as the authorization point: include the **setup plan** — git
  usage (init? checkpoint commit cadence?), any files the change adds, named
  individually by path, and **every new dependency with a one-line
  justification**
  (prefer the standard library and deps already present; an unjustified
  package is a spec defect) — so approving the spec authorizes the environment
  changes in one step instead of N interruptions, and the human can veto a
  risky package before it is ever installed.
- **Audit the gauntlet's tooling here, in the setup plan, before any code.** Walk
  the layer table and ask of each: *what does this project declare that runs it?*
  Read the manifests (`pyproject.toml`, `package.json`, `mise.toml`, lockfiles),
  not your PATH. **Read the merge gate in the same pass** — `.github/workflows/*`,
  `.gitlab-ci.yml`, `.pre-commit-config.yaml`, the CI target in a Makefile or
  justfile — and transcribe each check into the layer it corresponds to,
  **verbatim, arguments included**. The gate states, one line per tool, the
  command that will judge this change; it is readable before you write a line,
  and reading it afterwards is how a report ends up documenting a scope you chose
  rather than the scope that judges you. **Scope is part of the command:**
  `pyright src/` is not a narrower `pyright`, it is a different check over a
  different set of files, and the difference is invisible in a row that reports
  `0 errors`. Then list, for the human to approve in the same breath as the
  spec:
  - what is already declared and will be run — a configured tool you skip is a
    layer you skipped, not a layer that does not exist;
  - what is missing, as **named tools with one line each on what they would
    catch**, proposed as additions to the project's manifests, pinned;
  - which layers stay `UNAVAILABLE` if the human declines;
  - which gate checks correspond to no layer, and will therefore be run as the
    gate writes them.

  Asking costs one round trip at the point where they are already reading and
  approving. A tool added to the project this way serves every future task in
  that repo and runs in CI; the alternative — discovering the gap mid-gauntlet,
  when a green report is nearly written — is what tempts an agent into building
  its own substitute. Do that audit at SPEC time and the temptation never
  arises.
- Show the spec to the human in plain language and get approval **before writing
  implementation**. **Name every file by its absolute path.** A relative path is
  not clickable in the terminal. Print the full path from the root, so one click
  opens the file. Approval is one explicit act with one subject: the spec.
  These are NOT approval: an answer to a question you asked, a "go ahead" about
  some other step, silence, and the request that started the task. If you cannot
  quote the words that approved THIS spec, you do not have approval.
- **Questions and approval are two different exchanges, in that order.** A
  decision you asked for is an input the spec did not have. Fold each answer in,
  say what changed, show the revised spec, and ask for approval on the new text.
  A spec the human approved BEFORE answering is approval of a document that no
  longer exists.
- In autonomous mode, state the spec in your response and
  proceed — but the correlation-breaking review never happened, so EVIDENCE
  must record `spec approval: not obtained (autonomous run)` and claim
  correspondingly lower confidence; the spec becomes the artifact the human
  reviews after the fact. **Approval recorded in a tracker is the exception** —
  a comment or label from a named human is durable and checkable by someone who
  was not present, so it clears the downgrade where chat approval cannot. Cite
  it (`references/templates.md`). Where the request and the codebase do not
  settle a value the spec needs, do not leave the field empty and do not guess
  silently: write the most reasonable value a careful engineer would propose,
  marked as your proposal, so the after-the-fact reviewer can veto one line
  instead of discovering a hole mid-build. Investigate before you invent — a
  value read from the code beats one you composed.
- The spec is append-only during the task. If implementation reveals the spec was
  wrong, say so explicitly and revise it visibly — never silently drift.
- Open it with an **Orientation** block: the change, why, what it touches, and the calls you
  want the human to rule on. It tells them which scenarios to read closely — it
  does not replace them. Approval is of the scenarios; if the two disagree, the
  scenarios win (`references/templates.md`).
- **The spec is a file, not a message.** Create the task's artifact directory
  now — `<artifacts>/<YYYYMMDD-HHMMSS>-<slug>/`, UTC, one per *task* — and write
  `SPEC.md` there, with a tracker issue ID in the header if one exists (layout:
  `references/setup.md`; template: `references/templates.md`). **Commit it at
  approval** — subject to the commit grant, and only possible if the artifact directory
  is *not* gitignored: once the approved spec is a commit, later drift is
  literally a `git diff`, which makes "append-only" a mechanism rather than a
  promise. Gitignore the directory and that mechanism is gone, not merely
  weakened (`references/setup.md`).
- **Declare the destination in the SPEC, and publish a projection — never move
  the artifact.** `SPEC.md` and `EVIDENCE.md` are written to the artifact
  directory in every configuration; a destination beyond that is a *rendering*
  sent to a tracker or a PR body. Say which in the SPEC's header, beside the
  isolation mechanism, so the human vetoes it at approval rather than inheriting
  it. A published copy carries no `logs/`, binds to no SHA, and stays editable
  after review. Project to a tracker **comment**, never an issue description,
  which is edited in place and reproduces the silent drift the
  commit-at-approval rule exists to prevent (`references/templates.md`).
- Declare the **isolation mechanism** (worktree / branch / none, and why) in the
  spec, so the human can see and veto it before work starts. Under worktree
  isolation the artifact directory spans two locations — tracked files in the
  worktree, gitignored ones (`logs/`) outside it, since nothing gitignored
  survives the worktree's cleanup — unless the artifact root is an absolute path, which
  makes the whole directory durable at the cost of spec-drift detection
  (`references/setup.md`).

**Intent review — one pass, before the human sees the spec.** Tier 2 up; a Tier 1
change has no spec to misaim. Send `SPEC.md` and the
request *verbatim* to a **fresh subagent with no inherited context** (`old-coder-spec-intent`, see
"The bundled agents" below), and ask one question: *if every scenario here passes, does the
human have what they actually asked for?* Three prompts, nothing more:

1. What did the request want that the spec does not cover?
2. What does the spec do that the request never asked for?
3. Where would a reasonable implementer read this spec and build the wrong thing?

**This layer is deliberately light, and keeping it light is the point.** It is not the
gauntlet's adversarial review and must not imitate it: no failure-class hunt, no severity
labels, no line-editing, no reading the implementation — there isn't one yet. Give the
reviewer the request and the spec, not the codebase. One round, no second pass. Prose, a
handful of points at most; a reviewer that returns twenty is doing the wrong job, so say
so in the brief.

Findings are **advisory**. Fold in what is right, revise the spec visibly, and say in one
line what you disagreed with and why. It does not block — the human's approval still
governs — but it runs **first**, so the spec they read is the improved one. Record it in
EVIDENCE as one line: reviewer ran, what it changed. It costs one round trip at the
cheapest moment in the loop, when the only artifact is a document. A spec that is solid
but aimed at the wrong target produces a flawless gauntlet around the wrong feature, and
no later layer catches that — every one of them takes the spec as given.

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
- **Assert the property, not the mechanics you are about to build.** A test
  written next to its own fix drifts toward describing the implementation —
  *two reports were emitted*, *the list had three entries* — instead of the
  thing a human would check: *the message told the truth about what actually
  happened*. Both go green; only the second fails when the code is wrong. This
  is how a test ends up pinning a defect in place, and it bites hardest on
  tests written to close a review finding, where the mechanics are freshest in
  your head and the property is whatever the reviewer was really worried about.
  Write the assertion from the SPEC's wording, before the implementation exists
  to describe.

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

**What this layer is for.** The gauntlet is the adversarial review mechanised:
every independent analysis available, pointed at the change before anyone else
sees it. Its target is concrete — **leave nothing for an external reviewer to
find.** So when a review bot or a human reviewer does find something, the first
question is not "was that finding right" but *which analysis would have caught
it, and why did I not run it?* Usually the answer is a tool the project does not
have yet, or has and you skipped. Both are fixable, and fixing them is how the
gauntlet gets sharper per task instead of staying the same size forever. Record
the answer in EVIDENCE's per-layer yield.

| Layer | What it catches | How |
|---|---|---|
| Merge gate parity | a layer that measured a narrower slice than the thing which will judge the change | map every check the merge gate declares to the layer row that covers it, and run each with the gate's own arguments. A check with no layer runs as the gate writes it. A layer whose command differs from its gate counterpart reports the difference rather than the number alone. Every other layer's scope is self-declared, and a self-declared scope cannot detect its own gap — this is the only layer that can. Where a check cannot run locally (a version matrix, a service container, a secret) the row is `SUBSTITUTED`, naming what the local run does not reach |
| Egress: new data paths | secrets and unlimited data that reach an output | For each field, log line, message, or artifact that the change ADDS, name four things: where the data comes from, whether the environment controls it, where it ends up (CI log, JSON, terminal, PR body), and whether it is limited in bytes AND redacted. Coverage and mutation cannot ask whether data *belongs* somewhere. They report only that the line ran. Scan the diff for secrets at rest also, but that is a different question |
| Full test suite | regressions | project's test command, zero NEW failures (baseline note below) |
| Static types | whole classes of bugs | tsc / mypy / etc., zero new errors |
| Lint + format | latent bugs, drift | project's linter, zero new warnings |
| Coverage on changed lines | untested code paths | every changed/added line executed by a test; branch coverage where the tool supports it. Global % is vanity — changed-line coverage is the constraint. **This layer must exit nonzero when its threshold is missed** (`--cov-fail-under`, `diff-cover --fail-under`, equivalent): a layer that prints a percentage and exits 0 is a report, not a gauntlet layer, and it will sit there green while coverage falls |
| Mutation testing | tests that assert nothing | **Scope is derived, never typed.** The mutated set comes from `git diff --name-only <base>...HEAD`, filtered to source files — not from your sense of where the new logic is. Hand-scoping to the new module leaves the glue unmutated, and the glue is where caller-side defects live. A changed source file the tool cannot mutate is a **named** exclusion in EVIDENCE, never a silent one. Then: **prefer the project's mutation tool** (mutmut, cosmic-ray, Stryker, PIT…), which generates mutants from the syntax tree and cannot silently skip one. No tool available? Manual mutation, per `references/gauntlet.md` — introduce 3–5 plausible bugs one at a time; the suite must kill every one; restore after. A hand-rolled runner must **prove it executed each mutant**: a runner that can report a kill it never ran inflates the score and no red gauntlet will ever surface it |
| Property-based tests | edge cases you didn't imagine | for parsing, math, serialization, anything with invariants (round-trip, idempotence, ordering) — add hypothesis/fast-check properties |
| Complexity budget | unmaintainable output | new functions small and single-purpose; if a function needs a paragraph to explain, split it |
| Parity with the authority | a second implementation that drifts from the first | Whenever the change RE-IMPLEMENTS something that already exists in executable form — a shell pipeline rewritten in Python, a regex ported between languages, a schema restated in code, a rule the build already enforces — the test must **run both and compare outputs on the same inputs**. Never assert the equivalence in prose: a docstring saying "reads the file the way the Dockerfile does" is a claim, and claims are what this skill exists to replace. The comparison must read the authority **from its source at test time**, not from a copy pasted into the test — a copy agrees with your reading forever, including after the original changes. Cannot execute the authority from a test? That is `SUBSTITUTED`, and name what the substitute cannot see |
| Real execution | "passes tests, doesn't run" | actually run the app/CLI/endpoint once on a realistic input, not only the test harness. **Enumerate the entry points the change is reachable from and run one you did NOT develop against** — the path you built on is the path where the code is correct, so a run through it returns green *because* it used the working path. Where the change is reachable only one way, say so in the row; that is a fact about the code, not a pass |
| Supply chain & secrets | vulnerable/unnecessary deps, leaked credentials | when the dependency set changed: audit it (pip-audit / npm audit / govulncheck / cargo-audit) and check licenses; scan the diff for secrets; every new dependency must trace back to its SPEC justification. Also eyeball the capability diff: did the change start using network / subprocess / filesystem / env it didn't before? |
| Suite health | flaky or order-dependent tests | run the suite in randomized order (pytest-randomly etc.); repeat suspected flakes. Every EVIDENCE number rests on the suite being deterministic — a flaky suite quietly invalidates the report |
| Adversarial review | reasoning that the author cannot audit. **If the change adds or widens an output surface, one reviewer must use a security lens.** An author who picks the lenses omits the category that the author does not fear | the **`old-coder-adversary` agent, spawned fresh with no inherited context** (brief bundled inside the skill at `agents/old-coder-adversary.md`; see "The bundled agents"), briefed to falsify the claim that the change is correct — run as a registered agent where the host supports it, otherwise a general-purpose subagent carrying that file's body. Reviews the whole `<base>...HEAD` diff and **binds to that SHA**: any later commit — including your fix for its own findings — drops this layer back to not-run. Procedure, failure-class list, and the two-round limit in `references/gauntlet.md` |

Redirect every layer to its own log under the task's `logs/` dir and read a
bounded slice — `cmd > log 2>&1`, never `tee` (`references/gauntlet.md`).
EVIDENCE cites the log path beside each number, so every claim traces to a run.

**The gate runs before EVIDENCE, not after it.** This layer's target is to leave nothing for an
external reviewer to find, and the merge gate *is* an external reviewer — authoritative, free, and
written down in a file you can read on day one. This skill never pushes, so CI itself cannot be the
thing that runs; run the gate's own commands locally instead, inside the final fresh run
(`references/gauntlet.md`). Consulting the gate after the report is written is the inversion that
makes a scope error survive: at that point the report has already recorded the number your command
produced, and nothing in it says which command it should have been.

**At Tier 3, the final fresh run executes in a fresh agent.** Spawn `old-coder-gauntlet`
(see "The bundled agents") with four inputs — the entry-point command, the artifact
directory, the expected source state, and the layer/gate table from SPEC — and take back
its structured verdict. The run's interpreter then did not write the code, and the raw
logs never enter your context. The runner fixes nothing and reruns nothing; a red verdict
comes back to you. Optional at Tier 2. Where no subagent can be spawned, run it yourself
and record `Gauntlet run by: author` in EVIDENCE — a downgrade, recorded the way the
brief path is.

**Reuse carries the failure mode, not just the signature.** When you call an existing function from
a new context, the types lining up is the easy half. Ask what it does when it FAILS, and whether
that fits where you have just put it. A validator that refuses the whole input is right for a gate
and wrong for a sweep — reuse it in the sweep and one bad record silently discards every good one,
while the call site reads perfectly. Same question for dispatch: **the default branch must be the
safe one, or there must be no default.** `else: <the destructive handler>` is safe only for as long
as nobody adds a case, and it reads as deliberate long after it stopped being true. Prefer an
allow-list that skips what it does not recognise.

**Each finding is a class, not one instance — and the class has to be written as a generator.** A
finding arrives wearing the clothes of one line of code, so a symptom-shaped correction is the
default: it passes the new test and leaves the invariant broken one line away. This rule is old and
keeps getting read past, so it is four steps with an artifact, not a sentiment. Do all four before
any finding is marked fixed:

1. **Write the generator in one sentence**, in the commit or the fix note — the condition that
   *produces* instances, not the shape the reported one happened to have. Not "CRLF broke the
   parser" but "Python's idea of a line is not the pipeline's". Not "`splitlines()` disagrees with
   the shell" but "we open a path that arrived from outside without validating what it is or how
   much of it we read".
2. **Test the sentence: can you enumerate from it, or only search for it?** A generator names a set
   you can list — every call site of this function, every place a value of this kind enters, every
   branch of this dispatch. A symptom names a spelling, and a spelling finds only the instances
   already written the way you remember them. **If the only way to reach a sibling is to grep the
   token out of the finding, you have written the symptom. Rewrite it.** Under a symptom, two call
   sites in different files doing different jobs look unrelated; under the generator they are the
   same line twice.
3. **Produce the enumeration with a command, and put the list in the commit.** One line per site,
   each marked fixed, already-correct, or not-applicable-because — including any site you corrected
   earlier in this branch and have since reintroduced. A list of one site is not an enumeration, it
   is the instance you already had. Carry it into EVIDENCE under `Defect classes closed`
   (`references/templates.md`), where a reader who opens no source file can see how wide the search
   was.
4. **Brief the next review round with the generator and the list**, never with the fix. A reviewer
   told "CRLF was fixed" re-checks CRLF. A reviewer handed the generator and the sites you believe
   you closed hunts the one you missed. This is the cheapest upgrade available to the adversarial
   layer, and it costs one sentence and one list in the prompt.

**The same enumeration closes the seam no layer is aimed at.** When the change alters a function,
list its callers before deciding the tests are sufficient. Tests that drive the function directly
all sit on one side of the seam, and the defect lives in the caller that computes the argument.
Coverage will not find it: coverage asks whether a line ran, never whether anything asserted what
it produced.

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

Checker note — the gauntlet is only as trustworthy as its checkers, and the
dangerous checker failure is fail-open: nothing crashes, the layer prints pass.
Off-the-shelf tools (pytest, mypy, tsc…) have earned their failure behavior;
home-grown checks — grep gates, custom scripts, the manual mutation runner —
have not, so two rules apply to them: (1) **fail closed** — a crash, an
unreadable input, an unexpected exit code, or an item silently skipped inside
gate code is a hard failure of the layer, never a pass; no `|| true`, no
`2>/dev/null`, no bare fallthrough. (2) **Prove it can fail before trusting
its pass**: run it once against a known-bad input (a negative control) and
watch it fail — the RED principle applied to checkers, exactly like the
throwaway mutant for an immediately-passing test. Record the control in
EVIDENCE. Be precise about what that buys: **a negative control proves one
known-bad case reaches the checker's failure path. It does not prove the
checker recognizes every violation of the constraint it claims to enforce.**
A grep gate can fail closed perfectly and still guard a spelling rather than
a behavior. When the gate's coverage is narrower than the rule it serves, say
so where the rule is written, rather than letting the rule imply more.

Prove a negative control is itself non-vacuous the same way you prove a test:
temporarily remove or break the defence it validates, and watch the control go
red. A control that passes with the defence removed is measuring nothing —
this is a one-time proof, not a permanent extra layer.

Equivalent-mutant note — a classification of "equivalent" is where you stop looking. Before you
classify, name the real defect that can exist in that same expression, and search for it. Adjacent
boundary defects live exactly there. With a mutation tool, a survivor is not automatically
a failure: some mutants are semantically equivalent to the original and cannot
be killed. Classify such survivors as "equivalent, because <reason>" in
EVIDENCE rather than adding a meaningless test to kill them — that would
violate anti-gaming rule 4. Hand-written mutants (the manual procedure) get no
such excuse: you chose them, so choose real bugs.

Unreachable-mutant note — **a mutant your harness cannot reach is a design smell, not a footnote.**
When a survivor turns on ambient state the tests cannot vary — the locale, the clock, the platform,
an unset env var — the honest classification is "not equivalent, unkillable here", and the honest
next move is to **delete the degree of freedom rather than describe it**. An implicit dependence on
the environment is almost always a choice: pin the encoding, inject the clock, pass the value. Then
the mutant dies and the paragraph explaining it is unnecessary. Reach for the paragraph only when
the dependence is genuinely inherent. "No test in this process can vary it" is a reason to remove
the variable, not a licence to ship it documented.

#### Tooling belongs to the project — you do not write it

**Run the tools of the project. Ask the human for the tools that it does not have. Never write
your own.** This is the most expensive mistake available in this skill.

A tool that you write looks like diligence and operates like a liability. It is a second copy of the
code, and it breaks each time the original moves. It is the least-verified code in the change. It is
also the instrument that the human reads *instead of* the code. And it **fails open**: a parse that
matches nothing returns an empty set, counts zero defects, and prints **PASS**. That output is
identical to success, but the tool measured nothing.

The rule includes the source of a tool. **A binary on your PATH is not the tool of the project.** The
human, CI, and the next agent cannot reproduce evidence from such a binary. This is the same defect
as a tool that you write, under a more respectable name. If a manifest does not declare it
(`pyproject.toml`, `package.json`, `mise.toml`, lockfile), it is absent.

If a layer has no tool, do these three steps:

1. Name one specific tool, and what it can catch, in one line.
2. Ask the human to add it to the project, pinned.
3. Report the layer `UNAVAILABLE` until it arrives.

An honest gap costs one line in EVIDENCE. A substitute costs a permanent artifact, the defects in
that artifact, and the false confidence that it prints until someone removes it.

A request compounds, because a tool added one time serves each future task in that repo. Before you
report a layer as unavailable, read what the project already declares. "No configuration in
`pyproject.toml`" is not "no linter". A configured tool that you did not run is a layer that you
SKIPPED, not a layer that does not exist.

**Prefer a layer that interrogates the real system to a layer that counts proxies.** One run of the
actual binary, endpoint, or CLI has found real defects. A green suite, complete changed-line
coverage, and a perfect mutation score all reported those defects as absent. Those three can ask
only whether the code does what the tests say. The real system is where the assumptions live.

### 6. EVIDENCE — the only thing the human reads after code

End with a report the human can trust without opening a single source file
(template in `references/templates.md`):

- An **Orientation block at the top**: verdict, what was delivered, what is
  proven, and what is *not* proven. It exists to tell a reader how to read the
  detail, not to replace it. Write it last, read off the tables below it — the
  reader orients from it either way, which is what makes it the place where
  overstating the result pays. The
  tables are authoritative; a summary that disagrees with them is a defect.
  **Before showing EVIDENCE, run the mechanical consistency check in
  `references/templates.md`: `PASSED` only over all-green tables, and every
  non-passed row named in `Not proven:`.**
- The approved spec, with each behavior mapped to the test that verifies it.
- Each gauntlet layer: the command run, and its actual result (pasted numbers,
  not adjectives). "All 47 tests pass, changed-line coverage 100% (31/31 lines),
  5/5 manual mutants killed" — never "tests look good".
- **Each layer resolves to exactly one status**, from this closed list: `PASSED` · `FAILED` ·
  `N-A (<no such surface>)` · `UNAVAILABLE (<tool missing>)` · `SUBSTITUTED (<what ran instead>,
  cannot detect <blind spot>)`. **A substitute is never a pass.** The layer did not find nothing. It
  looked with a different instrument, so name what that instrument cannot see. `N-A` and
  `UNAVAILABLE` are different. A project with no type checker is not a degraded run. A project with
  a type checker that you skipped is a degraded run.
- The mutation row must carry a **command**, not prose. A score with no
  runnable command beside it is an incomplete row, not a quiet footnote.
- **Every layer row names the merge-gate check it mirrors**, or reads
  `no gate counterpart`. Where the command differs from the gate's, the row states
  the difference rather than only the number. This is the one field in the report
  a reader can check without opening a source file, and it is what turns a scope
  error from invisible into obvious.
- All numbers must come from one final fresh run executed after the last code
  edit — results from mid-task runs are stale and must not be reported. The same
  applies to the reviewer: name the SHA the adversarial review actually read, and
  it must be that same final HEAD. Fresh numbers over a stale review is the
  easier half of this rule to satisfy and the more misleading half to get wrong
  (`references/gauntlet.md`).
- The report must be reproducible from the repo alone: every command it cites
  (including the mutation script) must exist as a persisted file in the repo,
  not in a scratch directory or only in the conversation. Reproducible means:
  dev-tool versions pinned or recorded, one entry-point command that reruns
  every layer, and the source state identified (commit SHA, or a source-tree
  hash when git is absent). Where the entry point writes a completion record
  (`references/gauntlet.md`), cite it: the narrative interprets the harness's own
  record of the run, never substitutes for it.
- Layers not run as specified, grouped by which of the three non-passing
  statuses they carry (`N-A` / `UNAVAILABLE` / `SUBSTITUTED`), and why.
- **Findings dismissed rather than fixed**, each with the check that disproves
  it (`references/gauntlet.md`).
- **What the gauntlet cost, and what each layer found.** Give the wall-clock time per layer. Add one
  line per layer that names the defect it caught, or the word `nothing`. This data tunes the tier
  map. A layer that costs minutes and finds nothing over several tasks is a candidate for demotion.
  A cheap layer that repeatedly finds the worst defect has earned a promotion. Cost alone makes the
  tier map unfalsifiable. Cost without yield makes it unimprovable. Even if the honest entry is
  "found nothing", record the data.
- **Your structural blind spot** — the layer this project cannot run at all
  (for example, a suite that never exercises the container runtime). Name it in
  every report, not once in a README: knowing which claims are unverifiable is
  what lets a reader judge how far to trust the rest.
- **Every limitation, filtered first.** Before a known limit goes in the report, ask whether it is a
  property of the world or a property of your own choice. A limit you could close by pinning a
  value, injecting a dependency, or narrowing an interface is **an unfixed defect wearing a
  limitation's clothes** — close it and delete the line. The "known limits" section is the easiest
  place in this report to launder a defect into a disclosure, because writing it feels like rigour.
  The test of whether you got this right comes later and is unambiguous: **when a reviewer files
  something you had already documented, that is a defect you shipped, not a duplicate they missed.**
- Anything that failed and how it was resolved, honestly. A gauntlet you passed
  on the first try and a gauntlet you fixed your way through are equally fine;
  a gauntlet you quietly weakened is the only failure.

**At Tier 3, a fresh scribe drafts the report.** Write your claims first — defect-class
generators, dismissal rationale, honest notes — to `FACTS.md` in the artifact directory,
then spawn `old-coder-evidence` (see "The bundled agents") with the artifacts and take
back the drafted report. The scribe copies numbers and cannot run anything, so a row
without an artifact comes back failed rather than remembered green; `FACTS.md` enters as
labeled claims that never upgrade a status. Optional at Tier 2. Where no subagent can be
spawned, draft it yourself and record `Evidence drafted by: author` — a downgrade,
recorded the way the brief path is.

Write it to `EVIDENCE.md` in the task artifact directory beside `SPEC.md`, show
it to the human, and stop — see "Where this skill stops". Give the absolute path
to `EVIDENCE.md`, the same as for `SPEC.md`.

**Projections**, when the SPEC declared a destination beyond the file: publish a
short rendering — the Orientation block, the source state, and the artifact path — never the
report itself. Derive it from `EVIDENCE.md` and rebuild it whenever the source
state moves; a PR body describing an earlier commit is worse than an absent one,
because nothing tells the reader which commit it describes. Into a PR only if one
is already open, draft unless a rule says otherwise, and gated by a user-scope
grant; **this skill
opens no pull requests in any configuration.** Without a standing grant, or with no PR open,
write the block to the artifact directory and say so — that is the expected
outcome, not a failure (`references/templates.md`).

**Tracker roll-up**, only if the SPEC named an issue: a short note back to it —
what was built, what was deliberately left undone, traps for the next task, the
artifact path. Never a copy of EVIDENCE; the two have different readers, and
keeping them distinct is what stops them becoming rival sources of truth.
EVIDENCE must be complete for whoever reviews *this* change; the note must be
short for whoever takes the *next* one. Gated by the tracker grant — without it,
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
6. **Never label a property that you did not test.** A test name, a docstring, or an EVIDENCE line
   can claim "fails safe", "refuses", "cannot leak", or "is limited". For each such claim, a test
   must supply the unsafe input and report the refusal. A claim attached to a mechanism is not
   evidence about the property. The label also propagates: it reaches EVIDENCE as verified.
   Make it a pass, not a good intention: **before EVIDENCE, reread the prose you wrote in the diff**
   — docstrings, comments, test names — and list every behavioural claim in it. Map each to the test
   that holds it, or delete the claim. The dangerous ones read as description rather than promise
   ("skipped rather than fatal", "never raises", "preserves comments", "reads it the way X does"),
   and they are most often written at the moment you intended the behaviour rather than the moment
   you built it. A docstring that outlives the behaviour it describes is worse than no docstring:
   the next reader treats it as tested.
7. **Failing gauntlet blocks done.** You are not finished while any layer fails.
   If you're genuinely blocked, report the failure verbatim as the outcome.

## Calibration

Scale effort to blast radius, and say which tier you chose:

- **Tier 1 — trivial** (typo, comment, config value): full suite + lint. No new
  tests required, but state why the change is untestable or already covered.
- **Tier 2 — normal** (bug fix, small feature): full loop. Bug fixes MUST start
  with a RED test reproducing the bug — the fix is not done until yesterday's
  bug is tomorrow's regression test.
- **Tier 3 — high stakes** (money, auth, data loss, concurrency, public API, or
  a hand-rolled parser / config-format reader — YAML, TOML, shell, INI, or any
  hand-written scan of a text format, where the failure mode is input the parser
  accepts but the tests never feed it):
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
  implementation + **adversarial review by an independent agent** (`old-coder-adversary`). Failure modes
  deliberately not covered go in EVIDENCE as known limits.
  The hostile-input pass is you attacking your own work and shares your blind
  spots, which is why the `old-coder-adversary` review is separate from it and not
  optional at this tier. Where a spec gap would be expensive on top of that,
  independent verification below is a further and much larger step.

## Two independent reviews, and which one you want

This skill carries two ways to put a fresh pair of eyes on the work, and they
are not interchangeable. Run the first by default; reach for the second only
when the stakes carry its cost.

| | **Adversarial review** (`old-coder-adversary`) | **Independent verification** (VERIFY) |
|---|---|---|
| What it attacks | the diff | the finished work: run, spec, tests, checkers, mapping |
| When | inside the gauntlet, Tier 3 or any change to code you did not write | after the gauntlet, before EVIDENCE is signed, Tier 3 by choice |
| Cost | one agent, 10 tool calls, one round | a protocol with a blind phase and a round cap; ~550k tokens in the one recorded case |
| Is it a gauntlet layer? | yes — bounded, and its verdict binds to a SHA | **no** — prose a human must grade |
| Protocol | `agents/old-coder-adversary.md` (in the skill) | `references/verifier.md` |

They share the rule that matters most, arrived at independently: **a verdict
attaches to the source state that was reviewed, not to the project.** Any later
commit — including the fix for the review's own findings — returns that review
to not-run.

## Independent verification (Tier 3 option, experimental)

The gauntlet is evidence, not self-authentication: its checkers can be
unsound, its mappings can overclaim, and the spec can be incomplete. Human
spec approval mitigates only the last, by breaking author correlation, and
only before code exists — it does not make a spec complete.

Independent verification answers the rest where the stakes justify it: a
fresh-context agent that attacks the finished work before EVIDENCE is signed.
It reduces **task-context** correlation, not model correlation. **It is not a
gauntlet layer** — a layer is an executable check with a machine-evaluable
result; this is an agent returning prose a human must judge, spending the one
resource this skill otherwise guards. Experimental: the evidence is one case study
(`references/verifier-case-study.md` — for deciding whether to run this, not
for the verifier to read), not a benchmark.

**The protocol is `references/verifier.md`. Verification has not been performed
until that file has been read in full and executed; missing or unreadable →
`blocked`, never `passed`.** What cannot be traded away:

- **Fresh context, blind first**, four inputs only — the task contract, the
  approved SPEC, an exact source state, the entry point. Never your
  conversation. The draft EVIDENCE comes after its own results, not before.
- **It fixes nothing.** A SPEC gap goes to the human, never to the builder to
  self-amend.
- **The human grades the findings.** Behavioural findings are fixed and
  re-verified in a new context; description and mapping findings are fixed and
  disclosed without buying another round. Propose a grade if you like — the
  human decides any disputed or material one, and approves stopping at the
  cap. Self-grading is the obvious way to make this rule fail open.
- **Cap at two rounds**, more only by explicit approval. The cap does not limit
  the spending; it makes the spending someone's decision.
- **Verification is source-state-specific.** A state no verifier saw is
  `not performed`, whatever earlier rounds concluded. Fixing a behavioural
  finding after the final permitted round therefore ships an unverified state:
  record that as a declared downgrade and keep the earlier rounds as history.
- **Four states**: `passed` finalizes; `failed` and `blocked` do not;
  `not performed` finalizes only as a declared downgrade, like an unapproved
  spec. On Tier 3 it needs no apology — say so and claim less.

Where the newer layers attach:

| Layer | From |
|---|---|
| Isolation (branch or worktree) | Tier 2 up |
| Intent review of the SPEC (`old-coder-spec-intent`) | Tier 2 up |
| Adversarial review by an independent agent (`old-coder-adversary`) | Tier 3, **or any change to code you did not write** |
| Final fresh run in a fresh agent (`old-coder-gauntlet`) | Tier 3; optional at Tier 2 |
| EVIDENCE drafted by a fresh scribe (`old-coder-evidence`) | Tier 3; optional at Tier 2 |

## The bundled agents

Four layers of this loop run as subagents. The briefs ship **inside** the skill, at
`agents/` beside `references/`, so they are always present wherever the skill is:

| Agent | Layer | Tools | Budget |
|---|---|---|---|
| `old-coder-spec-intent` | Intent review, end of SPEC | `Read` only | ~0 tool calls, one round |
| `old-coder-adversary` | Adversarial review, in the gauntlet | `Read`, `Bash`, `Grep`, `Glob` | 10 tool calls, one round |
| `old-coder-gauntlet` | Final fresh run, end of the gauntlet | `Read`, `Bash`, `Grep`, `Glob` | 1 entry-point run + 15 tool calls, one round |
| `old-coder-evidence` | EVIDENCE draft, step 6 | `Read`, `Grep`, `Glob`, `Write` | 25 tool calls, one round |

**They are separate agents on purpose.** The spec reviewer must not reach the codebase —
there is no implementation yet, and a spec compared against the source instead of the intent
always passes. The code reviewer must reach it and nothing else matters. The gauntlet runner
can execute and must not fix; the evidence scribe can write and must not execute — a scribe
with no `Bash` cannot produce a number, only transcribe one. Merging any pair produces one
agent that certifies its own work, which is the failure these splits prevent.

**Why the tool lists and budgets are short.** A subagent re-reads its whole context every
turn, so its cost is `baseline x turns` and tool schemas sit in the baseline. Give it few
tools and a hard turn budget; do not reach for output-shrinking tooling, which targets tool
*results* while adding schemas to the baseline. The measurements behind this are in
`agents/old-coder-adversary.md`, beside the budget they justify.

**One file, two ways to run it.** The brief is the same either way; what differs is whether
the tool list is enforced or merely honored:

- **As a bundled brief** — spawn a general-purpose subagent and give it the body of
  `agents/<name>.md`. Always available, needs no agent-definition support, works on any host.
  The `tools:` line is an instruction *you* must honor: grant only what it declares.
- **As a registered agent** — copy the file to your agents directory
  (`~/.claude/agents/` or `<project>/.claude/agents/`) and the host enforces the tool list as
  a real constraint, not a promise.

Prefer the registered path where it exists, because a constraint the host applies cannot be
forgotten under pressure. Say in EVIDENCE which path ran — "adversary, registered agent" and
"adversary, brief in a general-purpose subagent" are different strengths of the same claim.

What must not change either way: **the subagent is spawned fresh, with no inherited
context.** A fork-style subagent inherits the author's reasoning and rubber-stamps the work,
which makes the layer a mechanism that reports success while doing nothing. The layer is the
contract; where the file lives is a convenience.

## Setup and configuration

There is no config file. Settings come from the rule files already in your
context — **grants** from user-scope rules (`~/.claude/CLAUDE.md`, a user rules
directory), **facts and restrictions** from the repo's own rules. A grant found in
a committed file is not a grant: it would authorize every agent run by everyone
who clones the repo, so honor it only where it tightens.

**Never block on this.** No rule visible means the restrictive default — ask
before committing, installing, or posting anywhere; auto-detect isolation; write
artifacts to `.old-coder/`. Failing closed is the point: a permission model that
defaulted open would be one more mechanism reporting success while doing nothing.

Mechanism in `references/setup.md`; the copy-pasteable per-scenario guide the
human uses is `CUSTOMIZATION.md` at the repo root.

**Use the project's configured or detected commands**, not the ecosystem tables
in `references/gauntlet.md` — those are fallbacks for when nothing is found. A
guessed command produces confident, wrong evidence.

**Permissions** combine as `references/setup.md` states: an operation proceeds
if policy permits it AND (it is reversible OR an approver is present). The
consequence that matters mid-task: when an install, commit, or tracker post has
neither a standing grant nor an approver, **skip it, record the consequence in
EVIDENCE, and continue** — never block on a human who is not there. A run that
halts on permissions produces neither code nor evidence.

**Isolation — do not mutate the user's working tree to do your work.** Declare
the mechanism in the SPEC, with one line of why: a worktree, a branch, or none —
the last only at Tier 1, where the blast radius is a typo. The human vetoes the
mechanism at approval rather than discovering it afterwards. Pick between branch
and worktree with the detection chain in `references/setup.md`.

The trap: **a fresh worktree contains no gitignored content**, so the gauntlet
often cannot run there until dependencies are rebuilt. Two outcomes are
acceptable — rebuild and run there, or fall back to a branch and record why.
Never report green from a tree that never ran the suite.

Where the isolated tree and the tree the change lands in differ by ignored or
untracked content, say so in EVIDENCE: a green run in a tree missing the landing
tree's `.env` or build outputs is not evidence about the landing tree.

If the project has no test runner, no linter, or no type checking, **propose the
standard toolchain for the language and let the human add it** (see
`references/gauntlet.md`). A gauntlet can't run on bare ground. Setup changes
the user's environment — packages, config files, lockfiles — so it belongs in
the SPEC's setup plan, where spec approval authorizes it in one step; record
every environment change actually made in the evidence report.

Add it to a manifest, pinned. Never add it only to your machine. **If the human
declines, the layer is `UNAVAILABLE`. Full stop.** Do not substitute a tool that
you write. *Tooling belongs to the project* above gives this same rule and its
reasons.

If the directory is not a git repository, propose `git init` in the SPEC's
setup plan. Version control is itself a gauntlet layer: commit at SPEC and at
each GREEN/REFACTOR checkpoint, so mutant restores are verifiable with
`git diff` (not by eyeball), a bad refactor is rolled back instead of debugged,
and the final diff shows exactly what changed. Checkpoint commits happen only
under that spec-approved authorization (or an explicit user request) — never
impose a commit cadence on a repo whose owner hasn't agreed to it (the commit grant
governs this — see above). Where the repo *mandates* a commit style — signing,
a required trailer — that mandate is not optional: a commit the
repo's own rules reject is worse than no commit. Detect it at setup and name it
in the SPEC's setup plan (`references/setup.md`).

Checkpoint commits are also **load-bearing for evidence reproducibility**:
EVIDENCE must identify a source state the human can return to and rerun. A
report that names only a dirty working tree becomes unverifiable at exactly the
moment the human is relying on it *instead of* reading the code. If
there is no commit grant and the human declines, or git is unavailable, record that
in EVIDENCE — mutant restores then rest on rerunning the suite, a weaker
guarantee — say plainly that the work is uncommitted, and identify the state by
tree hash instead of a SHA.
