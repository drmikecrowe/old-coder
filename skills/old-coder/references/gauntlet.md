# Gauntlet Tooling by Ecosystem

## Configured commands beat guessed ones

Command resolution has a strict order:

1. **Commands named in the project's rules** (see `setup.md`) — always win.
2. **The merge gate** — the CI workflow, pre-commit config, or CI target that
   decides whether this change may land. See the next section: it outranks
   generic detection because it is the command that will judge the change.
3. **Detection** — package.json scripts, Makefile targets, pyproject, justfile.
4. **The tables below** — fallbacks, used only when 1–3 find nothing.

Treat the tables as last resort, not as prescription. A project's real test
command usually encodes setup the raw tool call skips: virtualenv selection,
per-branch environments, required flags, service fixtures. And many repos
forbid the exact invocation a table suggests — a repo standardized on `pnpm`
will reject `npx`. Guessing does not fail loudly; it produces confident, wrong
evidence, which is the one failure mode this skill exists to prevent.

## The merge gate is the other reviewer, and it is readable on day one

Every gauntlet layer reports on what it ran. Nothing in the gauntlet checks what
a layer *should* have run — a self-declared scope cannot detect its own gap, and
the number in the row is true either way. The merge gate closes that hole,
because it states the intended scope in a file, before any code exists.

**Find it and transcribe it at SPEC time**, in the tooling audit:
`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/config.yml`,
`.pre-commit-config.yaml`, a `ci` / `check` target in a Makefile or justfile, or
whatever the repo's rules name as required. Write down each check as the gate
writes it, arguments included, and map it to the layer it corresponds to.

**Scope is part of the command.** `pyright src/` is not "`pyright`, narrowed" —
it is a different check over a different file set, and a row reading
`pyright src/ | 0 errors | PASSED` is fully true while nine errors sit in
`tests/`, which the gate checks and the row did not. The same holds for
`ruff check src tests` against a gate's `ruff check src tests tools`. Compare the
argument lists, not the tool names.

**Run the gate's commands, in the final fresh run, before EVIDENCE is written.**
`tools/gauntlet.sh` is where they go, so the entry point is a superset of the
gate rather than a second opinion beside it. Then each EVIDENCE row carries the
gate check it mirrors:

- **Same command** — cite the gate job name in the row's `Gate` column.
- **Different command** — state the difference in the row. A deliberate
  difference (the gate runs a matrix; you ran one version) is a `SUBSTITUTED`
  row naming what the local run does not reach. An accidental one is a defect
  you just caught for free.
- **No gate counterpart** — write `no gate counterpart`. Mutation, property
  tests, and adversarial review usually have none; that is expected and worth
  seeing, because it says which of your evidence nothing external will re-check.
- **A gate check with no layer** — run it as written and give it its own row. A
  docs build, a changelog check, or a schema validation gets no attention from
  any layer in this skill and fails just as loudly.

**Where the gate cannot run locally** — a service container, a secret, a
platform you are not on — do not silently drop it. The row is `UNAVAILABLE` or
`SUBSTITUTED` with the reason, and it belongs in EVIDENCE's `Not proven:`. The
point is not that every gate check runs; it is that no gate check is missing
without a reader being told.

This skill never pushes, so CI is never the thing that runs here. The gate's
*text* is the artifact being used, and it is available from the first minute of
the task.

## Python

| Layer | Tool | Command |
|---|---|---|
| Tests | pytest | `pytest -q` |
| Types | mypy | `mypy <pkg>` (or pyright) |
| Lint + format | ruff | `ruff check . && ruff format --check .` |
| Changed-line coverage | coverage.py | `pytest --cov=<pkg> --cov-branch --cov-report=term-missing --cov-fail-under=<n>` — without the threshold flag the layer prints a number and exits 0, so it can never fail; `diff-cover coverage.xml --fail-under=100` gates changed lines specifically |
| Mutation | mutmut (3+) | configure `[tool.mutmut] source_paths = ["src/"]` in pyproject.toml, then `mutmut run` (target one module with `mutmut run "my_module*"`); survivors = weak tests |
| Property-based | hypothesis | `@given(...)` strategies for invariants |

## JavaScript / TypeScript

| Layer | Tool | Command |
|---|---|---|
| Tests | vitest / jest | `npx vitest run` / `npx jest` |
| Types | tsc | `npx tsc --noEmit` |
| Lint | eslint | `npx eslint .` |
| Changed-line coverage | vitest/jest coverage | `npx vitest run --coverage` (v8, per-file report); check touched files |
| Mutation | Stryker | `npx stryker run` (scope with `mutate: [<changed files>]` — full-project runs are slow) |
| Property-based | fast-check | `fc.assert(fc.property(...))` |

## Go

| Layer | Tool | Command |
|---|---|---|
| Tests | go test | `go test ./... -race` |
| Types | compiler | `go build ./...` |
| Lint | go vet + staticcheck | `go vet ./... && staticcheck ./...` |
| Coverage | built-in | `go test -coverprofile=c.out ./... && go tool cover -func=c.out` |
| Mutation | (no mature default) | manual mutation |
| Property-based | testing/quick or rapid | `rapid.Check(t, ...)` |

## Rust

| Layer | Tool | Command |
|---|---|---|
| Tests | cargo | `cargo test` |
| Types | compiler | `cargo check` |
| Lint | clippy | `cargo clippy -- -D warnings` |
| Coverage | llvm-cov | `cargo llvm-cov --branch` |
| Mutation | cargo-mutants | `cargo mutants --file <changed file>` |
| Property-based | proptest | `proptest!` macros |

## Java

| Layer | Tool | Command |
|---|---|---|
| Tests | JUnit 5 via Maven / Gradle | `./mvnw test` / `./gradlew test` |
| Types | javac via Maven / Gradle | `./mvnw compile` / `./gradlew classes` |
| Lint + format | Checkstyle + Spotless | `./mvnw checkstyle:check spotless:check` / `./gradlew check spotlessCheck` |
| Changed-line coverage | JaCoCo | `./mvnw verify` / `./gradlew test jacocoTestReport`, then inspect the XML/HTML report for touched lines and branches |
| Mutation | PIT | `./mvnw test-compile org.pitest:pitest-maven:mutationCoverage` / `./gradlew pitest`; scope changed packages or classes |
| Property-based | jqwik | write `@Property` tests; the normal JUnit test command runs them |

## Scala

| Layer | Tool | Command |
|---|---|---|
| Tests | MUnit / ScalaTest via sbt | `sbt test` |
| Types | Scala compiler | `sbt "compile" "Test / compile"` |
| Lint + format | Scalafix + Scalafmt | `sbt scalafmtCheckAll "scalafixAll --check"` |
| Changed-line coverage | scoverage | `sbt clean coverage test coverageReport`, then inspect the report for touched statements and branches |
| Mutation | Stryker4s | `sbt stryker`; scope `mutate` to changed source files when the full project is slow |
| Property-based | ScalaCheck | define `Properties` or framework-integrated properties; `sbt test` runs them |

## SQL

SQL has no portable test runner or type checker. Configure the actual dialect,
use the project's migration/query framework, and validate against a disposable
instance of the same database engine used in production.

| Layer | Tool | Command |
|---|---|---|
| Tests | project/database-native tests | run the project's test command (`dbt test` for dbt), including migrations, constraints, and result-set assertions |
| Parse + schema checks | SQLFluff + target database | `sqlfluff parse --dialect <dialect> <changed.sql>`, then prepare, explain, or execute each changed statement against the disposable database |
| Lint + format | SQLFluff | `sqlfluff lint --dialect <dialect> .`; apply rule fixes with `sqlfluff fix` (`sqlfluff format` handles layout only) |
| Changed-statement coverage | spec-to-test mapping | map every changed statement, predicate branch, constraint, and migration direction to an integration test; record any unexercised item |
| Mutation | manual | use the manual procedure below to alter predicates, joins, aggregates, constraints, and migration steps; every mutant must fail a test |
| Property-based | host-language generator + target database | generate rows and assert schema, query, and round-trip invariants through the project test runner |

## Emacs Lisp

| Layer | Tool | Command |
|---|---|---|
| Tests | ERT | `emacs -Q --batch -L . -l ert -l <test-file> -f ert-run-tests-batch-and-exit` |
| Compile checks | byte compiler | `emacs -Q --batch -L . --eval '(setq byte-compile-error-on-warn t)' -f batch-byte-compile <files>` |
| Lint | package-lint + checkdoc | run `package-lint-batch-and-exit` and `checkdoc` in batch mode over every changed `.el` file |
| Changed-form coverage | testcover / undercover.el | instrument changed files in the batch ERT runner and verify every touched form is exercised |
| Mutation | no mature default | use the manual mutation procedure below on changed defuns and run the ERT suite for each mutant |
| Property-based | deterministic ERT generators | generate inputs in an `ert-deftest`, pin the random seed, and assert invariants |

## Extended layer menu (any ecosystem)

Always-on layers live in SKILL.md's table; these are picked per task by the
Tier 3 failure model (or when the domain plainly calls for them).

| Layer | Tools | When |
|---|---|---|
| Dependency audit | pip-audit / npm audit / govulncheck / cargo-audit | whenever the dependency set changed |
| License check | pip-licenses / license-checker / go-licenses / cargo-license | when adding deps to redistributable code |
| Secret scan | gitleaks (language-agnostic) | on the diff before committing |
| Capability diff | manual diff review, or semgrep rules | always cheap: did the change start using network / subprocess / filesystem / env vars it didn't before? An agent-added capability nobody asked for is a red flag |
| Suite health | pytest-randomly (py) / `vitest --sequence.shuffle` (ts) / `go test -shuffle=on` / `cargo test -- --shuffle` (nightly) | randomized order per run; repeat suspected flakes |
| API compatibility | griffe (py) / api-extractor (ts) / apidiff (go) / cargo-semver-checks (rust) | when a public API is touched |
| Concurrency | `go test -race` / ThreadSanitizer (C/C++/Rust) / loom (rust) / threading stress + rerun (py) | Tier 3, when the failure model names races |
| Performance | pytest-benchmark / hyperfine / criterion | only when the spec states a budget |
| UI checks | axe-core (accessibility) / Playwright screenshot diff (visual regression) / Lighthouse (perf & a11y budgets) | when the change touches user-facing UI — backend layers say nothing about a broken layout or an unreadable contrast |
| Version matrix | tox / nox / CI matrix | when the project claims support for multiple language or platform versions — one version green is not evidence for the others |
| Observability | assert critical paths emit logs/metrics (capture in tests or grep) | when the failure model includes "fails silently in production" — passing all tests but breaking invisibly is still a failure |

New dependencies are a SPEC matter first, a tool matter second: each one needs
a one-line justification in the setup plan, and EVIDENCE records the final
dependency diff so the human can see exactly what the agent pulled in.

## Egress: what the change lets data reach

A layer the counting layers cannot cover. Coverage and mutation ask whether a line RAN and whether a
test would notice it changing. Neither can ask whether the data on that line *belongs* where it now
goes.

Run it whenever the diff **adds or widens an output surface** — a report field, a log line, an error
message, an API response, an artifact, a PR body. For each one:

1. **Origin.** Where does the value come from? Constant, user input, environment, or another
   process's output? Child-process output is the dangerous case: it is unbounded and you do not
   control what it prints.
2. **Control.** Can an attacker or the environment influence it? Credentials arriving via env are
   the common path — a crashing child prints its own configuration.
3. **Destination.** Where does it end up? A CI log and a PR body are PUBLIC. `--json` consumed by
   CI means anything in that JSON is world-readable for repos that are.
4. **Bounds and redaction.** Is it capped in BYTES (not just lines) and are secret shapes removed?
   `tail -n 200` bounds neither a single 4 MB line nor a token.
5. **Precedent.** Does the codebase already solve this for a sibling surface? A neighbouring
   constant like `MAX_DETAIL = 120` with a comment about secrets is the codebase telling you the
   rule; matching it beats inventing a second, weaker mechanism.

**Removing the channel beats redacting it.** Best-effort redaction holds until it does not. If the
value of the data is diagnostic, prefer a POINTER — name the file and how to read it — over a copy.
Say plainly in EVIDENCE what diagnosability that costs; a stated cost is a decision, an unstated one
is an oversight.

## Adversarial review by an independent agent

Self-review has the same correlation problem the rest of this skill works to
break: the author knows why the code is right and will find reasons it is.
Tier 3 changes, and **any change to code the author did not write**, get a
review from an agent that shares none of that reasoning.

This is the bounded, in-gauntlet review: it attacks **the diff**, costs one
agent and ten tool calls, and returns a verdict bound to a SHA. It is not the
same thing as independent verification (`verifier.md`), which attacks the
finished work — run, spec, tests, checkers, and mapping — is deliberately not a
gauntlet layer, and costs orders of magnitude more. Run this one by default;
reach for that one when a spec gap would be expensive. SKILL.md § "Two
independent reviews" has the comparison.

**Use the `old-coder-adversary` brief, in a subagent spawned fresh with no inherited
context.** It ships inside this skill at `agents/old-coder-adversary.md` and already carries
the hunting order, the tool restrictions, and the call budget — do not re-brief it
from scratch, and do not hand it a wider toolset than it declares.

**Four task-specific inputs, and the last two are the ones usually forgotten:**

1. the base SHA of the diff, and the lens;
2. the failure **class from the previous round, as its generator sentence**, plus
   the enumeration you produced and the sites you believe you closed — a reviewer
   given the fix re-checks the fix; a reviewer given the generator and your list
   hunts the site missing from it;
3. **the layer commands you ran and the merge gate's own text** (or its path), so
   the reviewer can answer *do these commands match the gate?* Nothing else in
   this skill asks that question of an adversary, and it costs one `Read`;
4. **the list of functions the diff changed**, so the reviewer can enumerate
   callers rather than spend its budget rediscovering them.

A reviewer pointed at code cannot audit the evidence about that code unless you
point it there.

Two ways to run it, and EVIDENCE should say which:

- **As a registered agent** — the file copied to your agents directory, where the
  host enforces `tools:` as a real constraint.
- **As a bundled brief** — spawn a general-purpose subagent and give it that
  file's body. Always available, since the file ships with the skill. Here the
  tool restriction is an instruction you honor rather than a constraint the host
  applies, so grant only the tools it declares. Do **not**
use a "fork"-style subagent that inherits the parent conversation — it inherits
the author's justification for the design and will rubber-stamp it. Breaking
that correlation is the entire point of this layer.

**Assign lenses; do not let the author choose them freely.** A single reviewer briefed on
"correctness" will hunt the category its author already worries about, and the whole class the
author is *not* worried about goes unreviewed. Run reviewers with distinct, named lenses, and:

- **Security/privacy is MANDATORY whenever the change adds or widens an output surface** (the egress
  layer above tells you when that is). It is the category authors most reliably omit.
- Add lenses matched to the change: concurrency, failure/rollback, performance budget, API
  compatibility, does-it-reproduce.
- A finding a reviewer confirms is a finding about a CLASS. Before calling it fixed, search the diff
  for other instances of the same shape — including ones you fixed earlier in the same branch and
  have since reintroduced.

Brief each reviewer to **falsify**, not to review:

> Your job is to falsify the claim that this change is correct.

Give it the diff, the SPEC, and this named list of failure classes to hunt:

- behavior drift in anything presented as a pure move or rename
- tests that assert a refactor happened rather than asserting behavior
- tests that would still pass if the function under test returned a constant
- test doubles that no longer bind to the executing call site
- credential handling — construction, logging, storage, transport
- state read before it is initialized
- import cycles introduced by the change
- names the change invokes that may not exist — a method, flag, config key, or version
  constraint remembered rather than checked. Worth a lens only where the type checker and
  the suite are blind: dynamic dispatch, string-keyed config, CLI flags in shell scripts,
  and APIs that exist only above the pinned version.

<!--
  The class above is adapted from the "hallucination audit" vector of the
  `adversarial-agent-review` skill v1.0.1 (Apache-2.0):
  https://lobehub.com/skills/sharp-skills-skills-adversarial-agent-review?activeTab=skill
  Its other six vectors are already covered by the lenses and failure classes here.
  Its framing ("failure = saying looks good") was deliberately not adopted: it rewards
  fabricated findings, which anti-gaming rule 5 forbids.
-->


Require each finding to carry:

- `file:line`
- a concrete scenario: specific inputs → the specific wrong output or crash
- a verdict of **CONFIRMED** or **PLAUSIBLE**

**The author triages; the reviewer is not the authority.** Verify every claim
against the code before acting on it. Reviewers do report things that are simply
wrong, and saying so with evidence — quoting the code that refutes the finding —
is part of doing this layer properly, not a way of dodging it.

### Dismissing a finding costs more than fixing one

This is the one place the trust model has no backstop: the author grades their
own homework and the reviewer never gets a second look. Fixing a finding is
self-evidencing — the diff and the rerun show it. Dismissing one produces
nothing but prose written by the person the finding was about. So a dismissal
carries a higher burden of proof than a fix:

- **Cite the specific check that disproves it** — a command and its output, a
  `file:line` that contradicts the claim, or the name of the test that already
  covers the case. "I looked and it is fine" is not a dismissal, it is a
  refusal. (A good one, from a real run: a finding claimed a helper was dead
  code; the author named the test that calls it. That is checkable in seconds
  by anyone.)
- **A dismissal resting on "no better alternative exists" must argue it per
  call site**, not for the class. "A behavioral test would have to execute a
  path that ends in `exec`" can be true of one call site and false of its
  neighbour — and if it is false anywhere, the dismissal is wrong there. Walk
  each site; say which ones the argument actually covers.
- **Downgrade, don't dismiss, when the argument only partly holds.** Accepting
  a weaker test as a known limit is legitimate; recording it as a limit and as
  a defensible-for-now choice is honest. Recording it as refuted, when the
  reviewer was right and the fix was merely inconvenient, is the failure mode.
- **An unfalsifiable dismissal is a CONFIRMED finding you did not fix.** If you
  cannot state what observation would show the reviewer right, you have not
  refuted anything — carry it into EVIDENCE's known limits with that status.

**Re-run the gauntlet after resolving CONFIRMED findings.** A review fix is a
code change like any other: every EVIDENCE number must come from a run that
post-dates it. "2 CONFIRMED (all resolved)" above a test count from before the
fixes is exactly the stale-number failure the final-fresh-run rule exists to
prevent.

### A review is a claim about a commit, not about a change

Re-running the gauntlet keeps the *numbers* fresh. It does nothing for the
*review*, which goes stale the moment you commit again — and the rule above is
easy to satisfy while leaving the review stale, because measurements are cheap
to repeat and a reviewer is not.

So bind the review to a commit:

- **Review the whole delivered diff** — `<base>...HEAD`, the range the pull
  request will show — never a single commit, never a subset. Checkpoint commits
  are encouraged elsewhere in this skill; they are not review units.
- **Record the reviewed SHA in EVIDENCE**, beside the layer:
  `Adversarial review | PASSED | reviewed <sha>`.
- **The layer is `PASSED` only while that SHA is HEAD.** Commit afterwards — for
  any reason, including fixing the review's own findings — and the layer drops
  to not-run until a reviewer has seen the new head. If you stop there, say so:
  `SUBSTITUTED (reviewed <sha>; <n> later commits unreviewed — <what they
  changed>)`. An unreviewed head commit is not a bookkeeping detail; it is the
  part of the change nobody has attacked.

**Fixes for findings are the most dangerous code in the change.** They are
written quickly, under the impression that this area has already been thought
about, and they land last — after the layer that would have caught them has
finished. A reviewer's diagnosis is evidence about the *bug*; it says nothing
about your *fix*. So treat every finding-fix as new code: RED test first, then
re-review.

The re-review is usually cheap. Send the follow-up diff back to **the same
reviewer** — it already holds the context and can answer the one question it is
best placed to answer: does this fix actually address what I found? Use a
*fresh* reviewer instead when the fix changed the design rather than patching
it, because at that point the shipped design is not the one anybody attacked.

**On the final permitted round, narrow the work to the blocking finding.** Fix
only it, and brief the reviewer with only it. A last round spent across the whole
diff can close cosmetics while the blocker stands, and no round remains to catch
that. If
EVIDENCE has been drafted by the time a re-review round runs, include it in the
diff the reviewer sees — the summary-versus-tables check in its brief is
unreachable otherwise.

Watch for the same staleness in the prose. When a fix or a SPEC revision
supersedes a mechanism, the docstrings, comments, and helper names describing
the old one do not update themselves, and they are the part of the diff a green
suite says nothing about. Sweep the whole change for the superseded mechanism's
name before calling it done.

**Grade each finding before it buys a round, and the human does the grading.**
A finding is either **behavioural** — the code does the wrong thing, or a gate
cannot fail — or **description/mapping**: the spec, a comment, or EVIDENCE says
something untrue about code that is correct. Behavioural findings are fixed and
re-reviewed. Description findings are fixed and disclosed, and buy no round.
Propose a grade if you like; the human decides any disputed or material one.
Left to self-grading this fails open in the obvious way — call a boundary defect
a documentation defect and the round is avoided. It matters most when the
finding touches the SPEC, where the real question is whether the document is
wrong about correct code or has exposed a requirement nobody wrote down, and
that is the human's call by the same rule that sends SPEC gaps to the human.

Without the split, "fix every finding" times "re-review after any change" has no
stopping condition short of a round that returns the empty set, and prose has no
such fixpoint. Be clear about the trade: grading buys termination by giving up
completeness, and a behavioural gap can live inside a round you chose not to
run. Say in EVIDENCE which rounds were not run.

### A reviewer's "did not reach" list is work, not a footnote

Every reviewer under this brief ends with what it did not get to. That line is
the most useful sentence in the report and the easiest to discard, because it
arrives attached to findings that feel like the result.

- **Copy it into EVIDENCE verbatim**, under the review row. Each unreached item
  is an open item: either you cover it another way and say which layer did, or it
  stands as a named gap a reader can weigh.
- **Record the tool calls used.** A reviewer that stopped at 9 of 10 calls stopped
  because it ran out of budget, not because it ran out of defects. **Two rounds
  that both exhausted their budgets are not two rounds converging** — treat the
  agreement between them as worth exactly as much as the ground they both
  covered, which the unreached lists tell you. Convergence is a signal only when
  a round finished early with findings left unfound.
- **A round that ended with budget to spare and no findings is the real
  convergence signal.** Say which kind you got; the two read identically in a
  report that records only the findings.

**Two rounds maximum.** If a second round still finds CONFIRMED problems, the
change is too entangled to be verified this way: abandon it and take a smaller
cut. That is a legitimate outcome, not a failure of nerve. Report it in EVIDENCE
as `Adversarial review | abandoned after round 2 | <findings that drove it>`,
with every other layer marked `n-a: change abandoned` — an abandoned change has
no green result to report, and must never be written up as one.

### What this layer cannot prove

Be honest about it in EVIDENCE, because it is the one layer with no independent
artifact. Every other layer's log is written by a tool; `logs/review.log` is
written by **you**, summarizing a reviewer the human never saw. A fork-based
reviewer, or no reviewer at all, produces text indistinguishable from an honest
run. So:

- Record the reviewer's **model and agent type** in EVIDENCE, not just the word
  "independent" — a claim specific enough to be wrong is worth more than one
  that is not.
- Say plainly in EVIDENCE that this layer rests on self-report, so a reader
  weights it below the tool-generated layers and can ask for the reviewer's
  full transcript when the findings matter.
- Anti-gaming rule 5 applies with full force: an invented review is a fabricated
  layer, and fabricating this one is easier than fabricating any other.

### Fix what you wrote; file what you moved

When review finds a latent bug in code the change only *relocated*, file it as
follow-up work — do not fix it inside a change that claims to be
behavior-preserving. Mixing the two costs the reviewer the one thing that makes
a move cheap to review: the ability to treat a move as a move. State the split
explicitly in EVIDENCE ("bug found in relocated code at `file:line`; filed, not
fixed here") so it reads as a decision rather than an oversight.

## Capturing command output

Every gauntlet layer **redirects its output to its own log** under the task's
`logs/` directory. Once `tools/gauntlet.sh` exists (see "Gauntlet entry point"
below, which is where you write it), it enforces this by construction —
mechanism, not discipline, in the same way it deletes stale artifacts at start.
Until then, do it by hand on every command. Either way the log you read is the
final fresh run's log.

```sh
LOGS="$ARTIFACT_DIR/logs"
mkdir -p "$LOGS"          # redirect to a missing directory runs nothing at all
<test command>  > "$LOGS/tests.log" 2>&1
<types command> > "$LOGS/types.log" 2>&1
```

Why this belongs in *this* skill and not just in a general efficiency rule:
EVIDENCE requires every number to come from one final fresh run. Re-running a
suite to grep it a second way means the reported number and the grepped output
came from two different events — and on a flaky or order-randomized suite they
can genuinely disagree. The log file is the evidence substrate. **Cite the log
path next to each number in EVIDENCE** so any claim is traceable to an observed
run.

- **Redirect, don't `tee`.** `tee` is the instinctive choice and the wrong one:
  it dumps the whole run into the agent's context, which is the cost being
  avoided. `cmd > log 2>&1` also leaves the exit code direct.
- **Read a bounded slice** — `tail -30 "$LOGS/tests.log"`, or pull the summary
  line out with `rg`. Reading the whole log just relocates the waste.
- **Anti-pattern**: `pytest | tail -50` followed by `pytest | rg -i error`. That
  is two runs of the same thing. One run, two queries against the file.
- **Honest tradeoff**: a redirected run shows no live progress. For a long
  suite, say that it is running before starting it, then read the tail — an
  agent that goes silent for four minutes reads as hung.

## Scoping mutation: derive the set, do not type it

Mutation is slow, so it gets scoped, and scoping is where it stops covering the
defect. The failure has one shape: the author scopes to *the new module*, because
that is where the new logic is, while the change also touched the glue that calls
it — and the caller-side defect gets no mutants at all. Coverage will not flag
this; the glue line ran.

So the target set is **computed from the diff, not chosen**:

```sh
git diff --name-only <base>...HEAD    # then filter to source files
```

Every source file in that list is either mutated or **named in EVIDENCE as an
exclusion, with the reason**. "Too slow" and "the tool cannot reach it" are
legitimate reasons; the requirement is that the name appears, so a reader can see
which changed file nobody's tests were tested against. The mutation row shows
both the derivation and the resulting scope — a scope with no derivation beside
it is a claim about where the risk was, made by the person who wrote the risk.

Where the tool takes a module pattern rather than a file list (mutmut's
`"pkg.module*"`, Stryker's `mutate:`), translate the derived file list into that
pattern and check the translation covers every file. That translation is the step
that quietly drops the glue.

## Enumerating a defect class

SKILL.md requires four things of every finding: a generator sentence, an
enumeration produced by a command, the list in the commit, and the generator
handed to the next review round. The middle two are the mechanical part.

The test of the sentence is whether it names something you can list:

| Written as | Reachable by | Verdict |
|---|---|---|
| "`splitlines()` disagrees with the shell" | grepping `splitlines(` | symptom — finds only the spelling you already know |
| "we open a path that arrived from outside without validating what it is" | listing every `open`/`read` whose argument came from JSON, argv, or config | generator — a set, enumerable |
| "the CRLF case was missed" | grepping `\r\n` | symptom |
| "Python's idea of a line is not the pipeline's" | listing every place the two split the same text | generator |

Produce the list with a command — call sites of a function, every reader of a
config key, every branch of a dispatch — and record the command beside the list,
so the enumeration is reproducible rather than an assertion that you looked.
Then one line per site: `fixed`, `already correct (why)`, or
`not applicable (why)`. The disposition column is what makes a missed sibling
visible: an unexamined site simply has no row.

A class that returns one site is either genuinely singular or wrongly stated.
Both are worth a sentence — say which, because "the enumeration returned one" and
"I did not enumerate" look identical in a report that only shows the fix.

## Manual mutation procedure (any language, no tool)

**Reach for the project's mutation tool first.** A real tool generates mutants
from the syntax tree, so it cannot apply a mutant to code that has moved and it
cannot report a mutant it did not run. A hand-written mutant list matched
against source text is a second copy of the code: it goes stale on every
refactor of the thing it guards, and it fails in the one direction no gauntlet
can catch. Use the procedure below when no tool exists for the language, not as
a default.

**A hand-rolled runner must prove it executed each mutant.** This is the sharp
edge, and this repo's own demo found it: two same-size mutants written in the
same second shared a bytecode cache, so the runner reported kills for mutants it
never executed. That class of defect can *only* inflate the score, which means
it can never surface as a red gauntlet — the layer stays green precisely because
it is broken. `tools/mutants.py` now guards against it (mtime pinning, a cache
check that aborts the run); any runner written from this procedure needs the
equivalent, and EVIDENCE should say which check proves execution.

**The mutants are a committed file, not a sequence of edits.** This is the step
most likely to decay back into ad-hoc source edits in a scratch directory,
because hand-editing feels faster for the first mutant and the cost only lands
later. Write the script first; there is no "just this once" version of this
layer.

Where it goes: **repo level** — `tools/mutants.py` (or the ecosystem
equivalent), beside `tools/gauntlet.sh`, never inside the dated artifact
directory and never in a scratch dir. It is a tool the human reruns after the
task is over, not an output of the task. It must be named in the SPEC's setup
plan, so approving the spec authorizes creating it.

Three things the script buys that hand edits cannot:

- **A re-runnable score.** EVIDENCE claims "12/12 killed"; the human types one
  command and gets 12/12. A list of edits to re-apply by hand is not
  reproducibility, it is instructions for reproducing it yourself.
- **A free rerun.** The EVIDENCE rule (all numbers from one final fresh run)
  means the mutants run at least twice. The second run costs nothing.
- **Debris control.** A mutation run that dies midway leaves the source
  modified, or leaves stray files a mutant's code path wrote. The script
  restores in a `finally` and then *verifies* with `git diff --exit-code` and a
  check for new untracked files, so "restored clean" is a mechanism rather than
  a claim.

Shape — a table of mutants as data, plus a runner:

```python
# tools/mutants.py — each mutant is (path, old, new, label); `old` must be unique in the file.
MUTANTS = [
    ("src/pkg/rules.py", "if n <= limit:", "if n < limit:",  "off-by-one on the limit"),
    ("src/pkg/rules.py", "return matches",  "return matches[:1]", "only the first match reported"),
]
# for each: read file → assert old occurs exactly once → write mutated → run the suite
# → expect NON-ZERO exit (a zero exit is a SURVIVOR) → restore in `finally`.
# after the loop: `git diff --exit-code` and `git status --porcelain` must both be clean.
```

1. Pick the new/changed implementation code.
2. Write 3–5 plausible bugs into the table, biased toward the logic that matters
   most:
   - flip a comparison (`<` → `<=`, `==` → `!=`)
   - off-by-one a loop bound or slice index
   - delete one branch of a conditional / remove an early return
   - swap `and`/`or`; negate a boolean
   - replace a returned value with a constant (`0`, `null`, `""`)
3. Run the script. **Every mutant must make at least one test fail.** A
   surviving mutant means a missing or vacuous assertion — add the test that
   kills it, then rerun the whole script.
4. The script's own restore check (`git diff --exit-code` clean, no new
   untracked files) is the proof the tree came back; run the suite once more to
   confirm green.
5. Report as: `manual mutation | python tools/mutants.py | N/N killed` — the
   command is part of the claim. A score with no command is an incomplete
   EVIDENCE row.

Include a **control mutant** when the set is small (1–2 real mutants): one
deliberate, obviously-fatal break whose death proves the harness detects
mutations at all. A "1/1 killed" from a harness that never actually ran the
suite looks identical to a real result.

### Callout: mutation testing on relocated code

Not a separate layer — a reason to run the existing one after a move. When a
symbol changes location, tests that patch it *by location* silently stop
applying: they keep passing while asserting nothing. Python's
`monkeypatch.setattr` binds per-module, so patching the old module no longer
affects the new call site; `jest.mock` binds by path, with the same result.

Mutation testing already catches this — a test that asserts nothing kills no
mutants. Say so explicitly, because a passing suite immediately after a move is
the case people most readily trust and the case most likely to be hollow.

## Gauntlet entry point

Persist one command that runs every layer in sequence and fails on the first
broken one (e.g. `tools/gauntlet.sh`: tests+coverage → types → lint → mutation
→ real execution). It takes the task's artifact directory as an argument and
writes each layer's output to `<artifact dir>/logs/<layer>.log`. Pass that
directory in rather than deriving it from the CWD: under worktree isolation the
logs live outside the worktree, not beside the code being tested
(`setup.md` § Which tree each artifact is written in). Start the
script by deleting stale artifacts from previous runs (old coverage data,
report files, the previous logs) so no layer can accidentally read a prior
run's output — freshness by mechanism, not discipline. (Keep tool
databases that accumulate value, e.g. hypothesis's example store.) The "final
fresh run" IS this command; EVIDENCE cites it, and the human can rerun the
whole report with it. It runs whatever commands the project's rules name, so the script and the
rules never disagree. Pin dev-tool versions
(requirements-dev.txt, package.json devDependencies with exact versions, etc.)
so the rerun uses the same gauntlet.

Gate code itself must fail closed (see the checker note in SKILL.md): `set -e`
at the top, no `|| true`, no `2>/dev/null`, and spell out the exit-code cases
of any command whose codes are ambiguous. The classic trap is a
must-find-nothing grep: rc 1 (no matches) is the only pass; rc 0 means the
forbidden pattern exists, and rc ≥ 2 means the check itself broke (unreadable
input, bad pattern) — both must fail the layer, or an unreadable file turns
into a vacuous pass. Prove each home-grown check can fail with a one-off
negative control (feed it a known-bad fixture; make its input unreadable) and
record the control in EVIDENCE's honest notes.

Keep the assurance boundary explicit: application coverage and mutation target
the subject under test; do not widen them across every orchestration script by
default. Protect home-grown tools in the gauntlet's trust chain with targeted
negative controls for identified fail-open modes, and pin the failure reason,
not merely a non-zero status. A control proves only its named known-bad case,
not the whole tool. For the entry point itself, bind execution to completion:
maintain a fixed expected-layer manifest, record each layer only after its
commands succeed, and audit the manifest before printing success. Do not use a
heading as evidence that a layer ran, and do not rely on `set -e` through `&&`
or another conditional context; handle the command status explicitly.

Skeleton — adapt the commands, keep the structure. Four things carry the
mechanism claims: the `set -e`, the stale-artifact delete, the `mkdir -p`, and
the expected-layer manifest with its closing audit. Drop any of them and "by
construction" stops being true:

```sh
#!/usr/bin/env bash
set -euo pipefail
ARTIFACT_DIR="${1:?usage: gauntlet.sh <artifact dir>}"

# Guard the delete below: refuse anything that is not a real task directory.
[ -f "$ARTIFACT_DIR/SPEC.md" ] || { echo "not a task artifact dir: $ARTIFACT_DIR" >&2; exit 2; }
LOGS="$ARTIFACT_DIR/logs"

rm -rf "$LOGS" .coverage coverage.xml <other stale report files>
mkdir -p "$LOGS"

# Every layer this run must complete. Kept in one place so a layer that is
# deleted, commented out, or never reached is a failure rather than a silence.
EXPECTED_LAYERS="tests coverage types lint mutation property supply-chain suite-health real-execution"
COMPLETED_LAYERS=""

# Records the layer ONLY after its command exits 0. Not before, and never from
# the heading — a printed heading proves the script reached a line, nothing more.
run_layer() {
  layer=$1; log=$2; shift 2
  printf '=== %s ===\n' "$layer"
  if "$@" > "$LOGS/$log" 2>&1; then
    COMPLETED_LAYERS="$COMPLETED_LAYERS $layer"
  else
    rc=$?; echo "FAIL: layer '$layer' (rc=$rc); see $LOGS/$log" >&2; return "$rc"
  fi
}

run_layer tests          tests.log         <test+coverage command>
run_layer coverage       coverage.log      <coverage report command>
run_layer types          types.log         <types command>
run_layer lint           lint.log          <lint command>
run_layer mutation       mutation.log      <mutation command>   # the persisted script, e.g. python tools/mutants.py
run_layer property       property.log      <property command>
run_layer supply-chain   supply-chain.log  <dep audit + secret scan>
run_layer suite-health   suite-health.log  <randomized-order run>
run_layer real-execution run.log           <real-execution command>

# Not `echo "all layers passed"`. Audit the manifest first: name every expected
# layer that never completed, and print success only if none is missing.
for layer in $EXPECTED_LAYERS; do
  case " $COMPLETED_LAYERS " in
    *" $layer "*) ;;
    *) echo "FAIL: missing layer '$layer'" >&2; exit 1 ;;
  esac
done
echo "gauntlet: all layers passed; logs in $LOGS"
```

The guard matters because this script is generated by an agent and run
unattended. `${1:?}` catches an *empty* argument, not a dangerous one:
`gauntlet.sh /` would make the delete `rm -rf //logs`. Requiring `SPEC.md` to
exist in the directory means the only thing it will ever delete is a directory
this skill created.

`set -e` is what makes "fails on the first broken layer" true; without it the
script runs every layer and exits 0 on the last one, which reports green from a
run that had failures in it. The consequence is one failure per run: you fix,
rerun, and meet the next one. On a slow gauntlet that is worth knowing in
advance, so a clean tail after a fix is not misread as "only one thing was
wrong" — nothing after the first failure had a chance to run.

`set -e` is necessary and not sufficient, in two ways this skill has been bitten
by. It is *suppressed* wherever the command sits in a conditional context — the
left side of `&&`, a `!` negation, an `if` or `while` test, a command
substitution whose status you never read — so a layer written that way fails
silently and the script sails on. And even where it fires, it only stops a
command that ran; it cannot notice a layer that was deleted, commented out,
never reached, or run twice while another was skipped. That is what the
expected-layer manifest above is for: `set -e` bounds the damage of a *failing*
layer, the manifest is what proves an *absent* one cannot report green. Keep
both, and handle the command status explicitly rather than assuming the shell
did it for you.

**The entry point is itself a home-grown checker: prove it can fail before
trusting its pass.** One-off negative controls, once per project, then restore:
comment out one `run_layer` line and watch the closing audit go red naming the
layer; make one layer's command fail and watch the run exit nonzero with a red
record. Record both controls in EVIDENCE's honest notes. An orchestration that
has only ever been green has not been demonstrated to measure anything — the same
RED principle the tests and the checkers already answer to, applied one level up.

**Write a completion record from the entry point, on every exit path.** EVIDENCE is
model-written; the record is the completion artifact the harness writes, and it is
what turns "the checks ran, on this content, after the last change" from a claim
into a fact. Install an exit trap before the first layer and have it write, green
or red: the result, the expected and completed layer sets, a UTC timestamp, the
source state (commit SHA or tree hash — where the computation fails, write
`unavailable`, never a guess), and the pinned-toolchain file the run used. Only the
closing manifest audit may produce `green`. In the same trap, give the exit a
vocabulary: 0 for green; one code for a failed layer; one for a violated
orchestration contract, an exit 0 that skipped the audit included; a crash passes
through unchanged — automation needs a number, not a paragraph. The failure path
then leaves the trace a reader actually needs. Disclosed limit: the record is
written by the script it reports on, so it guards against accident, not a
coordinated edit to script and record together.

**Every EVIDENCE row must cite a log this script actually writes.** Two rules
keep that true:

- Where one command covers several layers (a test run that also produces
  coverage, or hypothesis properties that run inside the suite), cite the log
  that *contains the number* — the same log may appear on several rows. Do not
  invent a filename for a command you did not run separately.
- Layers no script can run — adversarial review, independent verification, and
  complexity budget where it is a judgement rather than a tool — are marked
  `manual` in the EVIDENCE Log column, never given a log path.

## The final fresh run in a fresh agent

At Tier 3, do not run the final gauntlet yourself. Spawn the `old-coder-gauntlet`
brief (ships at `agents/old-coder-gauntlet.md`) fresh, with no inherited context, and
hand it four inputs: the entry-point command, the artifact directory, the expected
source state, and the layer/gate table transcribed at SPEC time. It runs the entry
point once, reads bounded log slices, and returns a per-layer verdict in the closed
five-status vocabulary. It fixes nothing and reruns nothing; a red verdict is your
task, not its.

What the split buys: the run's interpreter did not write the code, so a skipped layer
or a stale number has no author present to rationalize it, and the raw logs never
enter the author's context — the author receives a verdict table. What it does not
buy: the entry point's own exit remains the gate; the runner reports and decides
nothing.

Two ways to run it, the same as the adversary: registered agent (the host enforces
`tools:`) or bundled brief (you honor the list). Record which in EVIDENCE's
`Gauntlet run by:` field. Author-run is the fallback and a recorded downgrade, not a
neutral note.

The `old-coder-evidence` scribe is the same mechanism pointed at the report: it
drafts EVIDENCE from artifacts alone, holds no `Bash`, and writes an absent artifact
as a failing row.

## Templates

The Gherkin scenario template, the SPEC template, the EVIDENCE report
template, and the tracker roll-up live in `references/templates.md`. This
file is read while building the gauntlet; that one is read while writing the
two artifacts the human reads.
