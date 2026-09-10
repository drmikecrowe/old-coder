# Spec: Sliding-Window Rate Limiter (Tier 3)

## Orientation
- **Change:** a new in-process library class `RateLimiter(limit, window_seconds,
  clock)` answering `allow(key) -> bool` — at most `limit` requests per key in
  any sliding `window_seconds` interval.
- **Why:** bound request frequency in front of a public HTTP API, where callers
  are untrusted and the key space is attacker-controlled.
- **Touches:** new library module only — no runtime dependencies (stdlib
  `deque`, `math`, `threading.Lock`). Adds gauntlet tooling under `tools/` and a
  CI workflow; changes no existing code.
- **Decide:** three accepted risks, each argued below rather than overlooked —
  the memory bound is **temporal, not cardinal** (an attacker can still inflate
  the key map within a single window); the clock is a **caller obligation** on
  three axes, so forward skew and non-finite readings are uncovered by design;
  and `allow()` returns a bare bool, so an HTTP frontend cannot populate
  `Retry-After`.

The contract below, in brief:

- **Covers:** the sliding window itself (hits expire individually, the exact
  boundary is still limited, denials consume no quota); per-key isolation with
  exact string comparison, no normalisation; constructor and `allow()` input
  validation, including NaN/inf/bool/float for `limit` and `window_seconds`;
  thread safety, with the clock read inside the critical section so commits
  cannot invert; and memory reclamation — a throttled sweep, its boundary, its
  behaviour under backward clock jumps, and what happens while traffic is silent.
- **Must NOT:** no real clock in tests (enforced by a regex gate over `tests/`,
  with two declared exceptions and their spurious-failure directions); no
  unbounded memory growth, bounded by the distinct keys seen in the **two**
  windows preceding the most recent request.
- **Out of scope:** no `Retry-After` or remaining-quota accessor, so an HTTP 429
  cannot be populated as RFC 9110 expects; no distributed or multi-process
  limiting — in-process state only.

The Gherkin scenarios below are the contract — this summary only says which of
them to read closely.

A library class `RateLimiter(limit, window_seconds, clock)` answering
`allow(key) -> bool`: at most `limit` allowed requests per `key` within any
sliding `window_seconds` interval. `clock` is an injected callable returning
current time in seconds (the mock boundary — no real sleeping in tests).
Intended deployment: in front of a public HTTP API, so callers are untrusted
and the key space is attacker-controlled.

This document is the contract. How each clause was arrived at — including the
defects that six rounds of independent verification found and the two that a
fix round introduced — is in `evidence.md`'s honest notes and in git history,
deliberately not here.

## Behaviour

```gherkin
Feature: Sliding-window rate limiting per key

  Scenario: requests under the limit are allowed
    Given a limiter with limit 3 per 60 seconds
    When a key makes 3 requests at t=0
    Then all 3 return True

  Scenario: request over the limit is denied
    Given a limiter with limit 3 per 60 seconds and 3 allowed requests at t=0
    When the key makes a 4th request at t=59
    Then it returns False

  Scenario: denied requests do not consume quota
    Given a limiter with limit 1 per 60 seconds
    And 1 allowed request at t=0 and 5 denied requests at t=10
    When the window expires at t=61
    Then the next request returns True

  Scenario: window slides — old requests expire individually
    Given a limiter with limit 2 per 10 seconds and requests at t=0 and t=5
    When the key requests at t=10.1
    Then it returns True   # the t=0 request left the window
    When the key requests at t=10.2
    Then it returns False  # t=5 and t=10.1 are still inside

  Scenario: keys are isolated
    Given a limiter with limit 1 per 60 seconds and key "a" exhausted at t=0
    When key "b" requests at t=0
    Then it returns True

  Scenario: request at the exact window boundary is still limited
    Given a limiter with limit 1 per 60 seconds and an allowed request at t=0
    When the key requests at exactly t=60
    Then it returns False  # a hit expires only when its age EXCEEDS the window

  Scenario: non-monotonic clock does not grant extra quota
    Given a limiter with limit 1 per 60 seconds and a request at t=100
    When the clock jumps backward by more than the window and the key requests
    Then it returns False  # skew must fail closed, never open

  Scenario: invalid construction is rejected
    When constructing with limit 0, a negative limit, or window_seconds <= 0
    Then ValueError is raised naming the bad parameter
    (a limiter that silently never or always allows is a security bug)

  Scenario: limit must be a finite positive integer
    When constructing with limit = NaN, +/-inf, a float such as 2.5, or a bool
    Then ValueError is raised naming limit
    (every comparison against NaN is false, so the limiter allowed forever)

  Scenario: window_seconds must be a positive finite number
    When constructing with window_seconds = NaN, +/-inf, True, "60", or None
    Then ValueError is raised naming window_seconds

  Scenario: key must be a non-empty string
    When calling allow() with None, an int, bytes, or ""
    Then TypeError (wrong type) or ValueError (empty) is raised
    (a missing HTTP header arriving as None must not become one shared bucket
    for every unidentified caller)

  Scenario: keys are compared as exact strings
    Given a limiter with limit 1 per 60 seconds
    When "Alice", "alice", "alice " and " " each make a request
    Then all are allowed — they are four different callers

  Scenario: concurrent callers never exceed the limit
    Given a limiter with limit 1 per 60 seconds
    When many threads call allow() for the same key simultaneously
    Then exactly 1 call returns True

  Scenario: concurrent commits never invert against the clock read
    Given two callers whose clock reads return different values
    When the caller that read the earlier value commits second
    Then the recorded hits are still in ascending order
    (both pruning and sweeping assume that order)

  Scenario: idle keys are forgotten — the key map is bounded
    Given 1000 distinct keys that each made one request at t=0 and never return
    When any request arrives after a full window has elapsed
    Then the limiter retains only keys with a hit inside the current window

  Scenario: a key is dropped by the first sweep after one idle window
    Given "armer" and "idle" both at t=0
    When a request arrives at t=61, firing the sweep
    Then "idle" is gone  # the idle threshold is one window, not more

  Scenario: the sweep keeps a key whose newest hit is exactly one window old
    Given "other" at t=0 arming the sweep, and "k" at t=1
    When a request arrives at t=61, firing the sweep
    Then "k" is still limited — its hit is exactly 60s old, not older

  Scenario: the key map is bounded by two windows, not one
    Given "armer" at t=0 and "idle" at t=1, then a request at t=60.9
    When a request arrives at t=100 — "idle" has been idle for 99s
    Then "idle" is still retained; only at t=121 is it forgotten
    (the sweep is throttled, so residency reaches 2W before the dropping sweep)

  Scenario: nothing is reclaimed while traffic is silent
    Given 50 one-shot keys at t=0
    When the clock advances by ~166,000 windows and no request is made
    Then all 50 are still resident; the map shrinks only on the next request

  Scenario: the sweep is throttled to at most once per window
    Given a limiter with a 60-second window and a request at t=0
    When further requests arrive at t=30 and at t=60
    Then no further sweep has run; the sweep at t=61 does run

  Scenario: the first call always sweeps
    Given a fresh limiter with a 60-second window
    When the very first request arrives at t=30
    Then a sweep has run

  Scenario: a backward clock jump does not suspend reclamation
    Given a limiter armed at t=1,000,000
    When the clock jumps back to 0 and 200 one-shot keys arrive over 400s
    Then the sweep still runs and the map does not grow without bound
```

## Invariants (property-based)

- **P1**: for any request sequence on one key, the allowed count within any
  window of `window_seconds` never exceeds `limit`.
- **P2**: interleaving traffic from other keys never changes one key's outcomes.

## Must NOT do

- **No real clock in tests.** The limiter under test is never driven by a real
  clock, and no test makes time pass by sleeping. The gate that enforces this
  is a regex over `tests/`; its scope is known direct wall-clock imports and
  calls. Dynamic imports, renamed helpers and a caller's own `sleep()` escape
  it, and the gate does not claim otherwise.

  *Declared exception.* Two assertions in the concurrency tests do depend on
  real elapsed time, and they fail in opposite directions:
  (1) the atomicity test asserts a blocked thread is still alive after 0.2s —
  spurious failure only; (2) the clock-ordering test waits up to 0.3s for a
  racing caller — on healthy code that wait always times out, and its spurious
  direction is a false PASS, i.e. a surviving fail-open mutant. Measured margin
  ~470×. Accepted deliberately: the alternative is a test that can hang.

- **No unbounded memory growth.** Growth is bounded by the distinct keys seen
  in the **two** windows preceding the most recent request. Precisely: a key is
  resident at an age of at most exactly 2W whenever a request is observed, and
  the sweep that drops it runs strictly later than 2W after its last hit. The
  qualifier is load-bearing — sweeping happens only inside `allow()`, so while
  traffic is silent nothing is reclaimed at all and the peak resident set is
  not released until traffic resumes.

## Clock contract

`clock` is a caller obligation on three axes. None is checked in code, because
each check would put a branch on the hot path for a fault the recommended
clock cannot produce.

- **Monotonic** (`time.monotonic`, as `examples/demo.py` uses). A forward jump
  — NTP step, resumed VM — expires every hit at once and resets every caller's
  quota simultaneously. That is inherent to a sliding window over a supplied
  clock. Backward skew *is* handled: it fails closed for quota, and the sweep
  re-arms rather than suspending.
- **Finite.** A NaN reading is recorded as a hit that can never expire, in
  pruning or in sweeping, so that key is retained forever and its caller is
  denied forever — which suspends the memory bound for that key. A NaN also
  costs one extra unthrottled sweep; the throttle re-anchors on the next
  finite reading.
- **Non-reentrant.** The clock is read inside the critical section, so a clock
  that calls back into the same limiter deadlocks.

`clock` is also the one constructor parameter with no validation: a
non-callable clock raises TypeError at the first `allow()`, which is loud and
fail-closed rather than silently accepted.

## Accepted residual risk

The memory bound is **temporal, not cardinal**. Keys idle for a window are
forgotten, but nothing caps how many distinct keys appear *within* one window,
so an attacker controlling the key can still drive the map arbitrarily large
inside a single window. Accepted, not overlooked: a cardinality cap needs an
eviction policy, and evicting a live key silently resets its quota — a
fail-open worse than the memory it saves.

## Failure model (Tier 3)

Every covered mode names a **falsification procedure that has been
demonstrated to fail** — a test, a mutant, fault injection, whatever fits the
risk. Not "a test AND a mutant", which only breeds mutants written to fill a
table. A row whose catcher cannot be shown to fail is a defect, not a mapping.

| How this can hurt | Falsification procedure, demonstrated |
|---|---|
| over-allowing in a burst | scenario tests + P1; M1/M5 killed |
| under-allowing / quota lost | boundary scenario; M2 killed (P1 is one-sided and cannot see this) |
| hostile or invalid config accepted | validation scenarios for limit, window_seconds and key; M4/M7/M9/M15 killed |
| backward clock skew opening the gate | non-monotonic scenario, jump exceeding the window; M10 killed |
| backward skew suspending reclamation | backward-jump scenario; M20 killed |
| forward skew resetting all quota | **not covered — caller obligation** |
| a non-finite clock reading freezing a hit | **not covered — caller obligation** |
| caller identity merged by normalisation | exact-strings scenario, case and padding; M14/M17 killed |
| quota reset by the sweep at the boundary | sweep-boundary scenario; M18 killed |
| the retention bound silently inflating | first-sweep scenario; M23 killed (the boundary was pinned long before the magnitude was) |
| unbounded memory growth (any path) | idle-keys + silent-traffic scenarios; M8/M12 killed |
| the sweep degrading to an O(keys) scan | throttle + first-call scenarios; M19/M21/M22 killed |
| concurrent callers racing on shared state | **fault injection**: the atomicity test constructs the interleaving and kills M13 deterministically. The threaded stress test only corroborates — it is statistical (see evidence.md) |
| commits inverted against the clock read | clock-ordering scenario with a gated clock; M16 killed |
| the mutation layer reporting kills it never ran | **negative control**: a killer and a strictly-equivalent mutant of identical size under one pinned mtime, proven non-vacuous by removing the defence |
| untested code reaching production | coverage layer, a gate at `--cov-fail-under=100` |
| silent failure in production | n-a: the library returns a bool the caller observes directly |

## Setup plan

- Runtime dependencies: **none** — `collections.deque`, `math` and
  `threading.Lock` are stdlib.
- Dev toolchain (pinned in `requirements-dev.txt`, never shipped): pytest +
  pytest-cov + coverage (tests and changed-line coverage), mypy (strict types),
  ruff (lint, format, mccabe ≤ 8), hypothesis (P1/P2), pip-audit (toolchain
  vulnerabilities), pytest-randomly (suite health).
- Git: repo-level; commits at each milestone; evidence binds to a commit SHA.
- Files the gauntlet adds: `tools/gauntlet.sh` (entry point), `tools/mutants.py`
  (scripted mutation + its negative control), `tools/must_not_match.sh` and
  `tools/test_gauntlet_checks.sh` (fail-closed scan helper and its self-test),
  `tools/source_state.sh`, `.github/workflows/gauntlet.yml` (CI).

## Explicitly out of scope

- **Retry-After / remaining-quota accessor.** `allow(key) -> bool` gives an
  HTTP frontend no way to populate `Retry-After` or `X-RateLimit-Remaining`,
  which RFC 9110 expects alongside a 429. Declined: it changes the public API
  shape, and the contract asks only to bound request frequency. Recorded so
  the gap is visible rather than absent.
- **Distributed / multi-process limiting.** In-process state only.

## Verification contract

What green will mean, stated before any of it runs. Every layer the entry point
invokes appears here, and `tools/contract_ids.py` fails when this list and
`tools/gauntlet.sh` disagree in either direction. A reader holding this table
can tell a layer that failed from a layer that was never wired up.

| Layer | What it gates | Threshold |
|---|---|---|
| `orchestration-self-test` | a harness that reports green while skipping a layer | every expectation holds; exit 0 |
| `checker-self-test` | a must-not scan that cannot distinguish "no matches" from "the check broke" | every expectation holds; exit 0 |
| `source-state-self-test` | a binding that survives a dirty or truncated tree | every control passes |
| `tests-coverage` | untested changed lines | 0 failures and 100% of changed lines and branches, gated by `--cov-fail-under=100` |
| `types` | contract drift the suite does not reach | 0 errors under `mypy` strict over `src tests examples tools` |
| `lint-format` | style drift and dead constructs | 0 findings from `ruff check` and `ruff format --check` |
| `shell-lint` | defects in the half of the harness written in shell | 0 findings from `shellcheck` over `tools/*.sh`, `../hooks/*.sh` and `../tools/*.sh`; a missing `shellcheck` is a red layer, never a skip |
| `supply-chain` | known-vulnerable dependencies | 0 advisories from `pip-audit` |
| `must-not-scans` | real clocks in tests, and credentials anywhere | 0 matches; a broken scan exits 2 and is distinguishable from a clean one |
| `mutation-control` | a mutation runner that reports kills it never ran | the killer mutant is killed and the equivalent mutant survives |
| `mutation` | tests that assert nothing | every mutant in the committed table is killed |
| `real-execution` | a suite that passes against a fake clock only | `examples/demo.py` runs against the real clock and exits 0 |
| `audit-sweep` | an audit row crediting a bound its agent's tools cannot hold | 0 unsupported claims |
| `audit-sweep-controls` | a sweep whose hooks-tier lift credits any agent that mentions hooks | 9 cases pass, including a hook on the wrong tool and a hook covering only one of two defeating tools |
| `ceiling-ids` | a published ceiling that has drifted from the audit | 0 disagreements in either direction |
| `contract-ids` | this contract drifting from the harness it describes | 0 disagreements in either direction |
| `hooks-registered` | a frontmatter hook whose handler was renamed, deleted, or left non-executable, which fails open silently | 0 unusable hooks; this is the CI half and is not the proof that the host calls them |
| `hook-controls` | a hook handler that allows what it claims to deny | 12 cases pass, symlink escape and empty payload included |
| `source-state` | a report bound to a state nobody can return to | a binding is produced, or a named reason why it is not |
| `evidence-binding` | a report whose numbers came from a different tree | the report's tree hash equals the derived one, and a stale review round does not sit under a bare `PASSED` |

Review layers, which are graded rather than computed. Their powers and binding
are published; the findings they should look for are not, because a reviewer
whose questions are known in advance grades work optimised for those questions:

| Layer | Powers | Binding |
|---|---|---|
| Spec intent (`old-coder-spec-intent`) | `Read`; one round; expected to use no tools at all | the SPEC text as approved. Its `Read` is bounded to the SPEC's own directory by a frontmatter `PreToolUse` hook (`hooks/spec-intent-scope.sh`), which `docs/loop-alignment.md` EX-1 keeps at `accepted` until the host probes for that hook are recorded |
| Adversarial review (`old-coder-adversary`) | `Read`, `Bash`, `Grep`, `Glob`; one round; at most 10 tool calls | the source-state tree hash the reviewed diff was taken from. Any later change to the source manifest returns this layer to not-run |
| Independent verification | a fresh context at a named state, no inherited reasoning | the state it actually saw. Its status for this report is recorded in `evidence.md`, not promised here |

Exit vocabulary for `tools/gauntlet.sh`: `0` every layer green; `2` a layer ran
and failed, with its own status preserved in the stamp; `3` the orchestration
contract was violated, including an exit 0 that never reached the completion
audit; any other status is a crash, passed through unchanged.

## REVISION 5 — reproducible source-state binding (Tier 3)

Approved 2026-08-18. This revision repairs the evidence mechanism; it does
not change rate-limiter runtime behaviour or its public API.

### Behaviour

- In a Git checkout, `tools/source_state.sh` hashes only version-controlled
  files in the declared source scope. Ignored build products such as
  `*.egg-info`, bytecode caches and coverage output cannot change the hash.
- The same tracked content produces the same tree hash in the working tree, a
  clean checkout and the no-Git archive fallback, regardless of current
  working directory.
- In Git, relevant staged changes, unstaged changes, deletions or non-ignored
  untracked files make the command fail closed instead of emitting a binding.
- The command reports both current HEAD and the most recent commit that
  changed the source scope. A later evidence-only commit may change HEAD while
  preserving the source commit and tree hash.
- Missing or unreadable manifest inputs make the command fail non-zero; no
  partial hash may be reported.
- The gauntlet runs a negative-control self-test for these properties and then
  emits the source-state binding only after every other layer has passed.

### Must NOT do

- Do not derive a Git binding from ambient ignored files on disk.
- Do not silently omit a new, non-ignored file inside the source scope.
- Do not use a hashing pipeline whose intermediate read failure can be hidden
  by the exit status of its final command.
- Do not add a runtime or development dependency for this repair.

### Setup plan

- Modify `tools/source_state.sh`; add its implementation and regression tests
  under `tools/` and `tests/`; connect the self-test and binding to
  `tools/gauntlet.sh`; clarify the reusable rule in the old-coder evidence
  template; update `evidence.md` after the implementation commit is clean.
- Commit cadence: this approved SPEC first; tests plus implementation second;
  evidence rebinding third. Independent verification remains `not performed`
  unless a separate verifier actually inspects the final source state.

## REVISION 6 — shallow-history provenance and grounded negative controls (Tier 3)

Approved 2026-08-18. This revision repairs a provenance defect introduced by
REVISION 5 and grounds the negative controls that guard it; it does not change
rate-limiter runtime behaviour or its public API.

REVISION 5 reported the most recent commit that changed the source scope
without checking whether the repository holds enough history to answer. In a
shallow repository `git log` attributes the scope to the grafted HEAD, so the
command emitted a real-looking commit that had not touched the source — at
exit 0, with no warning. Before this revision the canonical CI ran a shallow
checkout, so the one environment that executed this automatically was the one
reporting it wrongly.

### Behaviour

- The two outputs carry different obligations. **When a binding is produced,
  the tree hash is the required content identity; the source commit is
  provenance and is supplied only when complete history is available.** No
  error path emits a binding at all.
- In a shallow repository the command still succeeds: it reports HEAD and the
  tree hash, and reports the source commit as the exact marker
  `(unavailable: shallow history)`.
- That degradation is deliberately conservative. A shallow repository reports
  the marker even when the source commit happens to lie inside the fetched
  depth, because truncation cannot be disproved from inside the repository.
  Guessing here would reintroduce the defect for a narrower input.
- No error path writes anything to standard output. A caller that sees any
  binding line can rely on the command having succeeded.
- The canonical CI checks out complete history, so the source-commit path is
  exercised for real rather than permanently degraded.

### Must NOT do

- Do not report any commit as the source commit when history is truncated.
- Do not treat an exit status alone as proof of which failure occurred; a
  negative control must pin the reason.
- Do not let a test fixture continue when the implementation under test is
  absent — a fixture that degrades silently cannot be a negative control.
- Do not add a runtime or development dependency for this repair.

### Setup plan

- Modify `tools/source_state.py` (shallow detection and marker) and
  `.github/workflows/gauntlet.yml` (`fetch-depth: 0`). Extend
  `tests/test_source_state.py`: a shallow negative control asserting the full
  output contract, two no-Git error-path controls, `stdout == ""` on every
  error path, the Git deletion control renamed to what it actually exercises,
  and unconditional copying of the implementation into the fixture.
- No new files, no new dependencies.
- Commit cadence: this approved SPEC first; implementation, tests and CI
  configuration second; evidence rebinding third. Independent verification
  remains `not performed` unless a separate verifier inspects the final state.

## REVISION 7 — fail-closed gauntlet orchestration (Tier 3)

Approved 2026-08-18. This revision repairs a demonstrated fail-open defect in
the gauntlet entry point; it does not change rate-limiter runtime behaviour or
its public API.

Before this revision, deleting a layer command while leaving its heading could
make `tools/gauntlet.sh` print that heading, perform no work for the layer, exit
zero and announce that every layer was green. This was reproduced by deleting
the committed mutation invocation: no mutant ran, but the gauntlet still
reported success.

### Behaviour

- The gauntlet has a fixed manifest of expected layers and records a layer as
  complete only after all commands for that layer succeed.
- A layer command that fails stops the gauntlet immediately, preserves its
  non-zero status and names the failed layer. Later layers do not run.
- A successful command sequence that omits any expected layer fails at the
  final audit and names every missing layer.
- Unknown and duplicate layer completions fail instead of silently changing or
  overstating the run.
- The all-green message is emitted only by the final completion audit, after
  every expected layer has completed exactly once.

### Must NOT do

- Do not use a printed heading as evidence that a layer ran.
- Do not rely on `set -e` to stop a command placed on the left side of `&&` or
  inside another conditional context.
- Do not extend application coverage or mutation gates across all of `tools/`
  as a substitute for a control aimed at this orchestration failure mode.
- Do not claim that one negative control proves a checker recognizes every
  violation; each control proves only its named known-bad case.

### Setup plan

- Work on branch `codex/issue-13-gauntlet-orchestration`, preserving unrelated
  untracked assets in the user's checkout.
- Add `tools/gauntlet_layers.sh` for the expected-layer manifest, execution
  wrapper and final audit; add `tools/test_gauntlet_orchestration.sh` with
  controls for an omitted layer and a failed command, plus unknown and
  duplicate registrations; modify `tools/gauntlet.sh` to use the helper.
- Clarify the reusable assurance boundary in
  `skills/old-coder/references/gauntlet.md`: targeted negative controls guard
  identified fail-open modes in trust-chain tooling, while application
  coverage and mutation remain scoped to the subject under test.
- No new dependency. Commit cadence: this approved SPEC first; tests plus
  implementation second; evidence rebinding third. Independent verification
  remains `not performed` unless a separate verifier inspects the final state.

## REVISION 8 — harness-written completion stamp and exit vocabulary (Tier 3)

Approved 2026-08-30 (as part of the loop-alignment roadmap,
`docs/loop-alignment.md` Phases B and D). This revision extends REVISION 7's
fail-closed orchestration; it does not change rate-limiter runtime behaviour
or its public API.

Before this revision the entry point proved completion only through its exit
status and terminal output. The evidence report that cites it is written by
the model, so nothing harness-written asserted the three facts a completion
claim rests on: that the layers passed, against which exact content, and
after the last change. On failure the run left no artifact at all, so the
trace existed only for the runs nobody needs to re-read. And the exit status
was whatever the failing tool exited with, so automation could not tell a
layer verdict from a broken script.

### Behaviour

- After every run — green, failed, or crashed — the entry point writes a
  completion stamp to `gauntlet-stamp.txt` (git-ignored) recording the
  result, the expected and completed layer sets, the failed layer where one
  failed, a UTC timestamp, and the source-state binding.
- The stamp's source-state section is the output of `tools/source_state.sh`.
  Where that command fails — dirty tree, truncated input — the stamp records
  that the binding is unavailable; no stamp carries a partial or guessed
  binding.
- The stamp reports green only after the final completion audit has passed.
  A run that exits zero without reaching the audit is stamped incomplete,
  never green, and the exit is remapped to the orchestration-failure code.
- The entry point's exit status distinguishes a decision from a crash:
  0 — all layers green; 2 — a layer ran and failed (its own status is
  preserved inside the stamp); 3 — the orchestration contract was violated
  (unknown, duplicate, or missing layer, or an exit before the audit); any
  other status is a crash, passed through unchanged.
- `run_layer` and `finish_gauntlet` keep their return statuses; the
  vocabulary is applied once, at the entry point's exit. The existing
  orchestration controls that assert preserved statuses stay valid.

### Must NOT do

- Do not write a green stamp from anywhere but the final completion audit.
- Do not let a stamp claim a source binding that `tools/source_state.sh` did
  not produce.
- Do not skip the stamp on the failure path — a trace that exists only for
  green runs is missing exactly the runs a reader needs.
- Do not change the return statuses of `run_layer` or `finish_gauntlet`.
- Do not add a runtime or development dependency for this repair.

### Setup plan

- Modify `tools/gauntlet_layers.sh` (stamp writer, failure classification,
  exit-trap installer) and `tools/gauntlet.sh` (delete the stale stamp,
  install the trap). Extend `tools/test_gauntlet_orchestration.sh` with
  controls for the green stamp, the failed-layer stamp and exit 2, the
  orchestration stamp and exit 3, crash passthrough, the
  exit-zero-before-audit remap, and the unavailable-binding stamp. Add
  `gauntlet-stamp.txt` to `.gitignore`.
- No new dependency. Commit cadence: this approved SPEC first; tests plus
  implementation second; evidence rebinding third. Independent verification
  remains `not performed` unless a separate verifier inspects the final
  state.

## REVISION 9 — one identity function for evidence and review (Tier 3)

Approved 2026-09-10, after an intent review that found the spec shipped
detection while leaving the authoring guidance that causes the defect. Track-A
object A4. This revision adds a gauntlet layer over `evidence.md`; it does not
change rate-limiter runtime behaviour or its public API.

Two identities are in use and only one is enforced. `tools/source_state.py`
hashes the tracked source manifest and fails closed, and the completion stamp
carries what it produced. Everything else in the report is a SHA a human typed:
the state the gauntlet ran at, and the state each verification round bound to.
Nothing compares the typed values against the derived one. A report can
therefore cite a clean commit while the tree that produced its numbers was
dirty, or keep citing a binding three source commits stale, and every layer
stays green. That is the failure `source_state.py` exists to prevent, still
open on the reporting path.

### Behaviour

- A new layer, `evidence-binding`, runs `tools/evidence_binding.py`. It derives
  the current binding by calling the same function the stamp calls, reads the
  bindings `evidence.md` states, and compares them.
- **Comparing against the derived binding is comparing against the stamp's.**
  The stamp's `source_state` section is the output of that same command and
  nothing else: REVISION 8 forbids a stamp carrying a binding the command did
  not produce, and the orchestration controls prove it. So the two comparisons
  cannot disagree, and the derived one is available at layer time while the
  stamp is not.
- **The report's own binding must be current.** The tree hash `evidence.md`
  gives as the source state of its gauntlet run must equal the derived tree
  hash. A mismatch is a failing row naming both values.
- **A verification round's binding is checked against the verdict, not against
  the present.** A round may legitimately bind to an earlier state; that is
  what a declared downgrade is. So: where the report's headline verdict is bare
  `PASSED`, every verification round it counts must bind to the current tree
  hash. Where any round binds to an older state, the verdict must be
  `PASSED WITH LIMITS` or `FAILED`. `PASSED` over a stale review is the
  failing row.
- The layer fails closed. An `evidence.md` it cannot parse a binding from, an
  absent report, and a source-state command that fails are each a failure
  naming the reason, never a pass.
- `evidence.md` is outside the source manifest, so editing the report does not
  move the binding it cites. Editing source does, which is the point: source
  changes turn this layer red until the report is rebound.

### Must NOT do

- Do not compare a verification round's binding against the present state and
  fail on difference alone. An older round is legal; an older round under a
  bare `PASSED` is not.
- Do not derive the binding by any route other than the source-state command.
  A second implementation of the identity function is the defect this revision
  closes, reintroduced.
- Do not let an unparseable report pass. A checker that cannot find the field
  it grades reports nothing found, never nothing wrong.
- Do not read `gauntlet-stamp.txt` for the comparison. The stamp is written by
  the exit trap after every layer has run, so a layer reading it would grade
  the previous run.
- Do not add a runtime or development dependency for this layer.

### Out of scope here, and where it is tracked

This revision is the demo's contract, so it governs the checker only. The
authoring side of the same defect lives in the skill: `SKILL.md` and
`references/templates.md` still tell an author to bind a review to a
`<base>...HEAD` SHA they type. A checker that catches a stale binding while the
template keeps asking for the value that goes stale is half the fix. That
change ships with this one under track-A object A4 (`docs/track-a.md`), and
neither half closes the object alone.

### Setup plan

- Add `tools/evidence_binding.py` and register `evidence-binding` in
  `tools/gauntlet.sh` and the expected-layer manifest in
  `tools/gauntlet_layers.sh`. Add `tests/test_evidence_binding.py` with a
  negative control per failure: a stale report binding, a bare `PASSED` over a
  stale round, an unparseable report, an absent report, and a failing
  source-state command. Add the layer's row to `evidence.md`'s gauntlet table
  and rebind the report, since `tests/` and `tools/` are inside the manifest.
- No new dependency. Commit cadence: this approved SPEC first; tests plus
  implementation second; evidence rebinding third. Independent verification
  remains `not performed` unless a separate verifier inspects the final state.

## REVISION 10 — the demo's gauntlet runs the repository's own checks (Tier 3)

Approved 2026-09-10, track-A object A5. This revision registers two existing
checks as layers; it adds no new check, and does not change rate-limiter
runtime behaviour or its public API.

`tools/audit_sweep.py` and `tools/ceiling_ids.py` live at the repository root
and grade repository documents: that no audit row credits a capability bound
its agent's tool list cannot hold, and that the ceiling published inside the
skill matches the audit it is drawn from. Both have negative controls. Neither
is run by anything. A check nobody runs is this repository's own named defect
class, so leaving them as hand-run scripts contradicts the text they check.

**Name the smell rather than hide it.** These are repository-level checks and
the demo is a rate limiter. They land here because the demo's gauntlet is the
only runner this repository has. That is a real design problem: the correct
home is a repository-level gauntlet the demo's one is a member of. This
revision buys the checks a runner today and records the debt.

### Behaviour

- Two layers, `audit-sweep` and `ceiling-ids`, run `../tools/audit_sweep.py`
  and `../tools/ceiling_ids.py`. Both are registered in the expected-layer
  manifest, so an omitted one is an orchestration failure like any other.
- They run before `source-state`, because they grade documents outside the
  source manifest and a failure in them says nothing about the binding.
- Each fails closed on its own terms, already: an audit with no rule rows, a
  ceiling with no rule rows, and an absent file are failures naming the reason.

### Must NOT do

- Do not add the repository-root `tools/` directory to the source manifest.
  The binding is about the demo's runtime behaviour; a wording change in an
  audit must not invalidate a rate-limiter verdict. The consequence, that these
  two checkers are outside the binding, is published in the skill's ceiling
  rather than fixed by widening the hash.
- Do not let either layer's absence pass. They are manifest members, not
  optional extras.
- Do not add a runtime or development dependency for either layer.

### Setup plan

- Register both layers in `tools/gauntlet.sh` and the manifest in
  `tools/gauntlet_layers.sh`. Add both rows to `evidence.md`'s gauntlet table
  and update the layer count. No new dependency, no new test: both scripts
  already carry their controls, exercised in the objects that wrote them.
- Commit cadence: this approved SPEC first; the registration second; evidence
  rebinding third. Independent verification remains `not performed` unless a
  separate verifier inspects the final state.

## REVISION 11 — the verification contract is published and checked (Tier 3)

Approved 2026-09-10 in the instruction that opened track-A object A7. Track-A
object A7. This revision adds a contract section and one layer that checks it;
it does not change rate-limiter runtime behaviour or its public API.

Until now this spec described the gauntlet only through its revisions, each
adding a layer in passing. A reader could not get the layer list from the
contract, only from the entry point, which means the contract was a record of
what had been built rather than a promise made before building. The difference
matters at exactly one moment: when a layer is missing. With a published list
the reader tells a layer that failed from a layer nobody wired up. Without one
those look identical.

### Behaviour

- `## Verification contract` names every layer the entry point invokes, with
  the number or state that makes it pass, and separately names the review
  layers with their powers and their binding.
- A new layer, `contract-ids`, runs `../tools/contract_ids.py`. It compares the
  contract's layer names against the `run_layer` calls in `tools/gauntlet.sh`
  in both directions, and is a manifest member like any other layer.
- The contract publishes thresholds for artifact-computed rows and powers plus
  binding for review rows. It does not publish, and must never publish, the
  findings a reviewer should look for.
- The checker fails closed: a missing contract section, a contract naming no
  layers, an unreadable file, and a gauntlet with no `run_layer` calls are each
  a failure naming the reason.

### Must NOT do

- Do not list findings, defect classes, or review categories to hunt in the
  contract. A reviewer whose questions are known in advance grades work
  optimised for exactly those questions, and the categories left off the list
  are the ones the author already feared least. Powers and binding are the
  published half; the questions are not.
- Do not let the checker read layer names from anywhere but the contract
  section's **first** table. A spec is full of tables whose first cell looks
  like a layer name, and grading a row that was never in the contract is the
  same defect as missing one. The section's second table lists review layers,
  which are graded by a human and have no `run_layer` call to match. Scoping to
  the first table rather than relying on review-layer names failing the name
  pattern is deliberate: the weaker rule would make this layer depend on how
  someone formats a cell, and report drift that does not exist.
- Do not let an absent or empty contract pass. A check that compares nothing
  agrees with everything.
- Do not add a runtime or development dependency for this layer.

### Setup plan

- Add `tools/contract_ids.py` at the repository root, in the mould of
  `ceiling_ids.py`, and register `contract-ids` in `tools/gauntlet.sh` and the
  manifest in `tools/gauntlet_layers.sh`. Add the contract section to this
  file. Add the layer's row to `evidence.md`'s gauntlet table, update the layer
  count, and rebind.
- No new dependency and no new test file: the checker's controls are its four
  arms, each exercised against a copy, plus one run through the real harness
  with the failure read back from `gauntlet-stamp.txt`.
- Commit cadence: this approved SPEC with the contract first; the checker and
  its registration second; evidence rebinding third.

## REVISION 12: the hooks tier's CI half runs as layers (Tier 3)

Approved 2026-09-10 in the SPEC for track-A2 objects H1 and H2
(`docs/spec-a2-h1-h2.md`, Decide 4). This revision registers three checks over
repository-level artifacts; it does not change rate-limiter runtime behaviour
or its public API.

A2 gives the repository a `hooks/` directory of host-specific bounds, and its
first hook bounds `old-coder-spec-intent`'s `Read`. A hook has a failure mode
no other layer has: delete its handler and Claude Code logs the failure and
carries on, so the bound disappears while every document still claims it. That
is silent from inside the run and needs a check outside it.

These layers are the CI half and nothing more. They prove the handler decides
correctly and that the frontmatter points at a file that exists and runs.
**Neither proves Claude Code calls it.** Only a recorded host probe does, and
it cannot run in CI, which is why `hooks/README.md` carries the procedure and
why the split is named in the layer names rather than left to a reader.

They live here for the same reason `audit-sweep` and `ceiling-ids` do: the
demo's gauntlet is the only runner this repository has. REVISION 10 recorded
that as debt. A2 object H6 pays it, and moves these out with the others.

### Behaviour

- `audit-sweep-controls` runs `../tools/test_audit_sweep.sh`, nine cases over
  fixture agent trees. The sweep's new hooks-tier lift is proven to refuse a
  hook on the wrong tool and a hook covering only one of two defeating tools.
- `hooks-registered` runs `../tools/hooks_registered.py`, which fails when a
  frontmatter names a handler that does not resolve, is not a file, or is not
  executable.
- `hook-controls` runs `../hooks/test_spec_intent_scope.sh`, twelve cases over
  the handler, including a symlink inside the scope pointing out of it and an
  empty payload. Both of those were open in the first draft and were found by
  these controls rather than by review.
- `shell-lint` widens to `../hooks/*.sh` and `../tools/*.sh`. A hook handler is
  the last place to leave a quoting bug unlinted: its failure mode is a tool
  call that proceeds.
- `tools/audit_sweep.py` takes an optional second argument, an agent root, so
  its controls can point it at fixtures. Nothing else should pass it.

## Revision history

Revisions 1–3 (2026-07-25 → 07-27) were made autonomously during the original
build and were never human-approved; the failure model in revision 3 was
retrofitted after implementation. Revision 4 and its amendments (2026-08-09 →
08-10) were approved item by item before implementation, and each amendment
answers a specific finding from an independent verification round. The
per-revision forensics live in `evidence.md` and in git.
