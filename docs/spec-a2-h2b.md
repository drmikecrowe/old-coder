# SPEC - H2b. The reviewer's scope, taken from the artifact directory

Cut from H2's recorded residual limit. H1 and H2 landed; their SPEC and the
record of their review rounds are at `docs/spec-a2-h1-h2.md`.

House rule: no em dashes.

> **LANDED** 2026-09-11 at `47dc328`, after one adversarial round. The `Decide`
> below was answered yes and is kept as written; outcomes are in `## Revisions`.
> Nothing here is an open question.

## Orientation

- **Change:** `hooks/spec-intent-scope.sh` takes its scope from a pointer file
  under `.old-coder/`, written when the task's artifact directory is created.
  `OLD_CODER_SPEC_DIR` is removed.
- **Why:** H2 proved the bound and left it unwired. A hook inherits the
  environment of the `claude` process, fixed before the session starts, and the
  artifact directory is named at SPEC time inside the session, so an
  environment variable cannot express it. The probe worked only because a fixed
  directory was pre-created and exported by hand.

  The second reason is worse than the first. `old-coder-spec-intent`'s brief
  tells it to use **no tools at all** in the normal case, because the documents
  are in its prompt. So an unset scope produces a handler that denies
  everything, a reviewer that reads nothing and notices nothing, and a review
  that looks completely normal. You would hold a deny-all that never fires
  while believing you held a path-scoped bound. Safe, invisible, and exactly
  the shape this repository keeps being caught by.

- **Touches:**
  - `hooks/spec-intent-scope.sh`, `hooks/test_spec_intent_scope.sh`
  - `hooks/README.md`, `hooks/probes/RUNBOOK.md`
  - `tools/audit_sweep.py`, `tools/test_audit_sweep.sh` (see Decide 3)
  - `skills/old-coder/SKILL.md` (one clause at line 227),
    `skills/old-coder/references/setup.md` (layout, and the tracked/ignored
    table)
  - `.gitignore`
  - `demo-rate-limiter/spec.md` REVISION 13
  - `docs/loop-alignment.md`, `skills/old-coder/references/ceiling.md`,
    `docs/track-a2.md`
- **Decide:** one, and it is scope growth you may want to cut. See below.

### Settled before drafting, recorded rather than re-asked

- **The pointer lives under `.old-coder/`**, which `references/setup.md` line 67
  already establishes as the artifact root, so it sits beside the dated task
  directories it points into. Project-scoped, so two checkouts do not collide.
- **`OLD_CODER_SPEC_DIR` is removed, not deprecated.** Two sources of scope
  means two ways to misconfigure and two things a reader must check.
- **`SKILL.md` is amended in place**, a clause on the existing
  artifact-directory instruction at line 227, with the mechanics in
  `references/setup.md`. Strict in-one-out-one waived.

### Design that follows from those, stated so it can be objected to

`.old-coder/scope`: one line, an absolute path, trailing whitespace stripped.
One line rather than a format, because anything richer invites a parser, and a
parser inside a fail-closed handler is a second thing that can be wrong.

The handler finds `.old-coder/` by walking up from the payload's `cwd`, the way
git finds `.git`, stopping at the filesystem root. That survives a reviewer
whose cwd is a subdirectory, which a fixed relative path would not.

Two absences are distinguished in the denial reason, because they mean
different things to whoever reads the transcript: no `.old-coder/` found at all
(no task in progress), and `.old-coder/` found with no readable `scope` (a task
is in progress and the pointer step was skipped). Both deny.

### Decide. Scope growth: probe records must bind to the handler

**This object invalidates the probe that proved H2, and nothing currently
notices.** `tools/audit_sweep.py` lifts EX-1 when a file exists under
`hooks/probes/` whose stem matches the handler. It does not check that the
probe was run against *this* handler. So changing `spec-intent-scope.sh` leaves
a stale record standing, and EX-1 keeps reading `enforced` on the strength of a
run against different code. `hooks/README.md` already says to rebind on every
hook change; that sentence is prose, and this is the object that finds out.

Proposal: a probe record carries the handler's sha256, and the lift requires a
record whose recorded hash equals the current handler's. Change the handler and
every existing record stops counting, so the gauntlet goes red until a fresh
probe is recorded.

Roughly twenty lines in `audit_sweep.py` plus two controls. **Cut it and H2b
still works**, but the probe gate stays a gate against deletion only, not
against staleness, and the rebind rule stays prose. My recommendation is to
take it, because the hole is one I introduced in H2 and this is the first
change that would have walked through it.

The contract below, in brief:

- **Covers:** the pointer, its discovery, the handler's fail-closed paths, the
  skill's write step, and probe freshness if Decide 3 is taken.
- **Must NOT:** a second source of scope survives; the pointer is tracked; a
  stale probe keeps lifting EX-1; `SKILL.md` gains a section.
- **Out of scope:** everything from H3 onward. Nothing about
  `old-coder-adversary` or bounding `Bash`.

- Tier: 3. It changes what an agent can do.
- Issue: none
- Artifact dir: this file, `docs/spec-a2-h2b.md`.
- Isolation: none, as H1 and H2. One commit for the object.
- Artifacts: file only.
- Setup plan:
  - Merge gate: `.github/workflows/`, the demo gauntlet on push.
  - Tools to install: none.
  - Git: one signed commit carrying the `docs/track-a2.md` rows, then the
    evidence rebind, then the probe record when it arrives.
  - Files the gauntlet will add, by path: none. `hook-controls` and
    `audit-sweep-controls` already exist and absorb the new cases.
  - New dependencies: none.

## Scenarios

```gherkin
Feature: the reviewer's scope comes from the artifact directory
  Scenario: a source file outside the scope is denied
    Given .old-coder/scope names an existing directory D
    And   the payload cwd is inside the repository
    When  the handler receives a Read for a path outside D
    Then  it denies, and the reason names the path

  Scenario: a file inside the scope is allowed
    Given the same
    When  the payload names a file that resolves inside D
    Then  it does not deny

  Scenario: the pointer names a directory created after the session started
    Given the session began with no .old-coder/ at all
    And   the skill then created .old-coder/20260911-101500-widget/ and wrote
          the pointer to it
    When  the handler receives a Read for that directory's SPEC.md
    Then  it does not deny
    And   this is the case an environment variable could not express

  Scenario: no artifact root found
    Given no .old-coder/ exists at or above the payload cwd
    When  the handler runs
    Then  it denies, and the reason says no task is in progress

  Scenario: artifact root present, pointer missing
    Given .old-coder/ exists and holds no readable scope file
    When  the handler runs
    Then  it denies, and the reason says the pointer step was skipped
    And   the two reasons are distinguishable in a transcript

  Scenario: the pointer names something that is not a directory
    Given .old-coder/scope names a regular file
    When  the handler runs
    Then  it denies

  Scenario: a pointer with trailing whitespace still resolves
    Given .old-coder/scope holds D followed by a newline and spaces
    When  the handler runs against a file inside D
    Then  it does not deny

  Scenario: the escape cases from H2 still hold
    Given a valid pointer
    When  the payload names D/../outside.txt, or a symlink inside D pointing out
    Then  it denies in both cases

Feature: a probe record stops counting when the handler changes
  Scenario: the recorded hash matches
    Given hooks/probes/ holds a record naming the current handler's sha256
    When  tools/audit_sweep.py runs over an audit where EX-1 reads enforced
    Then  it exits 0

  Scenario: the handler changed since the probe
    Given every record names a different sha256
    When  the sweep runs
    Then  it exits 1 and says the probe predates the current handler
```

## Must NOT

- No second source of scope. Nothing reads `OLD_CODER_SPEC_DIR` after this.
- The pointer is gitignored. A tracked pointer would be committed pointing at
  one machine's directory and would be wrong on every other.
- The handler must not grow a parser. One line, one path, strip whitespace.
- The walk-up must terminate at the filesystem root and must not follow the
  pointer outside its own resolution.
- `SKILL.md` gains a clause on the existing artifact-directory instruction, not
  a new bullet or section.
- No em dash in authored prose. Verbatim quoted transcripts keep their own
  punctuation.
- Nothing in `agents/old-coder-adversary.md` is touched.

## Verification contract

The 21 computed layers from H2's contract, unchanged, all exit 0. The new cases
land inside `hook-controls` and `audit-sweep-controls` rather than adding
layers, so `contract-ids` still names 21.

| Row                    | What it proves                                                | Threshold                                                             |
| ---------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------- |
| `hook-controls`        | the handler's decisions, including the five fail-closed paths | all cases pass; the driver reports a failure against a broken handler |
| `audit-sweep-controls` | the lift refuses a stale probe as well as a missing one       | all cases pass                                                        |

Host rows, which cannot run in CI:

| Row              | What it proves                                                       | Who runs it                        |
| ---------------- | -------------------------------------------------------------------- | ---------------------------------- |
| negative control | the handler denies a source read, with the pointer as the only scope | Mike                               |
| positive control | a read inside the pointed directory succeeds                         | Mike                               |
| freshness        | the new record names the current handler's sha256, so it counts      | derived, then checked by the sweep |

**The H2 probe record is superseded by this object and must be removed or
re-run.** It proves env-var behaviour against a handler that no longer exists.
Leaving it in place while EX-1 reads `enforced` would be the stale-evidence
defect, which is why Decide 3 exists.

Review layers: human SPEC approval, and one adversarial round bound to the
object's commit range with the tree hash recorded.

**Honest limit, carried forward rather than closed.** Even after this, a run in
which the pointer was never written produces a reviewer that reads nothing and
reports normally, because its brief tells it to use no tools. The denial reason
distinguishes the cases for anyone reading a transcript, but nothing in a
normal run is obliged to read one. Closing that needs the reviewer to assert it
could reach its own SPEC, which is a change to the brief and a different
object. Stated here so H2b is not read as closing it.

## Revisions

- Initial draft, 2026-09-11, from H2's recorded residual limit.
- 2026-09-11, approved with the `Decide` taken: probe records bind to the
  handler's sha256. RED for it was concrete rather than argued: appending a
  comment to the handler left the existing record standing and the sweep passed.
- 2026-09-11, adversarial round one, bound to `0899bd0...3bf9a2e` at tree
  `0f6d9e8aa98315ec`, handler sha256 `0fc7bb66...`. Three findings, two upheld
  and one rejected with evidence, 5 of 10 tool calls used.
  1. **The freshness check proved a hash, not an attribution.** It searched for
     any 64 hex characters within 24 non-hex characters of the word "sha256", so
     a superseded record that merely mentioned the current handler lifted the
     row. The hash is now declared on its own line in one form, and a record
     declaring two different hashes contributes nothing. The reviewer's own
     example did not reproduce, because its separator text contained `b`, `e`
     and `d`, which the pattern excludes as hex; the reasoning was right and the
     example accidentally wrong, so it was reproduced with a hex-free separator
     before anything was changed.
  2. **The payload's `cwd` was not required to be absolute.** `readlink -f`
     resolves a relative path against the handler's own process directory, so a
     payload carrying `.` would find the launch directory's artifact root and
     enforce some other task's scope. Now fails closed.
  3. **Rejected:** the claim that the `case` pattern glob-expands when the scope
     path holds metacharacters. Quoted text in a `case` pattern is literal; a
     scope of `/tmp/spec[dir]` denies `/tmp/specdir/leak.txt`. Demonstrated.
  The round ran out of budget before attack 6, the workflow half, and that
  attack held a live defect. Under worktree isolation `setup.md` sends every
  gitignored artifact to the durable root while `SPEC.md` goes to the worktree.
  The pointer is gitignored, so it would have landed in the durable root while
  the reviewer's cwd is the worktree: the walk-up finds the worktree's artifact
  root, sees no pointer, and denies every read. `scope` is now the one ignored
  artifact written in the worktree. H2b round two of two; no signature repeated.
- 2026-09-11, at landing. The freshness check rejected the probe record I wrote,
  correctly: the declaration was a list bullet and the pattern requires the line
  to begin with the key. Since every other metadata field in a record is a
  bullet, the pattern now accepts an optional list marker, with a control for
  that form and the mention-only attack re-run under it. Host probe passed at
  tree `0f6d9e8aa98315ec`; EX-1 is `enforced`.
- 2026-09-11, before approval. The first draft listed three `Decide` items, two
  of which Mike had already answered. `templates.md` reserves that field for
  the calls you want ruled on, so re-asking a settled question pads the thing
  the approver has to read and buries the one item still open. The answers
  moved to a Settled block and one `Decide` remains.
