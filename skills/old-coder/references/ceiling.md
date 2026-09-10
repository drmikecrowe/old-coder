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
| `delegated` | it needs a capability a skill file cannot ship; the destination repo and rule id are named |
| `n-a` | the rule does not apply here, and the reason is named |
| `n-a by scope` | the loop the rule governs is not built here |
| `partial` | **not an end state.** A row may sit here only while it names the open decision it waits on. No row is in it |

## The rows

| Id | Rule, in one line | End state | Where it goes |
|---|---|---|---|
| IN-4 | a plan missing validation statements is rejected before execution | accepted | a human approver shown a plan with no validation statements is a better rejector than a parser |
| EX-1 | scope is absent capability, not instruction | accepted | `old-coder-spec-intent` holds `tools: Read`, the host's floor, and `Read` opens any file, so its "do not go looking for the codebase" is instruction. One host can close this; see "One limit you can close yourself" below |
| EX-5 | irreversible actions are missing capabilities, not policy | delegated | `drmikecrowe/old-coder-runtime` VE-1. True of the workflow, false of the adversary, whose `Bash` reaches `git push`. Same capability as VE-1, same id |
| EX-7 | tools are narrow and verb-specific | delegated | `drmikecrowe/old-coder-runtime` VE-1. Three of the adversary's four tools are verb-specific; `Bash` is a shell |
| EX-9 | authorization enforced at the tool boundary, per-tool credentials | n-a | no tool in this skill holds credentials |
| VE-1 | the verifier holds no write capability | delegated | `drmikecrowe/old-coder-runtime` VE-1. The adversary declares `Read, Bash, Grep, Glob`, and `Bash` writes. What closes it is a git surface narrow enough to read a diff without writing, or a read-only source view |
| CO-1 | iteration counted by calling code | n-a by scope | no outer loop is built here; the human is the loop |
| CO-2 | three exits: pass, retry, escalate, plus stable failure | accepted | the exits are defined; the human is the loop, so the human is the counter |
| CO-3 | stagnation detected by failure signature | n-a by scope | with CO-1 |
| CO-4 | budgets raise when exhausted | accepted | a budget *type* is unbuildable in prose, so the enforcement is that a breached budget voids the round |
| CO-7 | state survives the process, written atomically, locked | n-a by scope | single-run artifacts; no concurrent scheduled runs to protect against |
| CO-13 | the final attempt narrows to the blocking row | accepted | a rule that always narrows the last round would hide a second defect behind the first |
| DR-1 | gates and evaluations are different instruments | accepted | the skill cannot make anyone's CI fire. See "Two limits worth more than a row" below |
| DR-2 | a fixed corpus of known-good inputs, run on a schedule | accepted | the demo is the corpus; the trigger is a human, and that is escalated with DR-1 |
| DR-3 | evaluate weekly | n-a | no production traffic; the failure this catches does not accrue here |
| DR-4 | instructions and skills are behavior: versioned, reviewed, tested | accepted | `CONTRIBUTING.md` requires the fixture; nothing rejects a PR that ignores it |

## One limit you can close yourself

EX-1 is `accepted` because this skill runs wherever a skill can be read, and
the mechanism that would close it does not. On Claude Code it does. A
`PreToolUse` hook declared in a subagent's own frontmatter is registered only
while that subagent runs, fires on its tool calls, and can return
`permissionDecision: "deny"`, which prevents the call. That is a per-agent,
path-scoped bound on `Read`, which is exactly what the spec reviewer's brief
asks for in prose.

It is not in the shipped agent file, on purpose: a reader on another host would
inherit a mechanism their host ignores, and a constraint that silently does
nothing is worse than a stated instruction. Take it deliberately, on a host
that honors it:

```yaml
# In your copy of agents/old-coder-spec-intent.md, alongside `tools: Read`.
# Point the handler at a script that denies any Read outside the artifact
# directory the SPEC lives in, and returns permissionDecision "deny" with a
# reason the reviewer will see.
hooks:
  PreToolUse:
    - matcher: Read
      hooks:
        - type: command
          command: ${CLAUDE_PROJECT_DIR}/.claude/hooks/spec-intent-scope.sh
```

Two things to get right if you do. The handler must **deny by default and allow
by path**, not the reverse: a blocklist of directories you thought of is not a
bound. And it must fail closed, because a handler that errors and returns
nothing leaves the normal permission flow running, which is the same as no hook
at all. Prove both with a run where the reviewer tries to open a source file
and says it could not.

This works for `Read` because a path is a decidable thing. It does not
generalise to VE-1: bounding `old-coder-adversary`'s `Bash` would mean deciding
whether an arbitrary shell string writes, and a blocklist over shell syntax is
not a bound. That is why VE-1 is `delegated` and this one is not.

## Two limits worth more than a row

**A gauntlet that only runs on the author's machine is a gate, not an
evaluation.** This repository is the example. `drmikecrowe/old-coder` has never
run a GitHub Actions workflow: `actions/runs` returns `total_count: 0` against
a workflow committed in August. Every green CI run this repo's documents cite
is the upstream project's, and those are real, but they are not evidence about
this fork. Read your own CI the same way before crediting it in EVIDENCE. A
gate catches the change in front of it; an evaluation catches drift across
changes, and nothing does the second job here.

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
