# Loop-engineering alignment

A rule-by-rule audit of this repo against a private design document for
autonomous agent loops ("Loop engineering" v0.1: intent, execution,
verification, control, drift — stable rule ids). Reported the document's own
way: by id, with evidence, no aggregate score. Each rule is restated in one
line because the source is not committed. First audited at fork `main`
`78187f9`; refreshed at `e226c7b`, when Phases B through E landed on `main`
and the rows they governed stopped being gaps.

Status vocabulary, closed:

| Status | Means |
|---|---|
| `enforced` | a mechanism already does it; the evidence column names it |
| `partial` | intent present, part unmet; the gap is named |
| `gap` | not done; the phase column says where it lands |
| `n-a` | does not apply; the reason is named |
| `accepted` | prose is the enforcement; the reason is written down |
| `delegated` | it needs a capability this repo cannot supply; the destination repo and rule id are named |

`accepted` and `delegated` are `docs/track-a.md`'s end states. A row reaches
one of them when its `partial` is resolved rather than restated. `delegated`
rows carry the same rule id in the runtime repo, so the two
backlogs can be diffed.

The skill is a human-gated methodology, not a scheduled loop. Outer-loop
iteration and durable-state rules are `n-a` by scope: this audit does not
build the loop.

`docs/track-a.md` is the plan that closes this audit. It drives every row here
to an end state and records which object resolved it.

`skills/old-coder/references/ceiling.md` is this audit turned outward: every
row below that is not `enforced`, published inside the skill so its readers see
the limits without opening `docs/`. `tools/ceiling_ids.py` fails when the two
lists differ in either direction, or when they name different end states for
the same id.

`tools/audit_sweep.py` checks this file mechanically: a row asserting a
capability bound must name the agent id it constrains, and may not read
`enforced` when that agent's frontmatter declares a tool defeating the bound.
Run it by hand for now; A5 makes it a gauntlet layer.

## Plane 1 — Intent

| Id | Rule, in one line | Status | Evidence / gap |
|---|---|---|---|
| IN-1 | acceptance criteria are falsifiable, with a negative case | enforced | SPEC scenarios demand concrete inputs/outputs and error cases; "Handles bad input is not a spec" (`SKILL.md` §1) |
| IN-2 | intent lives in a plan artifact outside the conversation | enforced | `SPEC.md` is a file, committed at approval; append-only enforced by diffing the committed copy |
| IN-3 | every step names what would show it complete | enforced | scenario → test mapping is 1:1 and mechanical (`templates.md`) |
| IN-4 | a plan missing validation statements is rejected before execution | accepted | the spec-intent review and human approval reject in prose; nothing rejects in code. Accepted, and the reason is not time: the artifact is prose, and a human approver who can be shown a plan with no validation statements is a better rejector of it than a parser would be |
| IN-5 | one loop, one object type | enforced | the skill runs one task per artifact directory; `old-coder-api` composition explicitly forbids two parallel workflows |
| IN-6 | agree on what a partial result looks like before the run | enforced | the five-status layer vocabulary, `PASSED WITH LIMITS`, and declared downgrades are exactly this |

## Plane 2 — Execution

| Id | Rule, in one line | Status | Evidence / gap |
|---|---|---|---|
| EX-1 | scope is absent capability, not instruction | accepted | registered agents get a host-enforced `tools:` list; the bundled-brief path is a promise the author keeps, and Phase C (landed) makes it an explicit confidence downgrade. What the list enforces is which tools, not what they reach. `old-coder-spec-intent` declares `tools: Read`, already the host's floor: omit the key and it inherits every subagent tool, list nothing that resolves to a tool and it fails to launch. `Read` then opens any file, so "do not go looking for the codebase" is instruction. Accepted, and the reason is a trade rather than a shortage of mechanism: a `PreToolUse` hook in the agent's own frontmatter can deny `Read` by path for that agent alone, but it is a Claude Code feature and this skill claims to run wherever a skill can be read. Shipped as an opt-in snippet instead (`references/ceiling.md` § One limit you can close yourself), so a reader on that host can take the bound without every other reader inheriting a mechanism their host does not have. See VE-1 for the case the hook cannot close |
| EX-2 | deny beats allow; empty allow list permits nothing | enforced | grants honored only from user scope; "no rule visible means the restrictive default" (`SKILL.md` §Setup) |
| EX-3 | the check's author is not the implementation's author | enforced | human approves the spec; adversary and spec-intent reviewers spawn fresh; the merge gate's text is the scope authority |
| EX-4 | split the doer before adding a tool | enforced | two agents on purpose, and the split itself is real: `old-coder-spec-intent` and `old-coder-adversary` are separate files with separate briefs and budgets (`SKILL.md` §The bundled agents). The rule this row scores is the split. The instruction that `old-coder-spec-intent` stay away from the source tree is prose, not capability, and is scored at EX-1 |
| EX-5 | irreversible actions are missing capabilities, not policy | delegated → the runtime repo, VE-1 | true of the skill's own workflow: push and PR-open are "not gated, absent", never grantable. Not true of `old-coder-adversary`, whose `Bash` reaches `git push` like any other command. Not a second gap and not a second delegation: the same capability that closes VE-1 closes this, and it carries VE-1's id on both sides |
| EX-6 | containment first, path scoping as defense in depth | enforced | worktree/branch isolation from Tier 2; checkpoint restores verified by `git diff --exit-code` |
| EX-7 | tools are narrow and verb-specific | delegated → the runtime repo, VE-1 | `old-coder-adversary` holds `Read, Bash, Grep, Glob`. Three are verb-specific; `Bash` is a general-purpose shell, so the list is not narrow and the row cannot read `enforced`. Same capability closes it as VE-1, which is where the write path is stated |
| EX-8 | tool output is untrusted input | enforced | Phase C (landed): the adversary brief makes a comment, docstring, commit message, or file that directs the reviewer a finding in its own right, reported with `file:line` (`agents/old-coder-adversary.md`) |
| EX-9 | authorization enforced at the tool boundary, per-tool credentials | n-a | no tool in this skill holds credentials |
| EX-10 | large output goes to a file and is summarized back | enforced | every layer redirects to `logs/`, "redirect, don't tee", bounded reads (`gauntlet.md` §Capturing command output) |

## Plane 3 — Verification

| Id | Rule, in one line | Status | Evidence / gap |
|---|---|---|---|
| VE-1 | the verifier holds no write capability | delegated → the runtime repo, VE-1 | **This row read `enforced` and was wrong.** `agents/old-coder-adversary.md` declares `tools: Read, Bash, Grep, Glob`. `Bash` is a general write path: `rm`, `sed -i`, `git checkout`, `git commit`, `git push`. The brief's "reach for `Bash` only for git" is an instruction, and EX-1 in this same table says scope is absent capability, not instruction. The prose enforcement stays; what closes the row is a capability: a git surface narrow enough to read a diff without writing, or a read-only source view. The frontmatter `PreToolUse` hook that would bound `Read` by path for EX-1 cannot do this one: it would have to decide whether an arbitrary shell string writes, and a blocklist over shell syntax is not a bound |
| VE-2 | a check must be shown able to fail before its pass counts | enforced | RED-first; throwaway mutant for immediately-passing tests; negative controls for home-grown checkers |
| VE-3 | distinguish newly failing from already failing | enforced | baseline note: record pre-existing failures verbatim, hold zero NEW failures |
| VE-4 | verification is multi-row, not one check | enforced | the layer table; a substitute is never a pass |
| VE-5 | absent evidence is a failing row | enforced | "a path to a file that does not exist is a fabricated citation"; every non-passed row named under `Not proven:` |
| VE-6 | deterministic checks gate; model judgment advises | enforced | adversary findings are triaged against the code; the human grades verifier findings; layers gate |
| VE-7 | deterministic ≠ correct; add substance checks | enforced | "a negative control proves one known-bad case", the grep-gate-guards-a-spelling caveat, human spec approval |
| VE-8 | verdicts are structured, not prose | enforced | closed five-status vocabulary per layer, four verifier states, mechanical consistency check |
| VE-9 | completion is proven by a harness-written artifact: checks passed, on this content, after the last change | enforced | Phase B/D (landed): `gauntlet-stamp.txt`, written by the exit trap on every path, carries the result, both layer sets, a UTC timestamp, and the source binding. Six controls in `test_gauntlet_orchestration.sh` prove each path. Limit, stated in the skill: the stamp is written by the helper it reports on |
| VE-10 | content identity by hashing content, not by asking git what changed | enforced | `tools/source_state.py`: tracked-manifest hashing, fail-closed on staged/unstaged/untracked/deleted, no-git fallback |
| VE-11 | the evidence artifact records run provenance | enforced | Phase B (landed): the stamp emits source commit, tree hash, layer sets and UTC time from the harness. EVIDENCE cites the stamp rather than restating it (`SKILL.md` §EVIDENCE) |
| VE-12 | each failure to prove gets a distinct reason | enforced | `N-A` / `UNAVAILABLE` / `SUBSTITUTED` split; source_state pins reasons per error path |
| VE-13 | the verification layer is tested against known-bad inputs | enforced | orchestration/checker/source-state self-tests run as layers; the negative-control mutant; controls proven non-vacuous |

## Plane 4 — Control

| Id | Rule, in one line | Status | Evidence / gap |
|---|---|---|---|
| CO-1 | iteration counted by calling code | n-a by scope | no outer loop is built here; the human is the loop |
| CO-2 | three exits: pass, retry, escalate — plus stable failure | accepted | abandon-after-round-2 is the stable-failure exit and it is defined; nothing counts in code. Accepted with CO-1: the human is the loop, so the human is the counter |
| CO-3 | stagnation detected by failure signature | n-a by scope | with CO-1 |
| CO-4 | budgets raise when exhausted | accepted | the adversary's 10-call budget and the verifier's 2-round cap are enforced by the author and the human, not by a type. Phase C (landed) makes an uncounted or over-budget round a failed round rather than a nudge (`gauntlet.md`, `templates.md`). Accepted: a budget *type* is unbuildable in prose, so the enforcement is that a breached budget voids the round |
| CO-5 | escalation names a visible destination | enforced | the skill ends at EVIDENCE shown to the human; blocked operations are recorded there, never silently dropped |
| CO-6 | stopping carries gate, reason, and evidence | enforced | `FAILED` requires the verbatim failure; abandonment reports the findings that drove it |
| CO-7 | state survives the process, written atomically, locked | n-a by scope | single-run artifacts; no concurrent scheduled runs exist to protect against |
| CO-8 | corrupt state is a stop, not a fresh start | enforced | where state exists: a rejected spec keeps its directory and history, and corrupt source-state inputs fail closed with no partial hash. The skill holds no other durable state, so there is none left to corrupt |
| CO-9 | the trace is written on the exception path too | enforced | Phase D (landed): the exit trap stamps the failed-layer, orchestration-error, incomplete and crash paths, each with its own control. A failed source-state command is stamped `unavailable`, never guessed |
| CO-10 | exit codes distinguish a decision from a crash | enforced | Phase D (landed): 0 green, 2 a layer ran and failed, 3 the orchestration contract was violated (an exit 0 that skipped the audit included), anything else a crash passed through. One control per code |
| CO-11 | the trigger lives outside the loop | enforced | the offer gate: a configured wake IS the ask; the trigger never changes an exit |
| CO-12 | never destroy human work to simplify the task | enforced | isolation invariant; the worktree trap; "never report green from a tree that never ran the suite" |
| CO-13 | the final attempt narrows to the blocking row | accepted | no rule narrows the last verifier round to the blocking finding. Accepted deliberately, not for time: rounds are graded by a human who can direct this, and a rule that always narrows the last round would hide a second defect behind the first |

## Drift

| Id | Rule, in one line | Status | Evidence / gap |
|---|---|---|---|
| DR-1 | gates and evaluations are different instruments | accepted | gates are strong. The only evaluation was CI running the demo on every PR, and on this fork it does not run: `drmikecrowe/old-coder` has zero workflow runs, so the fork's own changes are evaluated by nothing. Upstream runs it. Accepted as a rule about the skill, which cannot make anyone's CI fire; **escalated as a fact about this repo**, and published in the skill's ceiling because a gauntlet that only ever runs on the author's machine is a gate wearing an evaluation's name |
| DR-2 | a fixed corpus of known-good inputs, run on a schedule | accepted | the demo is the corpus; the trigger is a human running `tools/gauntlet.sh`, because the fork's CI does not fire (see DR-1). No schedule independent of traffic either. Accepted for a prose skill; the missing trigger is escalated with DR-1, not accepted |
| DR-3 | evaluate weekly | n-a | no production traffic; the failure this catches does not accrue here |
| DR-4 | instructions and skills are behavior: versioned, reviewed, tested | accepted | versioned and reviewed, yes (this repo, CONTRIBUTING's bar). Phase E (landed): CONTRIBUTING requires that a skill-text change altering what the gauntlet accepts ships with the fixture that fails without it. Accepted: nothing rejects a PR that ignores it, and the reviewer who would enforce it is the same human who would notice the missing fixture. A related limit is published in the ceiling: the source manifest excludes `skills/`, so a skill-text change moves no tree hash |
| DR-5 | track cost and step count per unit of work | enforced | per-layer wall-clock and per-layer yield are EVIDENCE fields, kept to tune the tier map (fork-local; rejected upstream on #10) |

## The gaps, as work

In land order. Upstream tags follow `ROADMAP.md`'s conventions; everything
here diffs against fork `main` first and is re-cut upstream later, if at all.

All four phases landed on fork `main` at `8e2b2c2` (2026-09-09), track-A
object A1. The Upstream column is unchanged: landing here is not landing there.

| Phase | Rules | Change | Where | Upstream |
|---|---|---|---|---|
| B | VE-9, VE-11 | the demo entry point writes a completion stamp — result, layers, source binding, UTC time — through the layer helper, so completion proof is harness-written; EVIDENCE's consistency check binds to it | `demo-rate-limiter/tools/`, `references/templates.md`, `references/gauntlet.md`, `SKILL.md` | candidate, after Phase 3b lands |
| C | EX-1, EX-8, CO-4 | brief-path reviews record a confidence downgrade; the adversary brief treats repo content as data under review, never instruction; an uncounted or over-budget round is a failed round | `SKILL.md`, `agents/old-coder-adversary.md`, `references/templates.md` | candidate, with ROADMAP Phase 4 |
| D | CO-9, CO-10 | the stamp is written on the failure path too; the entry point's exit distinguishes layer verdict (2), orchestration failure (3), and crash (the original status) | `demo-rate-limiter/tools/` | candidate, with Phase B |
| E | DR-4 | CONTRIBUTING states it: a skill-text change that alters what the gauntlet accepts ships with the fixture that fails without it | `CONTRIBUTING.md` | candidate |

Consciously not adopted: CO-13 (the human grades rounds and can narrow the
last one) and the outer-loop rules (CO-1/CO-3/CO-7 — whoever schedules this
skill owns them). CO-4's budget *type* is likewise accepted as unbuildable in
prose: the enforcement is that a breached budget voids the round.
