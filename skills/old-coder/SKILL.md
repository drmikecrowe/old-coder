---
name: old-coder
description: Evidence-first development — surround the implementation with an executable spec and a gauntlet of constraints (tests, types, coverage, mutation) so line-by-line review becomes optional. Use when the user explicitly asks for high-assurance or evidence-first work ("reliable", "TDD", "prove it works", "I won't read the code"). Also load it when the user did NOT ask but the change touches a high-stakes domain (money, auth, data loss, concurrency, public API, or a hand-rolled parser / config-format reader) — in that case the first and only act is to OFFER the loop in one sentence and stop, so a wrong guess costs a sentence and no files. Work happens in an isolated branch or worktree and ends at an evidence report — this skill never pushes, opens a PR, or publishes, except an optional tracker roll-up, and only where explicitly granted. For routine changes where the user just wants normal tests, write good tests directly instead of invoking this loop.
---

# Old Coder: Reliable Coding Under Constraint and Test

## First: did the human ask for this loop?

This loop is expensive. It starts with a spec file, an approval, and a tools
audit. That cost is correct when the human wants it. It is waste when they want
a small fix.

- **The human asked for it.** They used the skill name, or words like
  "reliable", "TDD", "prove it works", or "I will not read the code". Start at
  step 1 below.
- **The human did not ask, and you loaded this because the change looks
  high-stakes** — money, auth, data loss, concurrency, a public API, or a
  hand-rolled parser or config-format reader. Your
  first act is an OFFER, and it is your only act. Write one or two sentences.
  Name the domain you saw. Give two choices: the full loop, or a normal fix with
  good tests. Then stop and wait.

**Create nothing before the answer.** No artifact directory, no `SPEC.md`, no
tools audit, no branch, no worktree. A wrong guess must cost one sentence, not a
document the human did not want.

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
  not your PATH. Then list, for the human to approve in the same breath as the
  spec:
  - what is already declared and will be run — a configured tool you skip is a
    layer you skipped, not a layer that does not exist;
  - what is missing, as **named tools with one line each on what they would
    catch**, proposed as additions to the project's manifests, pinned;
  - which layers stay `UNAVAILABLE` if the human declines.

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
  spec, so the human can see and veto it before work starts. Under worktree
  isolation the artifact directory spans two locations — tracked files in the
  worktree, gitignored ones (`logs/`) outside it, since nothing gitignored
  survives the worktree's cleanup — unless `artifacts` is an absolute path, which
  makes the whole directory durable at the cost of spec-drift detection
  (`references/setup.md`).

**Intent review — one pass, before the human sees the spec.** Tier 2 up; a Tier 1
change has no spec to misaim. Send `SPEC.md` and the
request *verbatim* to a **fresh subagent with no inherited context** (`spec-intent`, see
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
| Egress: new data paths | secrets and unlimited data that reach an output | For each field, log line, message, or artifact that the change ADDS, name four things: where the data comes from, whether the environment controls it, where it ends up (CI log, JSON, terminal, PR body), and whether it is limited in bytes AND redacted. Coverage and mutation cannot ask whether data *belongs* somewhere. They report only that the line ran. Scan the diff for secrets at rest also, but that is a different question |
| Full test suite | regressions | project's test command, zero NEW failures (baseline note below) |
| Static types | whole classes of bugs | tsc / mypy / etc., zero new errors |
| Lint + format | latent bugs, drift | project's linter, zero new warnings |
| Coverage on changed lines | untested code paths | every changed/added line executed by a test; branch coverage where the tool supports it. Global % is vanity — changed-line coverage is the constraint |
| Mutation testing | tests that assert nothing | the project's mutation tool (mutmut, cosmic-ray, Stryker, PIT…), which generates mutants from the syntax tree. **No tool in the project? Ask for one and report the layer `UNAVAILABLE` until it arrives** — see "Tooling belongs to the project" below. Do not hand-roll a substitute: a script holding hand-written mutants matched against source text is a second copy of the code, and it breaks on every refactor of the thing it is meant to guard |
| Property-based tests | edge cases you didn't imagine | for parsing, math, serialization, anything with invariants (round-trip, idempotence, ordering) — add hypothesis/fast-check properties |
| Complexity budget | unmaintainable output | new functions small and single-purpose; if a function needs a paragraph to explain, split it |
| Parity with the authority | a second implementation that drifts from the first | Whenever the change RE-IMPLEMENTS something that already exists in executable form — a shell pipeline rewritten in Python, a regex ported between languages, a schema restated in code, a rule the build already enforces — the test must **run both and compare outputs on the same inputs**. Never assert the equivalence in prose: a docstring saying "reads the file the way the Dockerfile does" is a claim, and claims are what this skill exists to replace. The comparison must read the authority **from its source at test time**, not from a copy pasted into the test — a copy agrees with your reading forever, including after the original changes. Cannot execute the authority from a test? That is `SUBSTITUTED`, and name what the substitute cannot see |
| Real execution | "passes tests, doesn't run" | actually run the app/CLI/endpoint once on a realistic input, not only the test harness |
| Supply chain & secrets | vulnerable/unnecessary deps, leaked credentials | when the dependency set changed: audit it (pip-audit / npm audit / govulncheck / cargo-audit) and check licenses; scan the diff for secrets; every new dependency must trace back to its SPEC justification. Also eyeball the capability diff: did the change start using network / subprocess / filesystem / env it didn't before? |
| Suite health | flaky or order-dependent tests | run the suite in randomized order (pytest-randomly etc.); repeat suspected flakes. Every EVIDENCE number rests on the suite being deterministic — a flaky suite quietly invalidates the report |
| Integration-tree verification | "green in isolation, broken on merge" | whenever the isolated tree and the tree the change lands in differ by ignored or untracked content, rerun the suite in the landing tree — by **applying the diff uncommitted and reverting**, never by merging, rebasing, or committing there (exact recipe in `references/gauntlet.md`). A green run in a tree that lacks the main tree's `.env`, build outputs, or installed deps is not evidence about the main tree |
| Adversarial review | reasoning that the author cannot audit. **If the change adds or widens an output surface, one reviewer must use a security lens.** An author who picks the lenses omits the category that the author does not fear | the **`adversary` agent, spawned fresh with no inherited context** (bundled with this skill in `agents/`; see "The bundled agents"), briefed to falsify the claim that the change is correct. Where agent definitions are unavailable, a general-purpose subagent carrying that file's body as its brief. Reviews the whole `<base>...HEAD` diff and **binds to that SHA**: any later commit — including your fix for its own findings — drops this layer back to not-run. Procedure, failure-class list, and the two-round limit in `references/gauntlet.md` |

Redirect every layer to its own log under the task's `logs/` dir and read a
bounded slice — `cmd > log 2>&1`, never `tee` (`references/gauntlet.md`).
EVIDENCE cites the log path beside each number, so every claim traces to a run.

**Name the invariant before you correct the symptom.** Write the one sentence that the code must
satisfy. Then test the correction against that sentence, not against the words of the finding. A
symptom-shaped correction passes the new test. It leaves the invariant broken one line away. This is how a loop of six lines takes three review rounds instead of one. The rounds stop
when someone writes "the deadline limits when a probe STARTS, not when a sleep ends".

**Reuse carries the failure mode, not just the signature.** When you call an existing function from
a new context, the types lining up is the easy half. Ask what it does when it FAILS, and whether
that fits where you have just put it. A validator that refuses the whole input is right for a gate
and wrong for a sweep — reuse it in the sweep and one bad record silently discards every good one,
while the call site reads perfectly. Same question for dispatch: **the default branch must be the
safe one, or there must be no default.** `else: <the destructive handler>` is safe only for as long
as nobody adds a case, and it reads as deliberate long after it stopped being true. Prefer an
allow-list that skips what it does not recognise.

**Each finding is a class, not one instance.** When a layer or a reviewer finds a defect, search the
diff for other instances of the same shape before you call it corrected. Also verify that you did
not put back an instance that you corrected earlier. A defect corrected twice and shipped a third
time was three instances of one class that nobody named.

Both rules above are old and both keep getting read past, because a finding arrives wearing the
clothes of one line of code. So they are steps, not sentiments — do all three before any finding is
marked fixed:

1. **Write the class in one sentence**, in the commit or the fix note. Not the symptom
   ("CRLF broke the parser") but the generator ("Python's idea of a line is not the pipeline's").
2. **Search for siblings and record the search.** If the class is "Python and this tool disagree
   about separators", enumerate every separator the two treat differently and test the lot — do not
   fix the one that was reported. An enumeration you can write down is a class you have closed; a
   spot fix is an instance you have closed.
3. **Brief the next review round with the CLASS, not the fix.** A reviewer told "CRLF was fixed"
   re-checks CRLF. A reviewer told "the author has twice confused Python's line-splitting with
   awk's — hunt that" finds the third instance. This is the single cheapest upgrade available to
   the adversarial layer, and it costs one sentence in the prompt.

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
  hash when git is absent).
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

Write it to `EVIDENCE.md` in the task artifact directory beside `SPEC.md`, show
it to the human, and stop — see "Where this skill stops". Give the absolute path
to `EVIDENCE.md`, the same as for `SPEC.md`.

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
  implementation + **adversarial review by an independent agent** (`adversary`). Failure modes
  deliberately not covered go in EVIDENCE as known limits.

Where the newer layers attach:

| Layer | From |
|---|---|
| Isolation (branch or worktree) | Tier 2 up |
| Intent review of the SPEC (`spec-intent`) | Tier 2 up |
| Integration-tree verification | whenever the isolated and landing trees differ by ignored/untracked content |
| Adversarial review by an independent agent (`adversary`) | Tier 3, **or any change to code you did not write** |

## The bundled agents

Two review layers in this loop run as subagents, and they ship with the skill as agent
definitions — `agents/` beside `skills/` in the source repo, installed to your agents
directory (`~/.claude/agents/` or `<project>/.claude/agents/`) alongside the skill:

| Agent | Layer | Tools | Budget |
|---|---|---|---|
| `spec-intent` | Intent review, end of SPEC | `Read` only | ~0 tool calls, one round |
| `adversary` | Adversarial review, in the gauntlet | `Read`, `Bash`, `Grep`, `Glob` | 10 tool calls, one round |

**They are two agents on purpose.** The spec reviewer must not reach the codebase — there is
no implementation yet, and a spec compared against the source instead of the intent always
passes. The code reviewer must reach it and nothing else matters. Merging them produces one
agent that does the heavy review at both stages, which is the failure this split prevents.

**Why the tool lists are short.** A subagent re-reads its entire context every turn, so its
cost is `baseline x turns`, and tool schemas sit in the baseline. Measured on a real
adversarial review: a 26K baseline over 38 turns was 46% of the total bill, for 18 actual
tool calls — roughly twenty turns of deliberation, each paying full freight. Restricting
tools shrinks the baseline; the explicit call budget shrinks the multiplier. Both terms
matter, and the budget is the cheaper win.

**Do not reach for output-shrinking tooling here.** Context-compressing MCP servers, output
filters, and the like target *tool result size* — measured at 3% of the same bill — while
adding schemas to the baseline that get re-read every turn. For a bounded reviewer they cost
more than they save. Give the agent few tools and a hard turn budget instead.

If the host does not support agent definitions, spawn a plain general-purpose subagent and
paste the body of the relevant file in as the brief. The layer is the contract; the agent
file is a convenience.

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
