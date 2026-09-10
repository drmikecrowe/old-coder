# What this skill does not enforce

A skill is prose. Prose persuades an agent; it does not bound one. This file is
the list of places where that gap is real, published rather than left in an
internal audit, because a methodology whose subject is not overclaiming cannot
keep its own limits private.

The rule ids come from a rule-by-rule audit of this repo against a design
document for autonomous agent loops. The audit lives at
`docs/loop-alignment.md` with the evidence for each row. Every rule not marked
`enforced` there appears here, and `tools/ceiling_ids.py` fails the gauntlet if
the two lists ever differ in either direction. Neither file parses the other by
hand, so without that check the drift would be invisible.

## The end states

| State | Means |
|---|---|
| `accepted` | prose is the enforcement, and the written reason is not "we ran out of time" |
| `delegated` | it needs a capability a skill file cannot ship; the row names the rule id and what that capability must do |
| `n-a` | the rule does not apply here, and the reason is named |
| `n-a by scope` | the loop the rule governs is not built here |
| `partial` | **not an end state.** A row may sit here only while it names the open decision it waits on. No row is in it |

## The rows

| Id | Rule, in one line | End state | Where it goes |
|---|---|---|---|
| IN-4 | a plan missing validation statements is rejected before execution | accepted | a human approver shown a plan with no validation statements is a better rejector than a parser |
| EX-1 | scope is absent capability, not instruction | accepted | `old-coder-spec-intent` holds `tools: Read`, the host's floor, and `Read` opens any file. This fork has landed the hook that bounds it; the row moves when the host probes are recorded, not before. See "One limit closed by a hook" below |
| EX-5 | irreversible actions are missing capabilities, not policy | delegated | the runtime repo, VE-1. True of the workflow, false of the adversary, whose `Bash` reaches `git push`. Same capability as VE-1, same id |
| EX-7 | tools are narrow and verb-specific | delegated | the runtime repo, VE-1. Three of the adversary's four tools are verb-specific; `Bash` is a shell |
| EX-9 | authorization enforced at the tool boundary, per-tool credentials | n-a | no tool in this skill holds credentials |
| VE-1 | the verifier holds no write capability | delegated | the runtime repo, VE-1. The adversary declares `Read, Bash, Grep, Glob`, and `Bash` writes. What closes it is a git surface narrow enough to read a diff without writing, or a read-only source view |
| CO-1 | iteration counted by calling code | n-a by scope | no outer loop is built here; the human is the loop |
| CO-2 | three exits: pass, retry, escalate, plus stable failure | accepted | the exits are defined; the human is the loop, so the human is the counter |
| CO-3 | stagnation detected by failure signature | n-a by scope | with CO-1 |
| CO-4 | budgets raise when exhausted | accepted | a budget *type* is unbuildable in prose, so the enforcement is that a breached budget voids the round |
| CO-7 | state survives the process, written atomically, locked | n-a by scope | single-run artifacts; no concurrent scheduled runs to protect against |
| CO-13 | the final attempt narrows to the blocking row | accepted | a rule that always narrows the last round would hide a second defect behind the first |
| DR-1 | gates and evaluations are different instruments | accepted | running the gauntlet twice is not evaluating it. See "Two limits worth more than a row" below |
| DR-2 | a fixed corpus of known-good inputs, run on a schedule | accepted | the demo is the corpus and CI is the trigger, but the trigger is traffic, not a schedule |
| DR-3 | evaluate weekly | n-a | no production traffic; the failure this catches does not accrue here |
| DR-4 | instructions and skills are behavior: versioned, reviewed, tested | accepted | `CONTRIBUTING.md` requires the fixture; nothing rejects a PR that ignores it |

## One limit closed by a hook, and what that costs you

EX-1 is `accepted` in the table above, and this fork has built the mechanism
that would move it. The row has not moved yet, on purpose: what is green is
the CI half, and the CI half is not the proof. When the host probes are
recorded the row becomes `enforced`, one word, with the scoping in the
audit's evidence column rather than in the status cell.

The honest version of that future sentence keeps its qualifier: **enforced on
Claude Code, an instruction everywhere else.**

The mechanism is `hooks/spec-intent-scope.sh` in this repository. A
`PreToolUse` hook declared in a subagent's own frontmatter is registered only
while that subagent runs, fires on its tool calls, and can return
`permissionDecision: "deny"`, which prevents the call. The handler denies
`Read` by default and allows only inside the directory the SPEC lives in, which
is exactly what the spec reviewer's brief asks for in prose.

Read the handler rather than a copy of it. It is a real file with real
controls, and a snippet reproduced here would drift from it silently, which is
the failure this whole file is about. `hooks/README.md` says how to take it on
another host: one symlink, and the `hooks:` block copied out of
`skills/old-coder/agents/old-coder-spec-intent.md`.

Three things to get right, and the third is the one people miss.

1. **Deny by default and allow by path**, never the reverse. A blocklist of
   directories you thought of is not a bound.
2. **Fail closed.** A handler that errors and returns nothing leaves the normal
   permission flow running, which is the same as no hook at all. On
   `PreToolUse`, exit 2 is a blocking error, so every unexpected path exits 2.
3. **A hook cannot fail closed on its own absence.** Delete the handler and
   Claude Code logs the failure and carries on. A parse-and-registration check
   in CI catches the deletion; nothing catches a runtime that quietly stops
   honouring frontmatter hooks. That is why the proof is a recorded host probe,
   rerun on every hook change, and never the CI check on its own.

Prove it both ways or you have proven nothing: a run where the reviewer tries
to open a source file and reports that it could not, **and** a run where it
reads the SPEC in its own directory and succeeds. A handler that denies
everything passes the first test perfectly.

This works for `Read` because a path is a decidable thing. It does not
generalise to VE-1: bounding `old-coder-adversary`'s `Bash` would mean deciding
whether an arbitrary shell string writes, and a blocklist over shell syntax is
not a bound. That is why VE-1 is `delegated` and this row is not.

## Two limits worth more than a row

**Running your gauntlet twice is not evaluating it.** A gate catches the change
in front of it. An evaluation catches drift across changes: a dependency that
moved, an interpreter that changed behaviour, a flaky test that has been flaky
for a month. CI on every push is a second gate, on a second machine, and that
is worth having. It is not the second instrument, because nothing fires unless
someone pushes, and a quiet repository is one where drift accumulates unseen.

This repository is the worked example twice over, and the second half only
because the first was caught. For weeks its CI ran zero times while its own
documents credited CI in the present tense: `actions/runs` returned
`total_count: 0` against a workflow committed in August, and every green run
those documents cited belonged to the upstream project. Real runs, wrong
repository. It now runs on every push, on the pinned interpreter rather than
the author's, and the gap it closed was never the one the documents claimed to
have covered.

Two habits fall out of that. Check that your CI has run, on your repository,
against the state you are shipping, before crediting it in EVIDENCE; a workflow
file is not a workflow run. And do not let a green pipeline persuade you that
the drift question is answered, because that question is about the runs nobody
triggered.

**A source binding covers what its manifest covers, and prose usually sits
outside it.** This skill's own demo hashes `.github/workflows` and the demo's
directories. `skills/` is not in that manifest, so editing `SKILL.md` moves no
tree hash. An adversarial review of a skill-text change therefore binds to a
hash that did not move, and the binding says nothing about the prose reviewed.
Widening the manifest to cover prose is not obviously right either: it makes a
binding about runtime behaviour invalidate on a wording change. Know which of
your files the hash speaks for, and do not let a green binding stand in for a
review of the ones it does not.

## What is enforced

Everything not listed above, with the mechanism named in the audit's evidence
column. The short version: content identity is hashed and fails closed; the
completion stamp is written by the harness on every exit path; exit codes
distinguish a decision from a crash; every check that can pass vacuously ships
a control proving it can fail. Those are mechanisms. This file is the rest.
