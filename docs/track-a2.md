# Track A2: the hooks tier

The plan for unfreezing `drmikecrowe/old-coder` and making it whole for the
host it runs on daily, without breaking the portable claim track A closed on.
Companion to `docs/track-a.md` (closed), `docs/loop-alignment.md` (the audit
these objects move), and `CONTRIBUTING.md` (the freeze this track amends).

House rule inherited from the source material: no em dashes.

## What A2 is, and what it is not

Track A froze the repo because a mechanism cannot live in prose, and the next
good idea would otherwise land here as another paragraph. The freeze wrote its
own exception: the opt-in shape EX-1 established, a host-specific bound that
ships as a documented artifact and is applied deliberately.

A2 widens that exception into a tier. A `hooks/` directory carries
host-specific bounds for Claude Code: opt-in for a portable reader, on by
default in this fork's own deployment. The skill text keeps its claim that any
agent able to read it can honour it. The hooks are where that claim stops and
enforcement starts, and the two are never blended.

**What stays out.** The unattended outer loop: triggers, budgets held by
calling code, durable state across runs, derived rubrics, anything that runs
with nobody at the keyboard. That is the runtime repo's scope, unchanged.
An object that fails here twice for want of that scope moves there, with the
failure signature recorded.

## The two disciplines that replace the freeze

1. **Every hook ships with its negative control.** The recorded bug that
   motivates this: a hook fails open on a typo. A hook without a control that
   proves it denies is a bound that reports success while measuring nothing.
   `CONTRIBUTING.md`'s fixture rule applies to hooks harder than to prose.

   Honesty about where controls run: a hook control needs the host. It is a
   probe script plus a recorded denial, rerun and rebound on every hook
   change, not a CI layer. CI can verify the hook files parse and are
   registered; only the host can verify they deny. Both halves are stated in
   each control, so nobody reads the CI half as the proof.

2. **The audit vocabulary stays single-valued.** No row becomes
   `enforced (on one host)`; that is the CO-8 smuggled-qualifier defect. The
   end state is one word. The evidence column carries the scoping: bounded on
   Claude Code via `hooks/`, instruction-only elsewhere. `ceiling-ids`
   compares end states, so the audit and the ceiling move together on every
   object.

## The loop

Unchanged from track A, restated so this file stands alone.

**Object.** One row of the backlog below, in order. **Trigger.** Manual.
**Roles.** Doer writes; adversary reviews fresh-context with its binding
recorded; the human approves SPEC and grades findings. **Steps.** SPEC, RED,
GREEN, GAUNTLET, EVIDENCE, with GREEN opening on the verification contract.
**Exits.** pass, retry, escalate, stable failure. **Stable failure**: the same
signature twice moves the object to the runtime repo's backlog rather than
earning a third round here. **Budget.** Two rounds per object. **State.**
This file, updated when the object lands.

## The backlog

Land order. Each object names what happens when its mechanism is broken.

### H1. Amend the freeze

`CONTRIBUTING.md` currently permits one opt-in shape. It gains the tier: what
`hooks/` is, its test (a hook ships with a control that proves it denies, and
the skill text never claims what only a hook enforces), and the boundary that
still holds (outer-loop mechanisms go to the runtime repo).

**Acceptance criteria.**

- `CONTRIBUTING.md` states the tier, its test, and the retained boundary.
- The freeze's original test for skill text is kept verbatim: an agent that
  can only read the text can honour a text change.
- `docs/track-a.md`'s freeze log entry gains one line pointing here, so the
  record shows the amendment rather than a contradiction.

**Broken.** Without H1, every later object violates the written freeze, and
the repo's own contribution rules become the first casualty of the work.

### H2. The spec reviewer's read scope

The snippet in `references/ceiling.md` becomes a real hook file in `hooks/`,
applied to `old-coder-spec-intent`'s frontmatter in this fork. Deny `Read` by
default, allow the spec's own directory. Deny by default and allow by path,
never the reverse, and fail closed, exactly as the ceiling already warns.

**Acceptance criteria.**

- The hook exists as a file, referenced from the agent frontmatter, and the
  ceiling's snippet points at it rather than duplicating it.
- Negative control: a probe run in which the spec reviewer attempts to read a
  source file and is denied, with the denial recorded and bound.
- Positive control: the same probe reading inside the spec directory
  succeeds, so the hook is proven to allow as well as deny.
- EX-1's audit and ceiling rows update together: end state single-valued,
  scoping in the evidence column.

**Broken.** The spec reviewer reads the implementation, confirms the spec
against the code instead of the intent, and returns no gaps. Fails green on
the layer whose value is catching what the human would have caught.

### H2b. The reviewer's scope, taken from the artifact root

H2 proved the bound and left it unwired. Its handler took scope from an
environment variable, which a hook inherits from the agent process, fixed
before the session starts. The task's artifact directory is named inside the
session, so the variable could only ever name a directory somebody pre-created
by hand. The handler reads `<artifact root>/scope` instead, written when the
SPEC step creates the artifact directory.

**Acceptance criteria.**

- The handler takes scope from the pointer and nothing else; the environment
  variable is gone from the tree.
- The three absences deny with distinguishable reasons: no artifact root, no
  pointer, a pointer naming nothing usable.
- `SKILL.md` writes the pointer as part of creating the artifact directory, and
  `setup.md` carries the mechanics and the ignore rule.
- A probe record names the handler's sha256, and `tools/audit_sweep.py` refuses
  to lift a row on a record that graded different code.
- A fresh host probe against the current handler, recorded and bound.

**Broken.** The bound exists and never applies, because the one directory it is
about cannot be named. Or worse, it applies as a deny-all nobody notices,
because the reviewer normally uses no tools and returns an ordinary review
either way.

### H3. The adversary's shell, bounded by grammar

VE-1, EX-5 and EX-7 are one gap: `Bash` in the adversary's tool list. A3
correctly ruled out deciding whether an arbitrary shell string writes. This
object does a different thing: deny `Bash` entirely except strings matching a
strict read-only git grammar. `git diff`, `git show`, `git log`, plain
arguments only, no `;`, no `|`, no `>`, no backticks, no `$(`. An allowlist
over a tiny grammar is a decision about a pattern, not write detection.

**Step zero is evidence, not design.** Harvest the Bash commands the
adversary actually ran in recent sessions. The grammar covers observed use or
the hook will fail closed on legitimate reads mid-review, which is the right
failure but a disruptive one to discover in production.

**Acceptance criteria.**

- The grammar is written down in the hook file with the step-zero harvest
  cited beside it.
- Negative controls, one per excluded class: a write (`sed -i`), a chain
  (`;`), a redirect (`>`), a substitution (`$(`), each denied and recorded.
- Positive control: the harvested read commands all pass.
- VE-1, EX-5, EX-7 move off `delegated` together, one edit across both audit
  files, `ceiling-ids` green before and after. The runtime repo's opening
  backlog in `docs/track-a.md` shrinks by the same rows in the same commit.

**Broken.** A reviewer that can rewrite what it reviews. Every verdict it has
ever produced becomes unattributable, because nothing distinguishes a finding
from a repair.

### H4. The budget, counted

CO-4: ten calls, honoured by the model, counted by nobody. A counter in the
subagent's own frontmatter hook, incrementing durable state per run, denying
past the cap.

**Step zero.** Whether a per-subagent hook can hold state across its own
invocations reliably: where the state file lives, when it resets, and what
two concurrent reviews do to it. Answered from documentation or a probe. If
the answer is that it cannot, this object takes the stable-failure exit to
the runtime repo, because a budget counted by racy state is a budget that
lies, which is worse than one that is honoured.

**Acceptance criteria.**

- Call eleven is denied, and the denial names the count.
- The counter resets per review round, not per session, and a control proves
  the reset by running two rounds back to back.
- CO-4's rows update under discipline 2.

**Broken.** The forgotten stop. A review that cannot end is a budget spent
on the review least likely to be reading carefully by the end of it.

### H5. The runner and scribe roles

Mine `archive/runner-scribe-v2` for the three agent files that exist nowhere
else: gauntlet, evidence, and gauntlet-verifier. This is the object that makes
daily runs less manual, which is the absence the word "whole" is pointing at.

**Step zero.** The branch predates A4. Reconcile every binding the three
briefs make against the one-identity rule: tree hash from the source-state
command, `Review binding:` recorded, never a typed SHA. A revived brief that
asks for the old binding reintroduces the defect A4 closed.

**Acceptance criteria.**

- The three agents land with tool lists at the floor the host allows, and any
  shell they hold is bounded by H3's grammar hook or a narrower one.
- Each brief's binding language matches `references/templates.md` post-A4.
- One full run of the demo driven through the revived roles, its evidence
  bound, as the integration proof.

**Broken.** The scribe writes the evidence the verifier grades. If their
scopes are not disjoint at the hook layer, this is self-verification wearing
two hats, which is the failure the whole skill exists to prevent.

### H6. A runner of the repo's own

REVISION 10's recorded debt: `audit-sweep`, `ceiling-ids` and the contract
check run inside a rate limiter's gauntlet because the repo has none. Give the
repo a top-level gauntlet whose members are the repo checks plus the demo's
gauntlet as one layer, and move the repo checks out of the demo.

**Acceptance criteria.**

- The demo's gauntlet grades the demo again, nothing else.
- The repo gauntlet runs the repo checks, the hook-file parse checks from
  discipline 1's CI half, and the demo as a member layer, in CI.
- The stamp and exit vocabulary apply at the repo level: an omitted member is
  an orchestration failure, not a silent skip.
- `docs/track-a.md`'s debt note is closed with the commit that paid it.

**Broken.** A wording change in an audit invalidates a rate-limiter verdict,
or worse, a repo check silently stops running because the demo it lived in
was skipped.

### H7. The writing standard

Adopt ASD-STE100 for the contract-bearing documents, enforced as a layer.
The standard's founding condition, a reader who cannot ask a follow-up, is
the doer agent's condition exactly. A criterion that reads two ways lets the
doer implement one reading while the judge grades the other, with both
correct.

**Scope, written down as a table, not implied.**

| In scope, Plain register | Out of scope |
|---|---|
| the spec template's contract sections in `references/templates.md` | evidence logs and verification-round prose |
| `demo-rate-limiter/spec.md` | the audit and the ceiling's rationale |
| the verification contract section | `docs/track-a*.md` |
| denial and error messages emitted by tools and hooks | README and orientation prose |
| the instruction sections of agent briefs | the briefs' rationale sections |

The exemption is the point, not a concession: evidence and rationale argue,
and a 900-word vocabulary strangles argument. Contract text instructs, and
instruction is what the standard was built for.

**Step zero is licensing, not linting.** ASD owns the copyright on
ASD-STE100 itself. Before any rule catalog or dictionary lands in this tree,
determine what the simple-english skill's license actually covers versus
what it repackages. If the dictionary cannot be vendored, the layer checks
only the mechanically expressible rules (sentence length caps, active voice,
one instruction per sentence) and says so, which is a narrower check stated
honestly rather than a broad one resting on an unlicensed file.

**Acceptance criteria.**

- The scope table above committed where a contributor hits it, with the
  exemption's reason.
- Step zero's answer recorded, and the layer's basis cited: vendored catalog
  or expressible-rules subset.
- The in-scope documents rewritten to Plain register, and the human SPEC
  approval confirms meaning survived the rewrite, because the layer proves
  conformance, not clarity. The linter measures rule obedience, not what a
  reader sees; the human stays the judge of whether the criterion says what
  is meant.
- The layer registered in the repo gauntlet H6 built, over the in-scope
  list. Red before the rewrite or against a seeded violation, green after.
- Non-vacuity: a thirty-word passive sentence inserted into an in-scope file
  turns the layer red through the real harness, stamp read back, restored.

**Broken.** An ambiguous Must NOT ships. The doer satisfies its reading, the
adversary grades the other, the finding is upheld, and the round is spent on
a sentence instead of a defect. The budget pays for the ambiguity either
way; the layer just moves the payment to before the work.

### H8. Close the track

- Every H-object's audit rows verified single-valued, evidence columns
  carrying the host scoping, `ceiling-ids` green.
- The runtime repo's opening backlog in `docs/track-a.md` reflects what A2
  removed and what it did not: the outer loop remains, the three shell rows
  are gone.
- The ceiling's reader-facing text says what the tier is in two sentences,
  so a portable reader knows what they are not getting and how to get it.
- This file's status table complete, each row bound to its landing commit.

**Broken.** The repo claims a tier it half-built, which is the overclaim the
ceiling exists to prevent, now in the ceiling itself.

## Gauntlet rows for this track

| Row | Why |
|---|---|
| full demo gauntlet green per object | unchanged baseline |
| ceiling-ids green before and after every audit edit | the two files move together or not at all |
| hook parse and registration checks (CI half) | a hook that does not load fails open, silently |
| recorded host probes (host half), rebound on every hook change | the only proof a hook denies |
| adversarial round per object, binding recorded | unchanged from track A |
| STE lint over the in-scope list (from H7) | an ambiguous contract sentence is paid for in review rounds otherwise |

## Status

| Object | State |
|---|---|
| H1 amend the freeze | landed 2026-09-10 at `8e9c2d4`, repaired at `0f5d8df` after one adversarial round; three findings upheld |
| H2 spec reviewer read scope | **landed 2026-09-11.** Mechanism at `6930f38`, hardened at `4559a7c` after one adversarial round, install pattern corrected at `86bfb66`. Its host probe passed and is not in the tree: H2b rewrote the handler, so that record graded code that no longer exists and was removed rather than left to vouch for this one. EX-1 moved to `enforced` on it and moved back when the handler changed, which is the rule working |
| H2b reviewer scope from the artifact root | in progress 2026-09-11; SPEC at `docs/spec-a2-h2b.md`. Handler, controls and probe-freshness landed; awaiting a host probe against the current handler |
| H3 adversary shell grammar | not started, blocked on step zero |
| H4 budget counted | not started, blocked on step zero |
| H5 runner and scribe roles | not started, blocked on step zero |
| H6 repo-level runner | not started |
| H7 the writing standard | not started, blocked on step zero |
| H8 close the track | not started |
