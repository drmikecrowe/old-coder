# Closing track A

The plan for taking `drmikecrowe/old-coder` as far as prose goes, then freezing
it. Written as a loop, because the repo's own thesis says a plan that is not a
loop is a wish. Companion to `docs/loop-alignment.md` (the audit this closes)
and `ROADMAP.md` (the upstream track, which this does not gate).

House rule inherited from the source material: no em dashes.

## What A is, and what it is not

A is the portable prose methodology: a skill any agent can read, carrying no
runtime. Closing A does not mean fixing every gap the audit found. Most of
them are not fixable in prose, and grinding on them is the failure this plan
exists to prevent.

**Done means the audit has no undecided row.** Every rule id in
`docs/loop-alignment.md` ends in exactly one of four states:

| End state | Means |
|---|---|
| `enforced` | a mechanism does it, and the evidence column names the mechanism |
| `n-a by scope` | the loop this rule governs is not built here |
| `accepted` | prose is the enforcement, the reason is written down, and the reason is not "we ran out of time" |
| `delegated` | it needs a capability a skill file cannot ship, and the row names the rule id plus what the missing capability must do. Not a repo name |

`partial` is not an end state. Every `partial` row resolves to one of the four
before A is closed.

Upstream (`ROADMAP.md` Phases 1 through 5) runs at the maintainer's review
latency. It is publishing, not closure. A closes without it.

## The loop

**Object.** One row of the backlog below. One at a time, in order.

**Trigger.** Manual. A session that names the object is the ask. Nothing
schedules this.

**Roles.** Unchanged from the skill: the doer writes repo files, the adversary
reviews with no write path and no inherited context, the human approves the
SPEC and grades findings. The doer for a docs change is still a doer.

**Steps.** SPEC, RED, GREEN, GAUNTLET, EVIDENCE, per the skill. The RED step is
not optional because the change is prose. `CONTRIBUTING.md` now says a skill
text change that alters what the gauntlet accepts ships with the fixture that
fails without it. This plan is the first consumer of that rule, and the rule
applies to itself.

**Exits.** pass, retry, escalate, and stable failure.

**Stable failure is the important one here.** If an object fails the same way
twice, stop. Do not write a third paragraph. Two identical failure signatures
means prose is not the instrument, and the object moves to `delegated` with the
signature recorded as the reason. That exit is what keeps A from becoming
open-ended.

**Budget.** Two rounds per object, the verifier's cap. A third round needs an
explicit yes and a written reason.

**State on disk.** This file. Each object carries its status, and the status is
updated when the object lands, not at the end of the session.

## The backlog

Land order. Each object names what happens when its mechanism is broken,
because the maintainer's test applies to our own work first.

### A1. Merge the loop-alignment branch

`origin/loop-alignment` at `eea55cb`. The stamp on both paths, the exit
vocabulary, the hostile-input rule, the brief-path downgrade, and the
CONTRIBUTING fixture rule are all built and all unmerged.

**Acceptance criteria.**

- `main` carries the branch content, CI green on `main` with `fetch-depth: 0`.
- Reverting the stamp write turns the orchestration self-test red. The fixture
  already exists on the branch; this criterion asserts it is non-vacuous.
- `ROADMAP.md` entries 6a, 6b, 6c reflect the merged state rather than the
  proposed one.
- `demo-rate-limiter/evidence.md` rebound to the merge commit.

**Broken.** A stamp that is written but never read is a green shirt on a silent
skip. The self-test is what proves it is read.

### A2. VE-1 is not enforced

The audit says the adversary holds read and inspect tools only. It holds
`Bash`. Bash writes: `git checkout`, `sed -i`, `rm`. The brief tells it to use
Bash only for git, which is an instruction, and the audit's own EX-1 says scope
is absent capability rather than instruction.

**Acceptance criteria.**

- VE-1 reads `partial` in the audit, and its evidence column names Bash as a
  write path rather than describing the tool list as read-only.
- The gap resolves to `delegated`, naming the destination repo and the
  capability that closes it: a narrow git surface, or a read-only source view.
- EX-7's row cross-references it, since EX-7 is where the tool list is quoted.
- Sweep: no row in the audit claims a read-only constraint for an agent whose
  frontmatter grants a shell.

**Broken.** An audit row that reports `enforced` while nothing enforces it is
the exact defect class this repo exists to catch, published in the file that
catches it.

### A3. The spec reviewer holds the capability that voids its own layer

`old-coder-spec-intent` declares `tools: Read`. Its brief says do not go
looking for the codebase, and the skill says a spec compared against the source
always passes.

**Step zero is research, not a change.** Determine what the host does with an
empty `tools:` list, with the key omitted, and with a minimal list. Answer with
documentation or command output. An assumption here produces a frontmatter
change that reads like a constraint and grants everything.

Then one of two branches:

| Finding | Resolution |
|---|---|
| empty means no tools | set it; the fixture is a run where the agent cannot open the tree and says so |
| empty means inherit all | the brief keeps `Read`, EX-1 records `partial` for this agent, and it joins A2 as `delegated` |

**Broken.** The spec reviewer reads the implementation, compares the spec to
the code instead of the intent, and returns "no gaps found." Fails green,
silently, on the one layer whose whole value is catching what the human would
have caught.

### A4. One identity function

`tools/source_state.py` hashes content and fails closed. Review verdicts bind
to a `base...HEAD` SHA the author typed. Two identities, one of them enforced.

**Acceptance criteria.**

- `SKILL.md` and `references/templates.md` say a review verdict cites the
  stamp's tree hash. No template field asks the author to type a SHA.
- EVIDENCE's consistency check compares the review's binding against the
  stamp's, and a mismatch is a failing row.
- Fixture: an evidence file whose review binds to a stale hash fails the
  consistency self-test.

If no fixture can be written for the consistency check without a runtime, this
object resolves to `accepted` with that sentence as the reason, and the
mechanical version is `delegated`. Say which.

**Broken.** Today, a review can bind to a clean SHA taken from a dirty tree,
and nothing notices. That is the failure `source_state.py` was written to
prevent, still open on the review path.

### A5. Publish the ceiling

The audit is internal. Turned outward it is the honest statement of what a
prose skill cannot enforce, in a skill whose entire subject is not
overclaiming.

**Acceptance criteria.**

- A section, in the skill rather than in `docs/`, listing every rule that is
  not `enforced`, by id, with its end state and destination.
- Every non-enforced row in `docs/loop-alignment.md` appears in it.
- A check, not a claim: a script diffs rule ids between the audit and the
  published section and exits nonzero on a difference in either direction. It
  runs as a gauntlet layer.
- The check is proven non-vacuous by deleting one id and watching the layer go
  red.

**Broken.** A published ceiling statement that drifts from the audit tells
readers the skill enforces something it does not. Without the id diff, drift is
invisible, because both files read as prose and neither parses the other.

### A6. Freeze and hand off

- `CONTRIBUTING.md` states it: new mechanisms go to the runtime repo. This repo
  takes wording, fixtures, and upstream re-cuts.
- The `delegated` rows, with their rule ids, become the runtime repo's opening
  backlog. Same ids on both sides.
- `ROADMAP.md` keeps running. It is no longer a closure dependency.

**Broken.** Without the freeze written down, the next good idea lands here,
where it can only be prose, and A reopens.

### A7. The grading contract

Cut from the original six and landed after the close. The rule: publish the
contract, not the grader's discretion. Artifact-computed rows are public with
their thresholds; the review layers' categories, powers and binding are public;
the findings to look for are never pre-listed, because a reviewer whose
questions are known in advance grades work optimised for exactly those
questions.

**Acceptance criteria.**

- `references/templates.md`: the SPEC template gains a Verification contract
  section, filled at approval.
- `SKILL.md`: GREEN opens by restating the contract; a handoff without it is
  incomplete.
- `demo-rate-limiter/spec.md`: carry the filled contract, bound to the actual
  layer names in `tools/gauntlet.sh`.
- `tools/contract_ids.py`: diff the contract's layer list against the
  `run_layer` calls, both directions, fail closed on an empty contract, and run
  as a manifest layer.

**Broken.** A contract nobody checks decays into a description of what the
harness used to do, and it decays silently, because both files read as prose
and neither parses the other. Then a missing layer and a failed layer look the
same to the reader the contract was written for.

## Gauntlet rows for this work

Docs changes still run the stack. The rows that actually bite:

| Row | Why it applies to prose |
|---|---|
| demo gauntlet, green on `main` | the demo is the only executable claim in the repo |
| id diff (A5) | the only mechanical check over the audit |
| reachability sweep | a reference file nothing points at is the F3 defect class |
| vocabulary sweep | `ROADMAP.md` step 7's `rg` list, run against every changed file |
| adversarial review | fresh context, bound to the tree hash, on any object that changes SKILL.md |

## Status

| Object | State |
|---|---|
| A1 merge loop-alignment | landed at `8e2b2c2`, 2026-09-09; its CI criterion discharged 2026-09-10 |
| A2 VE-1 correction | landed 2026-09-09, `delegated` |
| A3 spec reviewer tools | landed 2026-09-09 after one adversarial round; EX-1 is `partial`, and its end state is A6's portability call |
| A4 one identity function | landed 2026-09-10 as a mechanism, not an `accepted` |
| A5 publish the ceiling | landed 2026-09-10, all four criteria met |
| A6 freeze and hand off | landed 2026-09-10; track A is closed |
| A7 the grading contract | landed 2026-09-10 after the close, under the freeze rather than around it |

## The runtime repo's opening backlog

The runtime repo does not exist yet. When it does, these are its first issues,
carrying the same rule ids on both sides so the two backlogs can be diffed
rather than reconciled from memory.

**It is deliberately unnamed here, and the rule ids are why.** The join between
the two backlogs is `VE-1`, not a URL. A name written down before the repo
exists is a binding to something with no state to bind to: nothing can confirm
it, nothing goes red when it turns out to be wrong, and the first reader to
follow it lands on a 404 that looks like a broken promise rather than an
unstarted one. The rule id survives a rename, a different owner, and the
decision not to build the repo at all. So `delegated` requires the id and a
description of what the missing capability must do, and it does not require a
destination anyone can type. When the repo exists, its issues carry these ids
and the join works without either side citing the other's address.

| Id | What it needs | Why prose cannot do it |
|---|---|---|
| VE-1 | a git surface narrow enough to read a diff without writing, or a read-only source view, for `old-coder-adversary` | the agent needs `Bash` to run `git diff`, and bounding `Bash` means deciding whether an arbitrary shell string writes. A blocklist over shell syntax is not a bound |
| EX-5 | the same capability | push is absent from the skill's workflow and present in the adversary's shell. Not a second gap: same fix, same id |
| EX-7 | the same capability | three of the adversary's four tools are verb-specific and `Bash` is not, so the list cannot read as narrow while it is there |

One id, three rows. That is the honest count: the three rows are one missing
capability seen from three rules, and splitting them into three issues would
overstate the work.

`EX-1` is deliberately **not** on this list. It looked like a fourth
delegation until the adversarial round on A3 falsified that, and it turned out
to be closeable on one host by a `PreToolUse` hook. It ships as an opt-in
snippet instead, which is a different answer from "someone else's problem".

## Findings

### The fork's CI is a claim, not a mechanism — RESOLVED 2026-09-10

Resolved after the A7 push. Actions was enabled on the fork, the push to
`24dd097` triggered the workflow, and it went green on Python 3.12.14, deriving
this repository's shipped binding: source commit `8ecf38b`, tree
`7bc4352ff62e5e3e`. Run:
<https://github.com/drmikecrowe/old-coder/actions/runs/34468087528>.

That discharges A1's fourth criterion, which had been escalated since
2026-09-09: CI green on `main` with `fetch-depth: 0`. The depth setting is
proven by the run itself, which reported a real source commit rather than
`(unavailable: shallow history)`.

Everything narrowed under this finding is now un-narrowed and cited:
`evidence.md`'s toolchain bullet and its known-limits list, and DR-1 and DR-2
in the audit. The skill's ceiling kept the lesson and dropped the dead example,
because the general point survives the fix: running a gauntlet twice is not
evaluating it.

**How this was nearly missed, which is the part worth keeping.** The check was
run once at the start of the session, returned `total_count: 0`, and the thread
was closed on that reading. The instruction said to push and then check. I
pushed and did not re-check, and reported the fork as needing a settings click
as though that were established rather than one hypothesis consistent with zero
runs. Mike asked "shouldn't we push then run the action?" and the answer was
already sitting in the API. A measurement taken before the action that would
change it is not evidence about the state after it, and "cause unconfirmed" was
the honest report rather than a named cause.

The original finding, as it stood:

`drmikecrowe/old-coder` has zero workflow runs. Every green CI run this repo's
documents cite is `AmazingAng/old-coder`'s, and those are real: the demo, the
workflow and the provenance history in `evidence.md` all belong to upstream,
where PR #12 and the post-merge `main` runs it names did execute. Nothing in
the historical record is wrong.

What is wrong is the present tense. `evidence.md` says "CI runs the same
gauntlet on 3.12 via `.github/workflows/gauntlet.yml`", and
`docs/loop-alignment.md` DR-1 and DR-2 name CI as this repo's only evaluation
instrument. Neither is true of the fork. Every fork-only change since
2026-08-18, the completion stamp and exit vocabulary included, has been proven
on one machine on Python 3.14.7 and never on the 3.12 the workflow pins.

That is this repo's own defect class in this repo's own documents: a mechanism
credited for work it is not doing. Resolution is one human action, enabling
Actions on the fork, then one push. Until then the affected claims are
narrowed to what is true rather than left standing.

## Log

### A7, 2026-09-10

Cut from the original six and landed after the close. It fits under
`CONTRIBUTING.md`'s freeze rather than around it: the freeze's test is whether
an agent that can only read the text can honour the change, and three of the
four criteria are text. The fourth is one repo-level check in the pattern
REVISION 10 established, which the freeze already treats as in scope. Recorded
here rather than escalated, because escalating a change the freeze admits would
be theatre.

Each criterion, and what discharges it:

- **The SPEC template.** `references/templates.md` gains `## Verification
  contract`: a table of every layer with the number or state that passes it, a
  second table of review layers with their powers and binding, and the exit
  vocabulary. Filled at approval, before anything runs.
- **GREEN restates it.** One paragraph in `SKILL.md`. It says restate, not
  re-derive: a difference between what GREEN writes and what was approved is a
  finding, not an update. `SKILL.md` stays short.
- **The demo carries the filled contract.** All seventeen layers by the exact
  name the entry point invokes, plus the three review layers and the exit
  vocabulary, in `demo-rate-limiter/spec.md` under REVISION 11.
- **The check.** `tools/contract_ids.py`, in `ceiling_ids.py`'s mould, diffs
  the contract's layer names against the `run_layer` calls in both directions.

**The asymmetry is the object, not a detail of it.** Thresholds are published
because a number is checkable and withholding it only protects the author.
Review layers publish powers and binding and never a list of findings to hunt.
A reviewer handed the questions in advance grades work optimised for exactly
those questions, and the categories left off the list are the ones the author
already feared least. That is a Must NOT in REVISION 11, so a later revision
cannot add a "defect classes to look for" table and call it thoroughness.

**RED before GREEN, twice, and the second time was not planned.** The checker
ran against the repository before the contract section existed and failed
closed: no section, nothing compared. Then the contract was written naming
`contract-ids` before the layer was registered, so the missing arm fired
against the real files, and registering the layer is what turned it green. The
check was red on this repository before it was ever green on it.

Four arms, each against a copy: a contract promising a layer the gauntlet never
runs, a gauntlet running a layer the contract does not name, a missing contract
section, and a gauntlet with no `run_layer` calls.

**Proven through the real harness, not only as a script.** Deleting the `types`
row from the contract and running `contract-ids` through the harness exits 2,
and `gauntlet-stamp.txt` reads `result: layer-failed (contract-ids, rc=1)`.
Restored, green. The stamp is what distinguishes this from an unregistered
layer, which would have produced an orchestration error instead.

One audit row changed, and only where the evidence genuinely did. IN-6 ("agree
what a partial result looks like before the run") read as enforced by the
five-status vocabulary and declared downgrades. Those say what a partial result
is called, not which layers were promised. The contract is the missing half of
"before the run", so IN-6's evidence now names it. `ceiling-ids` ran green
after, which is the check that would have caught a status change smuggled in
with an evidence edit.

Full gauntlet green at `716028a`, twenty-one rows, `audit-sweep`, `ceiling-ids`
and `contract-ids` among them.

**Adversarial round, one round, findings graded.** Fresh context, no inherited
reasoning, ten calls available and six used. Binding, in the form
`references/templates.md` § Review binding asks for: `tree 1f85ffb6ed06f504` at
source commit `716028a`. The reviewer was told that hash covers
`.github/workflows` and the demo's directories and not `skills/` or `docs/`, so
the prose half of the diff was reviewed unbound. Its brief named categories and
no findings, which is the object's own rule applied to the object.

| Finding | Grade |
|---|---|
| no false pass found in `contract_ids.py` | recorded, not a finding |
| `contract_layers` reads both tables in the contract section and keeps review rows out only by their formatting; reformatting one to a bare lowercase name would report drift that does not exist | upheld and fixed |
| the factual claims check out: 17 layers both sides, 35/35 scenario rows, 65 tests | recorded |

The fragility fails in the safe direction, a false FAIL and never a false PASS,
which is why it is a fragility rather than a defect. Fixed anyway: a gate that
breaks on an innocuous edit teaches people to distrust it, and a red layer
nobody believes is worth less than no layer. Extraction now stops at the end of
the first contiguous table, and REVISION 11's Must NOT says first table and
says why the weaker rule was rejected, so the reasoning outlives the next
reader who finds the guard redundant.

Proven both ways against a copy: under the old rule a review row reformatted to
`` `spec-intent` `` produces "the contract promises `spec-intent` and the
gauntlet never runs it"; under the new rule the same input is green. The four
original arms still fire. That makes five.

**One thing the round did not have to catch, and I did.** Rebinding after the
repair, a blanket replace of the old commit hash rewrote a historical line in
`evidence.md`'s disclosure list, turning "REVISION 11 in commits `ba3ded9` and
`716028a`" into the new hash and erasing the middle of its own history. Caught
by reading back what the replace touched rather than trusting it. The entry now
names all three commits and what the third one repaired.

### The three leftovers, 2026-09-10

**Fork CI: checked at zero, closed too early, resolved the same day.**
`gh api repos/drmikecrowe/old-coder/actions/runs` returned `total_count: 0`
when the object opened, so the thread was stopped and nothing was un-narrowed.
That reading was correct and the conclusion drawn from it was not: the
instruction was to push and then check, and the check was never repeated after
the push. Actions turned out to be enabled, the A7 push fired the workflow, and
it went green on 3.12.14 against the shipped binding. Everything this thread
had narrowed is now un-narrowed and cited. See the Findings section, where the
resolution and the reasoning error are both recorded.

**The demo test count.** `README-zh.md` said 41. The suite says 65, verified by
running it rather than by trusting the number in the instruction. `README.md`
carried the identical stale figure in the identical sentence and was fixed with
it: correcting one and leaving the other would have left the pair disagreeing
about the same fact. Coverage and mutation figures in that sentence were still
right and were left alone.

**The successor repo is no longer named.** Every `drmikecrowe/old-coder-runtime`
became "the runtime repo", and both definitions of `delegated` changed to match:
a delegated row names the rule id and what the missing capability must do, not
a destination anyone can type. The reasoning is in the handoff section above.
The audit and the published ceiling define `delegated` separately, so
`ceiling-ids` ran before and after; that layer is what makes "they had to move
together" mechanical rather than remembered.


### A1, 2026-09-09

Merged `origin/loop-alignment` (`eea55cb`) into `main` as `8e2b2c2`, a `--no-ff`
merge over one intervening commit.

Criteria, one by one:

- **Branch content on `main`.** 16 files, `+509/-39`, including the new
  `docs/loop-alignment.md`. The workflow already carried `fetch-depth: 0`,
  added when `source_state.sh` learned to withhold provenance on a truncated
  history; no workflow change was needed.
- **CI green on `main`: blocked at the time, discharged 2026-09-10.** When A1
  landed, `gh api repos/drmikecrowe/old-coder/actions/runs` returned
  `total_count: 0` and the criterion was escalated; what was proven instead was
  the full gauntlet green locally at `e226c7b` on Python 3.14.7. It is now
  discharged for real: run 34468087528 is green on `main` on 3.12.14, and
  reported a source commit rather than `(unavailable: shallow history)`, which
  is what proves the `fetch-depth: 0` half of the criterion. See Findings.
- **The stamp fixture is non-vacuous.** Replaced the `write_gauntlet_stamp
  "$result"` call in `tools/gauntlet_layers.sh` with a no-op and reran
  `tools/test_gauntlet_orchestration.sh`: 8 expectations violated, exit 1.
  Restored the call: exit 0, tree clean. The six stamp controls read the
  artifact rather than asserting the call site.
- **ROADMAP 6a, 6b, 6c.** Moved from `[ ]` to `[c]` with the merge SHA. `[c]`
  is defined as committed and pushed to the fork, so the flip is bound to the
  push, not to the merge.
- **evidence.md rebound.** Reran the full gauntlet at `8e2b2c2`: every layer
  green, 22/22 mutants killed, and the binding reproduced unchanged (source
  commit `d81b5db`, tree `5a0eefa64a2cc101`). The merge carried in-scope files,
  but each arrived from `d81b5db`, so content identity did not move. Only HEAD
  did, and evidence.md already said HEAD is reported separately. Recorded that
  rerun rather than rewriting a binding that did not change.

Tail of A1, because the merge caused it: `docs/loop-alignment.md` still read
`gap` for the four phases the merge landed. Refreshed and rebound to `e226c7b`.
EX-8, VE-9, VE-11, CO-9 and CO-10 move to `enforced` with the mechanism named.
EX-1, CO-4 and DR-4 stay `partial` with the phase marked landed and the
residue stated, because a landed mechanism is not the same as a closed row:
those three resolve under A2, A5 and A6. `The gaps, as work` records that
landing here is not landing upstream.

Out of band, authorized in session: `UPSTREAM-AUDIT.md` was staged for deletion
with four live references to it in `ROADMAP.md`. Deleted it and closed all four
by inlining what each reference needed. `rg UPSTREAM-AUDIT` is now empty
repo-wide.

### A2, 2026-09-09

VE-1 read `enforced` on the strength of "adversary tools are read/inspect
only". `agents/old-coder-adversary.md` declares `tools: Read, Bash, Grep,
Glob`. `Bash` is a general write path, and the brief's "reach for `Bash` only
for git" is an instruction, which EX-1 in the same table already says does not
count as scope.

Resolved to `delegated` to the runtime repo under VE-1. The capability
that closes it is a git surface narrow enough to read a diff without writing,
or a read-only source view. Neither is expressible in a skill file, which is
why the row leaves this repo instead of getting another paragraph.

The sweep the object asked for found two more rows resting on the same fact:

- **EX-7** ("tools are narrow and verb-specific") read `enforced` while
  quoting a list containing a general-purpose shell. Same destination, same
  rule id.
- **EX-5** ("irreversible actions are missing capabilities") is true of the
  skill's workflow, where push and PR-open are absent, and false of the
  adversary, whose `Bash` reaches `git push`. Marked `partial` pointing at
  VE-1 rather than opening a second delegation for one fact.

The audit's status vocabulary was closed at four values and now carries six:
`accepted` and `delegated` are added, defined, and bound to this file.

RED before GREEN, on a docs change: the sweep is a script that reads every
agent's frontmatter, finds the ones holding a shell, and fails on any audit row
that claims a read-only constraint for one while reading `enforced`. Against
the pre-A2 audit it exits 1 naming VE-1; against the post-A2 audit it exits 0.
The script is not yet a gauntlet layer. A5 is the object that gives checks over
the audit a durable home, and this one lands with it.

### A6, 2026-09-10

**EX-1 resolved to `accepted` with an upgrade path, which is neither of the two
answers the question first looked like it had.** Shipping the hook by default
would put a Claude Code mechanism in a skill that claims to run wherever a
skill can be read, and a default that silently does nothing on the reader's
host is worse than a stated instruction. Refusing it outright would have
withheld a real bound from readers who can use it. So the hook ships as a
documented snippet in `references/ceiling.md`, applied deliberately, with the
two ways to get it wrong named: deny by default and allow by path, never the
reverse, and fail closed, because a handler that errors leaves the normal
permission flow running, which is the same as no hook at all.

That was the audit's last `partial`. Every rule id now ends in `enforced`,
`accepted`, `delegated`, `n-a`, or `n-a by scope`, and `tools/ceiling_ids.py`
fails if the published list ever disagrees with it.

**The freeze is written where a contributor will hit it**, in
`CONTRIBUTING.md`, not here. The test it states is not size: it is whether an
agent that can only read the text can honour the change. A PR that would move a
row from `delegated` to `enforced` is out of scope no matter how good it is.
The one exception is the opt-in shape EX-1 just established.

`ROADMAP.md` says plainly that it is not a closure dependency and never was.
Track A closed without a single upstream merge, because publishing runs at the
maintainer's review latency and closure cannot.

**What track A did not close, stated rather than quietly dropped.** A1's CI
criterion was still escalated at the close: `drmikecrowe/old-coder` had zero
workflow runs, so every change in this track was proven on one machine. Written
here as a permanent limit, which it was not. It was discharged the same day,
after A7, when a push fired the workflow and it went green on the pinned
interpreter. Left as written, with this note, because a plan that quietly edits
its own "what we did not close" section is worth less than one that shows which
of its limits turned out to be temporary.

### A5, 2026-09-10

**Closing the audit's `partial` rows came first**, because a ceiling cannot
publish an end state a row does not have. Nine rows read `partial` or
`gap, accepted`. Eight resolved:

| Rows | To | Why, in one line |
|---|---|---|
| IN-4, CO-2, CO-4, CO-13, DR-1, DR-2, DR-4 | `accepted` | each reason is a design position, not a shortage of time, and each is now written as one |
| EX-5 | `delegated` | it is VE-1's gap seen from another row, so it carries VE-1's id rather than opening a second delegation |

`CO-8` also read `enforced (where state exists)`, a qualifier smuggled into a
closed vocabulary. The qualifier moved to the evidence column where it belongs.

**EX-1 is the one row still `partial`, and that is deliberate.** It waits on
A6's portability decision and names it. The ceiling publishes it as the
undecided row rather than rounding it to an end state it has not reached.

**The ceiling ships inside the skill**, at
`skills/old-coder/references/ceiling.md`, not in `docs/`. `SKILL.md` is loaded
in full on every invocation and `CONTRIBUTING.md` asks that it stay short, so
the always-loaded file carries a pointer and the table lives beside the other
reference files. It also carries the two limits Mike asked for, both framed as
facts about any project rather than confessions about this one:

- a gauntlet that only ever runs on the author's machine is a gate, not an
  evaluation, and this fork is the worked example at `total_count: 0`. That
  example went stale within the day: CI now runs here. The ceiling keeps the
  lesson, drops the dead claim, and says instead that running a gauntlet twice
  is not evaluating it;
- a source binding covers what its manifest covers, and prose usually sits
  outside it, so a review of a skill-text change binds to a hash that did not
  move.

**The check.** `tools/ceiling_ids.py` compares rule ids in both directions and,
for shared ids, compares end states. Five controls, each producing a different
failure:

| Control | Result |
|---|---|
| an id deleted from the ceiling | exit 1: named as present in the audit, missing from the ceiling |
| the ceiling claiming a row the audit enforces | exit 1: both directions fire at once |
| the two files naming different end states for one id | exit 1: names both states |
| the audit resolving a row to `enforced` while the ceiling keeps it | exit 1: the reverse direction alone |
| a ceiling with no rule rows | exit 1: fails closed rather than comparing nothing |

**Both checks now run.** `REVISION 10`, approved, registers `audit-sweep` and
`ceiling-ids` as manifest members of the demo's gauntlet, so an omitted one is
an orchestration failure rather than a silent skip. They run before
`source-state`, because they grade documents outside the source manifest and a
failure in them says nothing about the binding.

The registration was proven at the layer, not only at the script. Deleting
`CO-13` from the ceiling and running the layer through the real harness exits
2, the layer-verdict code, and the stamp reads
`result: layer-failed (ceiling-ids, rc=1)`. That is A5's fourth criterion
discharged against the mechanism a reader would actually hit, and it also
distinguishes correctly: a failing layer, not an orchestration error.

Worth saying plainly, and REVISION 10 says it in the repo rather than only
here: repo-level checks are landing in a rate limiter's gauntlet because this
repo has no runner of its own. The right home is a repo-level gauntlet the
demo's is a member of. The revision buys the checks a runner today and records
the debt. It also refuses the tempting fix of widening the source manifest to
cover the checkers, because a wording change in an audit must not invalidate a
rate-limiter verdict; that consequence is published in the ceiling instead.

Pre-existing drift found and not fixed, because it is outside this object:
`README-zh.md` still says the demo has 41 tests. It has 65.

### A4, 2026-09-10

**The object's escape hatch did not apply, and saying so is the finding.** A4
offered `accepted` plus `delegated` if no fixture could be written without a
runtime. There is a runtime: the demo has a real `evidence.md`, a source-state
command that already fails closed, and a gauntlet to run a layer in. A fixture
was writable, so taking the hatch would have been a dodge dressed as a
judgment. The mechanism shipped.

`REVISION 9`, approved after an intent review, adds an `evidence-binding`
layer. It grades two things:

- the tree hash the report cites for its own gauntlet run must equal the one
  the source-state command derives now;
- a verification round may bind to an older tree, because that is what a
  declared downgrade is, but not under a bare `PASSED`.

Two design points that are easy to get wrong. The layer never hashes anything
itself, because a second implementation of the identity function is the defect
being closed, reintroduced. And it never reads `gauntlet-stamp.txt`: the exit
trap writes that after every layer has run, so a layer reading it would grade
the previous run. REVISION 8 already forbids the stamp carrying a binding the
source-state command did not produce, so deriving fresh and reading the stamp
cannot disagree.

Twelve controls, red before the checker existed and green after. They drive the
checker through a fake source-state command, which is not only for speed: the
checker's contract is that only that command produces a binding, so a fake
command is the entire environment it can observe. It also keeps the suite
honest on a machine whose signing agent is refusing.

**The layer proved itself on arrival.** It could not grade its own commit: at
`12e8d65` it went red on the real report for both reasons it exists to catch,
naming the stale hash and the missing field, and green once the report was
rebound to `e1e514b57b26706c`. That is a non-vacuity proof nobody had to
construct.

The companion half, which the intent review is the reason this object has: the
templates asked authors to type a SHA. `references/templates.md` now asks for
the tree hash and adds a `Review binding:` field, and its consistency check
gains a `Binding:` row. `SKILL.md` says the adversarial layer binds to the tree
hash the diff was taken from rather than the SHA typed to produce it, because
binding to a SHA is what lets a review taken from a dirty tree report a clean
state. A checker that catches a stale binding while the template keeps asking
for the value that goes stale closes nothing.

This object closes no audit row on its own. It strengthens VE-9 and VE-11: the
harness-written completion artifact now has a layer that fails when the
model-written report disagrees with it.

**Adversarial round, one round, findings graded.** Fresh context, bound to
`966bc7f...HEAD`, told explicitly that the tree hash does not cover `skills/`
so the prose in the diff was unbound. Six of ten tool calls.

| Finding | Grade |
|---|---|
| `VERDICT`, `REPORT_BINDING` and `REVIEW_BINDING` all used `search`, so the checker graded whichever match came first in a report full of hashes | upheld, three findings for one defect; `sole_match` makes a duplicated field a failure naming the count and line numbers |
| the stale-review control asserted only that `PASSED` appeared in stderr | upheld; it now asserts both hashes and the specific reason |
| "drops this layer back to not-run" misstates the mechanism, which fails rather than not-runs | not upheld as written, and the misreading is the finding |

The last one is worth the space. The sentence is about the adversarial review
layer, where not-run is correct: nobody has reviewed the state being shipped.
The reviewer read it as the evidence-binding layer, which fails. It read it
that way because after A4 both layers key off the same hash, so the sentence
now names which layer it means and says the two states differ. A reviewer
misreading a sentence in the direction of a real ambiguity is a finding about
the sentence.

The three-for-one defect is the one that mattered. The checker was correct only
because the report happened to hold exactly one of each field. Restoring
first-match-wins fails the three new controls and nothing else, which is what
makes them non-vacuous rather than decorative.

**What A4 deliberately did not do.** The A3 log banked an observation: the
source manifest scopes to `.github/workflows` and the demo's own directories,
so `skills/` sits outside it and a SKILL.md edit does not move the tree hash.
A4 leaves that alone. Extending the demo's manifest to cover the skill would
make the demo's content identity depend on prose the demo does not execute,
and every wording change would invalidate a binding about rate-limiter
behaviour. The honest consequence stands and belongs in A5's ceiling: an
adversarial review of a skill-text change binds to a hash that did not move,
so the tree hash is not evidence about the prose it reviewed. One identity
function now covers evidence and review. It does not cover the skill.

The demo's own report records `Review binding: unavailable`. Its six
verification rounds predate the mechanism and cite commit SHAs, so none can be
checked. The layer therefore holds it below a bare `PASSED` mechanically, which
is the verdict it had already declared for its own reasons. The two agreeing is
the point.

### A3, 2026-09-09

**Step zero, answered from the host's documentation** (`docs.claude.com`,
Create custom subagents, "Supported frontmatter fields"):

| `tools:` | What the host does |
|---|---|
| key omitted | "Inherits every tool available to subagents if omitted" |
| empty, or no entry resolving to a tool | the subagent "usually fails to launch with an error naming the entries" |
| minimal list | host-enforced; `disallowedTools` additionally removes from the inherited or specified list |

The object offered two branches and the answer is neither. Empty does not mean
no tools, it means a broken agent. `tools: Read` is therefore already the
narrowest setting the host has: there is nothing between "one tool" and "will
not start". The spec reviewer is at the floor and still holds a tool that
reaches every file in the tree.

**The first resolution of this object was wrong, and the adversary caught it.**
Round 1 concluded that the missing per-agent path-scoped read did not exist on
this host, and moved EX-1 to `delegated`. It does exist. A `PreToolUse` hook
declared in the subagent's own frontmatter is registered only while that
subagent runs and removed when it finishes, fires on that subagent's tool
calls, and can return `permissionDecision: "deny"`, which prevents the call.
Denying `Read` outside the spec's own directory is expressible there today, in
the agent file, with no runtime repo involved.

So EX-1 is `partial`, not `delegated`. The bound is buildable; it is not built.
The reason it is not built is a real trade and not a shortage of mechanism: a
frontmatter hook is a Claude Code feature, and this skill's claim is that any
agent can read it and carry no runtime. Taking the hook buys a real boundary on
one host and costs the portability the skill is built on. That is A6's question
(freeze and hand off), so EX-1 waits for A6 rather than being answered here.

VE-1 keeps `delegated`, with its reason corrected. The same hook cannot close
it: bounding the adversary's `Bash` means deciding whether an arbitrary shell
string writes, and a blocklist over shell syntax is not a bound. Path-scoped
`Read` denial is a decision about a path; write detection over `Bash` is not.

EX-4 stays `enforced` and is narrowed rather than downgraded. Its rule is
"split the doer before adding a tool", and the split is real: two files, two
briefs, two budgets. What was wrong was the evidence clause borrowing the
spec reviewer's scope instruction as proof. That claim now lives at EX-1,
where it can be scored honestly.

RED before GREEN. The sweep is now a committed file, `tools/audit_sweep.py`,
not a claim about one. Round 1 cited exit codes from a script that lived only
in the session's scratchpad, which is a fabricated citation by this repo's own
rule, and the adversary led with it. Four controls, all run against the
committed script:

| Control | Result |
|---|---|
| audit at `7f4dd97` | exit 1: EX-4 and EX-7 assert a bound and name no agent id |
| delegated rows forced back to `enforced` | exit 1: EX-7 and VE-1 overclaim against `old-coder-adversary`'s tool list |
| audit file absent | exit 1: fails closed rather than passing on nothing |
| the shipped audit | exit 0 |

Nothing runs it yet. A5 is the object that gives checks over the audit a
gauntlet layer, and this one lands with it; until then the citation resolves to
a file a reader can run by hand, which is the part that was missing.

`SKILL.md` gains a paragraph saying the boundary is not what the split buys,
and the "prefer the registered path" advice now says what that path enforces:
the tool list, not the scope those tools reach. It does not mention the
frontmatter hook, because SKILL.md is the portable half and the hook is
host-specific; the audit carries it. Per `CONTRIBUTING.md` this is a wording
change. It alters no gauntlet acceptance, so it ships without a fixture; the
fixture in this object belongs to the audit rows, not the skill text.

**Adversarial round, one round, findings graded.** Fresh context, no inherited
reasoning, bound to base `7f4dd97`. Nine of ten tool calls used.

| Finding | Grade |
|---|---|
| the "proven" sweep cites a script that exists in no committed file | upheld; the script is now `tools/audit_sweep.py` and the "not yet a layer" caveat is restored |
| `permissions.deny` asserted as the host's only path scoping, uncited, and it is the whole basis for `delegated` | upheld, and it inverted the object: frontmatter `PreToolUse` hooks are per-agent and can deny, so EX-1 is `partial` |
| the exit-1 claim for EX-4 is unverifiable | upheld as subordinate to the first; the committed control now shows it |

Three findings, three upheld, none dismissed. The second is the one that
mattered: it was the load-bearing claim under the object's verdict, and it was
an assumption wearing a citation's clothes.

Two observations for A4, not acted on.

`tools/source_state.py` scopes the content hash to `.github/workflows` and the
demo's own directories. `skills/` is outside it, so this session's SKILL.md
edit left the tree hash unmoved. That is right for the demo, whose binding is
about the demo. It is wrong for track A, where the skill text is the
deliverable: a review bound to that hash proves nothing about the prose it
reviewed, and DR-4 says skills are behavior. A4 is the object that decides
whether one identity function covers both.

`evidence.md` line 154 records the source
binding as "source commit, tree hash, current HEAD reported separately," while
the verification rounds bind to bare commit SHAs (`d0b506c`, `13b3cd5`). Both
identities are already in the same file, one sentence apart. A4 is the object
that reconciles them.
