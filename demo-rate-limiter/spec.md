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

## REVISION 9 — prove the trap's wiring; name the stamp's producer (Tier 3)

Drafted 2026-08-30 on an autonomous run (approval pending — nothing beyond
this spec text and the item-6 status edits is implemented until this revision
is approved). Isolation: worktree `worktree-revision-9-pre-audit`.
Destination: this file only; no tracker issue is named and no PR is open, so
nothing is projected. This revision edits the trust chain — the gauntlet's
own completion mechanism and the audit document the next audit is measured
against — hence Tier 3. It does not change rate-limiter runtime behaviour or
its public API.

REVISION 8 proved the stamp and exit vocabulary *in the helper*: scenarios
6–11 source `tools/gauntlet_layers.sh` and call `install_gauntlet_exit_trap`
themselves. None of them invokes `tools/gauntlet.sh`. Delete that call from
the entry point and every layer passes, the run exits 0, no stamp is written,
and the self-test still reports 11/11. The layer manifest proves an absent
*layer* cannot report green; nothing proves an absent *trap* cannot. This
revision closes that wiring gap and three adjacent ones, then makes
`docs/loop-alignment.md` say only what is proven.

### Behaviour

**Item 1 — the wiring control** (new scenario in
`tools/test_gauntlet_orchestration.sh`):

- The self-test inspects the text of `tools/gauntlet.sh` and asserts, in
  order: it sources `tools/gauntlet_layers.sh`; it invokes
  `install_gauntlet_exit_trap` as a command on a later line; the first
  `run_layer` line comes later still; the file defines no function named
  `install_gauntlet_exit_trap`; the file contains no `trap` command of its
  own (the helper owns the trap).
- The control fails closed: an unreadable entry point or a zero-match search
  is a red scenario, never a skip.
- Deleting the `install_gauntlet_exit_trap` line from `tools/gauntlet.sh`
  turns the self-test red, naming the wiring; restoring it turns the
  self-test green. Both runs are observed and recorded in `evidence.md`, not
  argued. Two further mutants are observed red once each during RED: the
  invocation moved after the first `run_layer`, and a same-named no-op
  function defined in the entry point.
- **Route and what it pins.** The control is a static assertion over the
  entry point's text, because the orchestration self-test is layer 1 of the
  gauntlet: it cannot invoke `tools/gauntlet.sh` without recursing, and a
  recursion guard would alter the code under test. It pins the presence and
  order of the wiring tokens and the absence of a local override in the
  entry point. It does not pin runtime semantics (scenarios 6–11 pin those,
  against the real helper — the two controls close the gap only together),
  it does not survive an edit to the helper (already the disclosed limit),
  and it does not defend against deliberate evasion via `eval` or
  indirection — the threat model here is REVISION 8's: accident, not
  coordinated edit.

**Item 2 — the no-stamp exemption becomes mechanical**
(`skills/old-coder/references/templates.md`, Stamp line, plus its fixture):

- The Stamp consistency line's escape hatch — "No stamp mechanism in the
  project — this line does not apply" — is replaced by a condition: the
  exemption applies only when inspection of the *entry point* shows it
  installs no stamp trap. Absence of a stamp file where the entry point
  installs a trap is a **failed** consistency line, never an exemption.
- Per `CONTRIBUTING.md` (skill text is behavior), this ships with a fixture:
  a new self-test scenario exercises the decision rule against two synthetic
  entry points in a temp directory — one that installs no trap, judged
  exempt with no stamp present; one that installs the trap, judged failed
  when no stamp exists after a run. Weakening the rule back to
  "no stamp file → exempt" turns the second case red (observed during RED).

**Item 3 — the stamp names the binding's producer**
(`tools/gauntlet_layers.sh`):

- `write_gauntlet_stamp` records, on the success *and* failure paths of the
  binding: `source_state_cmd:` — the resolved path of
  `$GAUNTLET_SOURCE_STATE_CMD` — and `source_state_cmd_sha256:` — the sha256
  of that file. Where the command does not resolve to a readable file, or no
  sha256 tool is available, the field reads `unavailable (<reason>)`; no
  field is ever guessed. Metadata failure does not by itself fail the run
  (same stance as REVISION 8's unavailable binding, scenario 11).
- Controls: a run with `GAUNTLET_SOURCE_STATE_CMD` overridden produces a
  stamp naming the override's path, with a hash matching an independently
  computed sha256 of that file; a default run's stamp names
  `tools/source_state.sh`.
- The disclosed limit is then restated in `evidence.md` and in
  `skills/old-coder/references/gauntlet.md`: the stamp now makes a
  substituted or overridden binding producer *visible in the stamp*; it
  still does not resist an edit to the helper that writes the stamp, and a
  hash names a file's content without proving that content honest.

**Item 4 — close the pre-trap window** (`tools/gauntlet.sh`):

- The entry point's first act after entering the demo root is writing a
  minimal `result: started` stamp to the stamp path, inline — before any `.`
  source, so it cannot depend on the helper. The `rm -f` of the stale stamp
  is dropped (the write replaces it); the `rm -f` of `.coverage` and
  `coverage.xml` stays. The exit trap overwrites the stamp on every governed
  path, so a stamp still reading `started` after a run means the script died
  before the trap was installed — absence is no longer ambiguous.
- Controls: the item-1 static assertion also pins the order (started-write
  before the first `.` source, before the installer call); the green-run
  scenario pre-seeds the stamp path with `result: started` and asserts the
  finished run stamps green (the trap overwrites); a synthetic replica of
  the preamble whose `.` source fails is observed to exit nonzero leaving
  `result: started`. The replica proves the *pattern* fails the right way;
  the static assertion is what binds the shipped file to that pattern.

**Item 5 — citation sweep, with a premise correction (deviation from the
task prompt, for the approver to rule on):**

- The prompt calls VE-10's citation `tools/source_state.py` fabricated and
  orders it changed to `tools/source_state.sh`. The premise is wrong:
  `demo-rate-limiter/tools/source_state.py` exists and is the
  implementation — `source_state.sh` is a ten-line wrapper that `exec`s it,
  and the manifest-hashing, fail-closed behaviour VE-10's evidence column
  describes lives in the `.py`. Proposed action: **no edit to VE-10**.
- The sweep still runs: every file path cited in `docs/loop-alignment.md` is
  resolved against the tree (audit-doc citations are short names, so a path
  resolves if it exists under the repo root, `skills/old-coder/`, or
  `demo-rate-limiter/`), and the result is reported in the final report and
  in `evidence.md`'s honest notes even if clean.

**Item 6 — status honesty in `docs/loop-alignment.md`, two commits:**

- Commit A, before any item-1 implementation: VE-9, VE-11, CO-9 and CO-10
  read `partial`, each naming the gap: the stamp/exit mechanism landed in
  the helper, and trap installation is untested at the entry point. (The
  rows currently still read `gap → Phase B/D` although those phases landed
  at REVISION 8 — commit A also corrects that staleness; it is the same
  edit.)
- Commit B, after item 1 is green: the four rows flip to `enforced`, citing
  the wiring control as the evidence.
- No other status cell in the document is touched.

**Item 7 — two new rows, fork-local ids:**

- The audit's ids mirror stable ids in a private source document this run
  cannot read, so this is a decision for the approver, not the spec (the
  request allows either): **(a) proposed default** — add the rows under
  fork-local ids, explicitly marked as observed in this fork and not present
  in "Loop engineering" v0.1 as audited, proposed for the doctrine document;
  or **(b)** add no row, and state in the document that both rules belong in
  the doctrine document first. Approving this revision unamended selects
  (a); the row text below implements it.
- `FL-1` (Plane 3): *reachability is proven separately from behavior — a
  mechanism can be implemented, controlled and green while absent from the
  path that would invoke it.* Status `partial`: the layer manifest covers
  layers and the item-1 control covers the exit trap; nothing covers any
  other mechanism.
- `FL-2` (Plane 2, beside EX-3): *a patch and its failing test written by
  one author can be wrong in the same direction; a same-model reviewer
  compresses the same English the same shallow way, and VE-2 does not catch
  it.* Status `gap`: this repo has no mechanism for it, and none is built
  here.

### Investigation (report only, no edits)

`evidence.md` claims 17 gauntlet layers; `GAUNTLET_EXPECTED_LAYERS` holds 13.
Each of the 17 rows is classified — manifest layer, sub-part of a manifest
layer, `n-a`, or work the entry point does not perform (the suite-health
row's 10 consecutive randomized runs are already known to be a separate
rerun; the entry point performs one randomized run via pinned
pytest-randomly). Reported in the final report and the honest notes; the
table is not restructured.

### Failure model (Tier 3)

- *The wiring control guards a spelling, not the property.* Mitigated by
  asserting order and the absence of a local override, and by observing the
  three mutants red; residual evasion (`eval`, indirection) is disclosed,
  not defended.
- *The control is itself fail-open.* Mitigated by fail-closed construction
  (unreadable file or zero matches is red) and by the delete-and-observe
  proof — the RED principle applied to the checker.
- *The started stamp masks a real result if the trap never overwrites.*
  Mitigated by the pre-seeded-stamp overwrite control.
- *The hash fields imply more than they enforce.* Mitigated by restating the
  disclosed limit in both documents (item 3) rather than only adding the
  mechanism.
- *The audit document drifts from the mechanisms again.* Mitigated by the
  two-commit ordering in item 6 and by touching no other status cell.

### Must NOT do

- Do not change the return statuses of `run_layer` or `finish_gauntlet`, and
  do not break any of the eleven existing orchestration scenarios.
- Do not write any stamp field the run did not produce; `unavailable` with a
  reason is the only fallback.
- Do not touch any `docs/loop-alignment.md` status cell outside items 6
  and 7.
- Do not widen coverage or mutation targets across `tools/`.
- Do not add a runtime or development dependency.
- Do not start the out-of-scope work: the versioned loop-alignment index,
  Phase C (adversary hardening, budgets, brief-path downgrade), or any
  upstream cut.

### Setup plan

- Files modified: `demo-rate-limiter/tools/gauntlet.sh`,
  `demo-rate-limiter/tools/gauntlet_layers.sh`,
  `demo-rate-limiter/tools/test_gauntlet_orchestration.sh`,
  `skills/old-coder/references/templates.md`,
  `skills/old-coder/references/gauntlet.md`, `docs/loop-alignment.md`,
  `demo-rate-limiter/spec.md` (this section),
  `demo-rate-limiter/evidence.md` (rebind, last). No files added or
  deleted.
- No new dependency; sha256 comes from `sha256sum`/`shasum`, already present
  on the platforms CI and the demo run on, with `unavailable` as the
  fail-closed fallback.
- Commit cadence: (1) this spec at approval; (2) item 6 commit A;
  (3) RED controls, observed failing; (4) implementation to green;
  (5) skill-text edits (items 2 and 3's limit wording) with their fixtures;
  (6) item 6 commit B, item 7 rows, item 5 sweep note; (7) evidence rebind
  after a final fresh gauntlet run. Commits signed.
- Isolation: worktree. Nothing is pushed and no PR is opened.

## Revision history

Revisions 1–3 (2026-07-25 → 07-27) were made autonomously during the original
build and were never human-approved; the failure model in revision 3 was
retrofitted after implementation. Revision 4 and its amendments (2026-08-09 →
08-10) were approved item by item before implementation, and each amendment
answers a specific finding from an independent verification round. The
per-revision forensics live in `evidence.md` and in git.
