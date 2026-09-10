# SPEC - Track A2, objects H1 and H2

Two objects, two SPECs, one approval gate. The loop in `docs/track-a2.md`
runs them in order: H1 lands, then H2. Budget is two rounds per object; the
same failure signature twice is a stable failure recorded here, not a third
attempt.

House rule: no em dashes.

---

# SPEC - H1. Amend the freeze

## Orientation

- **Change:** `CONTRIBUTING.md` gains the hooks tier as a named, wider
  exception to the freeze, with its test and its retained boundary, and
  `docs/track-a.md`'s A6 log entry gains one line pointing at
  `docs/track-a2.md`.
- **Why:** the freeze permits exactly one shape today: "an **opt-in**
  mechanism may ship as a documented snippet a reader applies deliberately,
  never as a default in a shipped agent or config file." H2 ships exactly
  that default, in `skills/old-coder/agents/old-coder-spec-intent.md`. Every
  A2 object from H2 onward violates the written rules until this lands.
- **Touches:** `CONTRIBUTING.md` (section "What belongs here, and what does
  not"), `docs/track-a.md` (the A6 log entry at line 522), `docs/track-a2.md`
  (status table). No code, no agent files, no audit rows.
- **Decide:**
  1. Whether the tier extends the existing exception paragraph or gets its
     own subsection. Recommendation: its own subsection, because the
     existing paragraph's last sentence ("A default that silently does
     nothing on the reader's host is worse than a stated instruction") is
     the reason the tier must be opt-in for a portable reader, and it should
     stay attached to the snippet shape rather than be rewritten.
  2. The exact wording for the fork-default half. The current text forbids a
     default in a shipped agent file **by name**, and this fork's deployment
     symlinks `~/.claude/agents/*.md` straight at the tracked files, so the
     shipped file and the deployed file are one file here. The amendment has
     to say that plainly rather than leave a reader to discover it.
  3. Whether the boundary sentence names the runtime repo. `592d0c3` deliberately
     stopped naming the successor repo and made rule ids the join. The
     amendment should follow that, not undo it.

The contract below, in brief:

- **Covers:** the tier's definition, its test, the retained boundary, the
  freeze's original test kept verbatim, and the track-a.md pointer.
- **Must NOT:** the original test for skill text changes meaning; the audit
  vocabulary gains a qualifier; an em dash appears.
- **Out of scope:** any hook file, any agent frontmatter, any audit or
  ceiling row. H1 is prose only. It authorises H2; it does not do H2.

- Tier: 2
- Issue: none
- Artifact dir: this file, `docs/spec-a2-h1-h2.md`, per the track-A
  precedent for prose objects (no dated artifact directory was used for A2,
  A5, A6 or A7).
- Isolation: none. Working directly on `main`, as track A did, with a
  checkpoint commit per object.
- Artifacts: file only.
- Setup plan:
  - Merge gate: `.github/workflows/` runs the demo gauntlet on push. No
    check in it has no layer counterpart, because it invokes the gauntlet.
  - Tools to install: none.
  - Git: checkpoint commit at the end of H1, signed, with the
    `docs/track-a2.md` status row in the same commit.
  - Files the gauntlet will add, by path: none.
  - New dependencies: none.

## Scenarios

H1 changes documents, so its scenarios are assertions over document state.
Each is checkable by a human reading a diff. None is mechanically gated, and
that is stated rather than papered over: see "Honest limit" below.

```gherkin
Feature: the freeze admits a hooks tier
  Scenario: a contributor reads the freeze and learns what hooks/ is
    Given CONTRIBUTING.md's section "What belongs here, and what does not"
    When  a reader reaches the exception
    Then  the text names hooks/ as a tier for host-specific bounds
    And   states that it is opt-in for a portable reader and on by default
          in this fork's own deployment
    And   states the tier's test: a hook ships with a control that proves it
          denies, and the skill text never claims what only a hook enforces
    And   states the retained boundary: outer-loop mechanisms are still out
          of scope here, by rule id rather than by repo name

  Scenario: the original test for skill text survives verbatim
    Given the sentence "The line is not \"small versus large\". It is whether
          an agent that can only *read* the text can honour the change."
    When  the amendment lands
    Then  that sentence is present, character for character, unmoved in meaning

  Scenario: the freeze log shows an amendment, not a contradiction
    Given docs/track-a.md's A6 log entry, which ends "The one exception is
          the opt-in shape EX-1 just established."
    When  a reader reaches that line
    Then  one added line points at docs/track-a2.md and says the exception was
          widened into a tier there
    And   the original A6 text is unedited, matching A6's own precedent of
          leaving a superseded claim in place with a note

  Scenario: the audit vocabulary is untouched
    Given docs/loop-alignment.md and skills/old-coder/references/ceiling.md
    When  H1 lands
    Then  neither file is modified
    And   tools/ceiling_ids.py exits 0, unchanged from before
```

## Must NOT

- The freeze's test for skill text is not reworded, softened, or moved.
- No status vocabulary anywhere gains a qualifier such as
  `enforced (on one host)`. That is the CO-8 defect.
- `CONTRIBUTING.md` does not claim the tier enforces anything on a host that
  does not have it.
- No em dash in any changed line.
- No file outside the three named in **Touches** is modified.

## Verification contract

Filled before anything runs. Layer names are exactly as
`demo-rate-limiter/tools/gauntlet.sh` invokes them.

| Layer | What it gates | Threshold |
|---|---|---|
| orchestration-self-test | the runner reports what it ran | exit 0 |
| checker-self-test | the home-grown checkers can fail | exit 0 |
| source-state-self-test | binding fails closed | exit 0 |
| tests-coverage | demo regressions | exit 0, 100% branch |
| types | demo regressions | exit 0 |
| lint-format | demo regressions | exit 0 |
| shell-lint | demo regressions | exit 0 |
| supply-chain | demo regressions | exit 0 |
| must-not-scans | credentials and real time in the demo | exit 0 |
| mutation-control | the mutation layer is non-vacuous | exit 0 |
| mutation | demo regressions | exit 0, all mutants killed |
| real-execution | the demo runs | exit 0 |
| audit-sweep | an audit row crediting a bound its agent cannot hold | exit 0 |
| ceiling-ids | audit and ceiling naming different end states | exit 0 |
| contract-ids | the demo contract and the runner disagreeing | exit 0 |
| source-state | content identity | exit 0 |
| evidence-binding | evidence bound to a stale tree | exit 0 |

Manual rows, graded by reading, not computed:

| Row | What it gates | Threshold |
|---|---|---|
| vocabulary sweep | banned wording in changed files, per `ROADMAP.md` step 7 | 0 hits |
| em-dash sweep over changed lines | the house rule | 0 hits |
| verbatim check on the freeze's skill-text test | Must NOT #1 | exact match |

Review layers:

| Layer | Powers | Binding |
|---|---|---|
| human SPEC approval | full; the only approver | this file at its approved content |
| adversarial | `old-coder-adversary`: Read, Bash, Grep, Glob; one round; 10 calls | `base...HEAD` for H1's commit, tree hash from `tools/source_state.sh` |

Exit vocabulary: 0 green, 2 a layer ran and failed, 3 the orchestration
contract was violated, anything else a crash passed through.

**Honest limit, stated rather than discovered later.** Every layer in the
first table is a demo layer plus three repository checks, and none of them
reads `CONTRIBUTING.md`. A green gauntlet after H1 proves that H1 broke
nothing. It does not prove H1 is right. The rows that grade H1 are the
manual ones and the human. Writing a grep gate over `CONTRIBUTING.md` would
be the "gate that failed closed perfectly while guarding a spelling" defect
named in `CONTRIBUTING.md` itself, so it is deliberately not proposed.

Also: `skills/` and `docs/` sit outside the source manifest, so the
adversarial round for H1 binds to a tree hash that did not move. That is
`ceiling.md`'s published limit, and it applies here. The binding is recorded
with that fact attached.

## Revisions

- Initial draft, 2026-09-10, from `docs/track-a2.md` H1's acceptance criteria.

---

# SPEC - H2. The spec reviewer's read scope

## Orientation

- **Change:** the `PreToolUse` snippet in `references/ceiling.md` becomes a
  real, executable hook file in `hooks/`, wired into
  `old-coder-spec-intent`'s frontmatter in this fork, proven by a recorded
  deny and a recorded allow on the host, with EX-1 moving to a single-valued
  end state in both the audit and the ceiling.
- **Why:** EX-1. `old-coder-spec-intent` declares `tools: Read`, the host's
  floor, and `Read` opens any file. "Do not go looking for the codebase" is
  instruction. On Claude Code it can be capability.
- **Touches:**
  - new `hooks/spec-intent-scope.sh`
  - new `hooks/README.md` (what the tier is, how to take it, both halves of
    every control)
  - `skills/old-coder/agents/old-coder-spec-intent.md` (frontmatter)
  - `skills/old-coder/references/ceiling.md` (the snippet becomes a pointer;
    the EX-1 row leaves the table; the "why this does not generalise to
    VE-1" paragraph keeps its point and loses its stale framing)
  - `docs/loop-alignment.md` (EX-1's status and evidence; EX-4's
    cross-reference to EX-1, which currently says the instruction "is scored
    at EX-1")
  - `tools/audit_sweep.py` plus a control for it (see Decide 3)
  - `demo-rate-limiter/tools/gauntlet.sh`, `demo-rate-limiter/spec.md`
    (see Decide 4)
  - `docs/track-a2.md` (status table, same commit)
- **Decide:** four calls, and the first three are blocking.

### Decide 1. How the hook command resolves its own path

The ceiling's snippet writes
`${CLAUDE_PROJECT_DIR}/.claude/hooks/spec-intent-scope.sh`.
`CLAUDE_PROJECT_DIR` is the project the agent is working on, not this repo.
`old-coder` is a skill that runs on other people's repositories, so on every
run except one, that path does not exist, the hook fails to start, and
Claude Code's normal permission flow continues. That is the fail-open the
whole tier exists to prevent, shipped as the default.

Three options:

| Option | Works when | Cost |
|---|---|---|
| absolute path to this checkout | always, on this machine | a machine-specific path in a tracked file that other readers inherit |
| `$HOME/.claude/hooks/spec-intent-scope.sh`, symlinked at the repo file | always, on this host | one setup step, and it matches how `~/.claude/agents/` already symlinks at `skills/old-coder/agents/` |
| keep `${CLAUDE_PROJECT_DIR}` | only when old-coder runs on old-coder | the bound is absent on every real use |

Recommendation: the symlink. It reuses a deployment shape this host already
uses, keeps the tracked file portable, and makes the setup step explicit
rather than implicit.

**Unresolved even after choosing.** If the script is missing or not
executable, Claude Code does not deny; it carries on. The hook can fail
closed on its own inputs, and will. It cannot fail closed on its own
absence. That limit is written into `hooks/README.md` and into the ceiling,
not claimed away, and it is the reason the registration check in Decide 4
exists.

### Decide 2. How the hook learns which directory is "the spec's own directory"

The artifact directory is per-task and dated, so no path can be baked in.

| Option | Decidable | Fails closed |
|---|---|---|
| `OLD_CODER_SPEC_DIR` env var, deny everything when unset or not a directory | yes | yes |
| infer from the hook payload's `cwd` | no; cwd is the repo, which is the thing being denied | no |
| allow any directory containing a `SPEC.md` | no; a repo may contain many | no |

Recommendation: the env var. Deny by default, allow by resolved path prefix,
and an unset variable denies everything rather than allowing everything.
Path comparison is on the fully resolved path, so `..` and symlinks cannot
walk out.

### Decide 3. `audit_sweep.py` must learn about hooks, or EX-1 cannot read `enforced`

This is the blocking one and it is not optional.

`tools/audit_sweep.py` fails any row that reads `enforced` for a
"no-codebase" bound when the agent it names declares a tool in `READER`,
which includes `Read`. After H2, EX-1's row names `old-coder-spec-intent`,
reads `enforced`, and that agent still declares `tools: Read`, because the
hook bounds the tool rather than removing it. The sweep would call the true
claim an overclaim.

The sweep's model is "the tool list is the bound". H2 introduces a second
bound at a lower layer, so the model has to widen: a row may read `enforced`
for a bound its agent's tool list defeats **when that agent's frontmatter
declares a `PreToolUse` hook matching the defeating tool**. Nothing weaker.
The lift must require an actual matcher on an actual tool name, or the
sweep becomes a check that any agent can silence by mentioning hooks.

This gains its own negative control: a row reading `enforced` for an agent
whose frontmatter has no such hook still fails, and a row whose hook matches
a different tool still fails.

### Decide 4. Scope call: does H2 ship the CI half

`docs/track-a2.md` discipline 1 splits every hook control into a host half
and a CI half, and the track's gauntlet row table lists "hook parse and
registration checks (CI half)". H6 builds the repo-level runner that should
own it. H2 can either ship that check now, into the demo gauntlet beside
`audit-sweep` and `ceiling-ids` under REVISION 10's recorded debt, or leave
it to H6.

Recommendation: ship it now, as a layer named `hooks-registered`, because a
hook whose absence is silent is the exact failure Decide 1 leaves open, and
H6 is four objects away. Shipping it requires `demo-rate-limiter/spec.md`
REVISION 12 so `contract-ids` stays green, which is one more file in the
commit and is stated here rather than discovered at GREEN.

Cut it if you would rather H2 stay small. Say so at approval and the SPEC is
revised in place.

The contract below, in brief:

- **Covers:** the hook file and its behaviour, its registration, the two
  host controls, the ceiling and audit updates, the sweep's widening.
- **Must NOT:** deny by default is not inverted; the skill text does not
  claim what only the hook enforces; no qualified end state; the sweep's
  lift cannot be triggered by prose.
- **Out of scope:** anything about `old-coder-adversary` or `Bash`. That is
  H3, and H2 does not touch it. Nothing from H3 onward.

- Tier: 3. It changes what an agent can do.
- Issue: none
- Artifact dir: this file.
- Isolation: none, matching H1 and track A. Checkpoint commit per object.
- Artifacts: file only.
- Setup plan:
  - Merge gate: `.github/workflows/`, the demo gauntlet on push.
  - Tools to install: none. `shellcheck` is present at `/usr/bin/shellcheck`.
  - Git: one commit for H2, signed, carrying the `docs/track-a2.md` status
    row.
  - Files the gauntlet will add, by path: `hooks/spec-intent-scope.sh` (new),
    `hooks/README.md` (new), `tools/test_audit_sweep.sh` (new control for
    Decide 3; `tools/audit_sweep.py` currently has no self-test of its own).
    `demo-rate-limiter/tools/gauntlet.sh` gains one `run_layer` line if
    Decide 4 is taken.
  - New dependencies: none.

## Scenarios

```gherkin
Feature: the spec reviewer cannot read the source tree
  Scenario: a source file is denied
    Given OLD_CODER_SPEC_DIR is set to an existing directory D
    And   the hook receives a PreToolUse payload for tool Read with
          file_path "demo-rate-limiter/src/ratelimiter/limiter.py"
    When  the hook runs
    Then  it prints JSON with permissionDecision "deny"
    And   the permissionDecisionReason names the path and says the reviewer
          reads the request and the spec, nothing else
    And   it exits 0, because a nonzero exit is not a denial

  Scenario: a file inside the spec directory is allowed
    Given OLD_CODER_SPEC_DIR is set to an existing directory D
    And   the payload's file_path resolves to D/SPEC.md
    When  the hook runs
    Then  it does not deny

  Scenario: an unset scope denies everything
    Given OLD_CODER_SPEC_DIR is unset
    And   the payload's file_path is D/SPEC.md, which would otherwise be allowed
    When  the hook runs
    Then  it denies
    And   the reason says the scope variable was not set

  Scenario: a path that escapes the scope is denied
    Given OLD_CODER_SPEC_DIR is set to D
    And   the payload's file_path is "D/../src/limiter.py"
    When  the hook runs
    Then  it denies, because the comparison is on the resolved path

  Scenario: malformed input denies
    Given the hook receives stdin that is not valid JSON
    When  the hook runs
    Then  it denies
    And   the reason says the payload could not be read

Feature: the host proves the hook, because only the host can
  Scenario: the recorded negative control
    Given the hook is registered in old-coder-spec-intent's frontmatter
    When  the reviewer is spawned and asked to read a source file
    Then  the reviewer reports that it could not
    And   the denial text is recorded verbatim in evidence, with the date,
          the tree hash, and the exact commands run

  Scenario: the recorded positive control
    Given the same registration
    When  the reviewer is spawned and asked to read the SPEC in its own directory
    Then  it succeeds and quotes the file
    And   the success is recorded the same way, so the hook is proven to
          allow as well as deny

Feature: the audit and the ceiling move together
  Scenario: EX-1 ends single-valued
    Given docs/loop-alignment.md and references/ceiling.md
    When  H2 lands
    Then  EX-1's status cell is one word from the closed vocabulary, with no
          parenthetical
    And   the host scoping lives in the evidence column: bounded on Claude
          Code via hooks/, instruction-only elsewhere
    And   EX-1 no longer appears in the ceiling's table, because the ceiling
          lists what is not enforced
    And   tools/ceiling_ids.py exits 0

  Scenario: the sweep does not credit a hook that is not there
    Given an agent frontmatter with no PreToolUse hook
    And   an audit row reading enforced for a no-codebase bound naming it
    When  tools/audit_sweep.py runs
    Then  it exits 1 and names the row

  Scenario: the sweep does not credit a hook on the wrong tool
    Given an agent frontmatter whose PreToolUse matcher is Bash
    And   an audit row reading enforced for a no-codebase bound on Read
    When  tools/audit_sweep.py runs
    Then  it exits 1
```

## Must NOT

- The hook must not allow by blocklist. Deny is the default branch and the
  allow is a single resolved-prefix test.
- The hook must not exit nonzero to mean "deny". It prints the decision and
  exits 0; an error exit leaves the normal permission flow running.
- `SKILL.md` and the agent brief must not claim the reviewer cannot reach
  the codebase as a fact about every host. The brief's existing prose stays
  prose, and the frontmatter carries the bound.
- No audit or ceiling cell gains a qualifier. The scoping goes in evidence.
- `audit_sweep.py`'s new lift must not be satisfiable by prose in the
  frontmatter. It requires a parsed `PreToolUse` matcher naming the tool.
- No em dash.
- Nothing in `agents/old-coder-adversary.md` is touched. That is H3.

## Verification contract

The computed table is H1's, unchanged, plus one row if Decide 4 is taken:

| Layer | What it gates | Threshold |
|---|---|---|
| (all seventeen layers from H1's table) | as above | as above |
| hooks-registered (only if Decide 4 is taken) | a hook file that does not parse, or that no frontmatter references | exit 0 |

Host rows. These cannot run in CI, and the split is stated in the control
itself so nobody reads the CI half as the proof:

| Row | What it proves | Threshold | Who runs it |
|---|---|---|---|
| negative control probe | the hook denies a source read | denial recorded verbatim | Mike, at the keyboard |
| positive control probe | the hook allows inside the spec dir | success recorded verbatim | Mike, at the keyboard |
| rebinding | both probes belong to this hook version | rerun on every hook change, tree hash recorded | Mike |

Unit rows, which run anywhere and prove the script's own logic, never its
registration:

| Row | What it proves | Threshold |
|---|---|---|
| `tools/test_audit_sweep.sh` | the sweep's hook lift is not vacuous | exit 0, two controls fail as designed |
| the hook's own five scenarios, driven by piping payloads to the script | deny by default, allow by path, fail closed | all five |

Review layers:

| Layer | Powers | Binding |
|---|---|---|
| human SPEC approval | full | this file at its approved content |
| adversarial | `old-coder-adversary`: Read, Bash, Grep, Glob; one round; 10 calls | `base...HEAD` for H2's commit, tree hash from `tools/source_state.sh` |

Exit vocabulary: as H1.

**Honest limit.** A passing unit row proves the script decides correctly. It
does not prove Claude Code calls it. Only the host probes prove that, and
they are the reason H2 stops and waits rather than reporting a result.
Nothing in this SPEC lets a green gauntlet stand in for a recorded denial.

## Revisions

- Initial draft, 2026-09-10, from `docs/track-a2.md` H2's acceptance
  criteria.
- 2026-09-10, during GREEN. Three files were added that the setup plan did not
  name by path, and an unnamed script is the thing `setup.md` warns about, so
  they are named here instead of silently: `hooks/test_spec_intent_scope.sh`
  (the handler's twelve controls), `tools/agent_frontmatter.py` (one frontmatter
  reader, so `audit_sweep.py` and `hooks_registered.py` do not grow two), and
  `hooks/probes/README.md` (the format for the recorded host probes).
  `tools/hooks_registered.py` was named in Decide 4 but not in the setup plan.
- 2026-09-10, during GREEN. Decide 1 is resolved a third way, better than the
  three the SPEC listed. `$HOME/.claude` is wrong under this harness:
  `CLAUDE_CONFIG_DIR` is set to a different path entirely. The frontmatter uses
  `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`, which is correct here and on a stock
  install, with the symlink as the SPEC recommended.
- 2026-09-10, during GREEN. Two layers were added beyond Decide 4's single
  `hooks-registered`: `hook-controls` and `audit-sweep-controls`. A control
  script nothing runs is the F3 defect class, and both were written to satisfy
  acceptance criteria that already existed. `shell-lint` widened to cover them.
  Demo `spec.md` REVISION 12 carries all of it; the contract now names 20
  layers.
- 2026-09-10, during GREEN. **H2 splits into two commits.** The SPEC assumed
  one commit carrying both the mechanism and EX-1's move to `enforced`. That
  ordering writes the claim before the proof exists: the evidence column would
  cite host probes that had not been run. Commit one lands the mechanism with
  EX-1 held at `accepted`, the reason stated in the row itself. Commit two
  moves EX-1 after the recorded probes land in `hooks/probes/`. The acceptance
  criteria are unchanged; only their order is.

---

## What I need from you

1. **Approve or revise both SPECs.** RED does not start until you do.
2. **Decide 1** for H2: symlink, absolute path, or leave it project-scoped.
   My recommendation is the symlink.
3. **Decide 2**: the `OLD_CODER_SPEC_DIR` env var. My recommendation is yes.
4. **Decide 3** is not a choice, it is a dependency: `audit_sweep.py` widens
   or EX-1 stays where it is. Confirm you want the sweep widened.
5. **Decide 4**: ship the `hooks-registered` CI half in H2, or leave it to
   H6. My recommendation is ship it.

When H2 reaches its controls I will prepare the two probes, give you the
exact commands, and wait for what you paste back. I will not write either
result myself.
