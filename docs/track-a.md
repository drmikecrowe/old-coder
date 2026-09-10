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
| `delegated` | it needs a capability, and the destination repo and rule id are named |

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
| A1 merge loop-alignment | landed at `8e2b2c2`, 2026-09-09; one criterion blocked, see below |
| A2 VE-1 correction | landed 2026-09-09, `delegated` |
| A3 spec reviewer tools | landed 2026-09-09 after one adversarial round; EX-1 is `partial`, and its end state is A6's portability call |
| A4 one identity function | landed 2026-09-10 as a mechanism, not an `accepted` |
| A5 publish the ceiling | not started |
| A6 freeze and hand off | not started |

## Findings

### The fork's CI is a claim, not a mechanism

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

### A1, 2026-09-09

Merged `origin/loop-alignment` (`eea55cb`) into `main` as `8e2b2c2`, a `--no-ff`
merge over one intervening commit.

Criteria, one by one:

- **Branch content on `main`.** 16 files, `+509/-39`, including the new
  `docs/loop-alignment.md`. The workflow already carried `fetch-depth: 0`,
  added when `source_state.sh` learned to withhold provenance on a truncated
  history; no workflow change was needed.
- **CI green on `main`: BLOCKED.** `gh api
  repos/drmikecrowe/old-coder/actions/runs` returns `total_count: 0`. The fork
  has never run a workflow, on any branch or event, against a `gauntlet`
  workflow created 2026-08-05. Enabling Actions on a fork is a one-time click
  in repository settings with no API behind it, so this criterion is escalated
  to the human rather than retried. What was proven instead: the full gauntlet,
  green locally at `e226c7b` on Python 3.14.7. See Findings.
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

Resolved to `delegated → drmikecrowe/old-coder-runtime VE-1`. The capability
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
