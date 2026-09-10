# Contributing

Thanks for considering it. This repo is small and opinionated, so it is worth
saying up front what gets merged quickly and what gets a long conversation.

## What this repo is, and why review is unusual here

`skills/old-coder/` is not documentation about code. **It is instructions that
coding agents will obey.** A pull request that changes one line of `SKILL.md`
changes what every agent loading this skill does next, on every repo it touches.

So the review question is never "is this sentence true?" — it is **"what will an
agent do differently after this merges?"** Expect reviewers to read your diff
that way, and expect a security-shaped read of any change that touches
approvals, permissions, what gets executed, or what gets written outside the
repo.

## The bar

**A rule earns its place if its absence would let someone believe something
false.** Not if its presence would be nice to have. That applies to rules in
`SKILL.md`, fields in the EVIDENCE template, and layers in the gauntlet alike.

The best contributions so far have all had the same shape: *here is a specific
way the skill fails, here is the run where I hit it, here is the smallest rule
that closes it.* An observed failure is worth more than a plausible one.

**Say what you left out.** If your fork does something more opinionated than
what you are proposing, say so and leave it out of the PR. Two of the most
useful PRs here did exactly that.

## Adding a gauntlet layer

A new layer has to pass three tests:

1. **Orthogonal** — it catches a failure class no existing layer catches.
2. **Can fail meaningfully** — you have watched it fail on a known-bad input.
   A layer nobody has seen fail is not a layer.
3. **Tool-ready** — a real command exists in the common ecosystems, or you have
   written the manual procedure.

Layers are cheap to propose and expensive to keep. Expect the second test to be
where most proposals stop.

## The failure mode we care about most

Read the note at the top of `SKILL.md` about mechanisms that report success
while doing nothing. This project has hit that five times — a coverage layer
that printed a percentage and exited 0, a gate that failed closed perfectly
while guarding a spelling, a mutation runner scoring a mutant it never
executed, an approval that was an answer to a different question, a green suite
reported from a tree that could not run it.

If your change adds anything that produces a claim, say in the PR what it does
when it is broken. If the answer is "reports success", it is not finished.

## Skill text is behavior

If a change to `SKILL.md` or `references/` alters what the gauntlet accepts,
ship the fixture that fails without it — usually a negative control in the
demo's self-tests, the way the orchestration and stamp controls arrived.
Review catches wording; only a fixture catches a mechanism that stops doing
what the text claims. A pure wording change needs none — say which kind your
PR is.

## Keeping `SKILL.md` short

The main file is loaded in full on every invocation, including for tasks that
will never use the rule you are adding. Detail belongs in `references/`, behind
a pointer.

**In one, out one.** If you add to `SKILL.md`, look for something that can move
to a reference or come out entirely. A file long enough to be skimmed is its
own fail-open: nothing tells you which rule the agent missed.

## Changing the demo

`demo-rate-limiter/` is the worked example, and changes to it go through the
loop the skill describes — spec revision first, RED test watched failing,
minimal implementation, full gauntlet, then `evidence.md` rebound to the new
commit with `tools/source_state.sh`. A demo change that skips the loop is not
a demo of the loop.

Run `./tools/gauntlet.sh` before opening the PR. It must exit 0.

## What belongs here, and what does not

This repository is a prose methodology plus one worked demo. It is deliberately
finished as a place to invent enforcement.

**It takes:** wording that makes an existing rule clearer or harder to
misread; fixtures, negative controls and layers that prove an existing claim;
corrections where the text says something untrue; re-cuts of fork-local work
for upstream; and translations.

**It does not take a new runtime.** If your idea needs a process to run, a
daemon, a credential, a scheduler, a per-agent capability, or a host feature to
enforce it, it does not belong in a skill file, and putting it here produces
either an instruction pretending to be a bound or a mechanism that only works
on one host. Those go to the runtime repo.

The line is not "small versus large". It is whether an agent that can only
*read* the text can honour the change. `skills/old-coder/references/ceiling.md`
is the standing list of rules that fail that test, each with its destination.
A PR that would move a row from `delegated` to `enforced` is the one kind of
change that is out of scope here no matter how good it is. The hooks tier below
is the single exception, on terms stated there; nothing else moves a row.

One exception, and it has a shape: an **opt-in** mechanism may ship as a
documented snippet a reader applies deliberately, never as a default in a
shipped agent or config file. `ceiling.md` describes the `PreToolUse` bound
this way for a reader on another host, and `hooks/README.md` says how to take
it. A default that silently does nothing on the reader's host is worse than a
stated instruction.

### The hooks tier

That exception is now a tier, and it has a directory: `hooks/`. It carries
host-specific bounds for Claude Code, opt-in for a portable reader and on by
default in this fork's own deployment. `docs/track-a2.md` is the plan that
builds it.

The two halves are never blended. The skill text keeps its claim that any agent
able to read it can honour it. A hook is where that claim stops and enforcement
starts, and a hook is the only thing entitled to say "cannot".

**This is what lets a row move, and it is the only thing that does.** A rule in
`ceiling.md` may leave `delegated` or `accepted` for `enforced` when a hook in
`hooks/` is what moves it, the row's evidence names the host the bound holds on,
and a recorded host probe proves it denies. Text asserting the move does not
earn it, and neither does a green CI check. For any mechanism that is not a
hook, the rule above stands: that PR is out of scope no matter how good it is.

**The tier's test, three clauses, all required.**

1. **A hook here is a bound.** It refuses something. A hook that injects
   context, rewrites a tool call, or logs is not in scope for this directory,
   however useful it is. The second clause is a proof of denial, and a hook
   that never denies satisfies it by having nothing to prove, which would let
   an on-by-default mechanism enter the tree untested through the one door
   marked "tested".
2. **A hook ships with a control that proves it denies.**
3. **The skill text never claims what only a hook enforces**, so a reader on
   another host can tell from the text alone which sentences are bounds for
   them and which are instructions.

The second clause is not satisfied by CI. A hook control needs the host: a probe
script plus a recorded denial, rerun and rebound on every hook change. CI can
verify that hook files parse and that a frontmatter references them. Only the
host can verify that they deny. State both halves inside the control, so nobody
reads the CI half as the proof. A hook without a control that proves it denies
is a bound that reports success while measuring nothing, which is this project's
oldest failure mode wearing a new hat.

**The repository is the source of truth; the install is a documented step.**
The handler is written and edited in `hooks/`. It is installed beside the
agents, under the same config directory they are copied to, because the address
has to follow the agent rather than the project: these agents review other
people's repositories, so a project-relative path would resolve only when the
skill runs against this one.

**A hook that ships must ship with its install step in the README**, and the
step must be checkable. Skipping it is silent: an unresolved hook path does not
error, it does nothing, and the tool call proceeds while every other check
stays green. `tools/hooks_registered.py` therefore reports the install state
and prints the exact command that fixes it. A tier whose setup a careful reader
cannot complete is a tier that ships instructions, not bounds. That is what "on by default in
this fork's own deployment" costs, and it is why the paragraph above still
governs a portable reader: what is a default here is a documented artifact they
apply deliberately, or do not.

**The boundary the tier does not move.** Anything belonging to the unattended
outer loop stays out: triggers, budgets held by calling code, durable state
across runs, derived rubrics, anything that runs with nobody at the keyboard.
Those go to the runtime repo carrying their rule ids, which is the join between
the two backlogs, and a hook is not a way to smuggle one back here. An object
that fails twice for want of that scope moves, with its failure signature
recorded.

## Practical notes

- Drafts are welcome, and a series of small independent PRs beats one large
  one. Say which PRs depend on which.
- CI runs on pull requests, but a first contribution from a fork needs a
  maintainer to approve the workflow run. That is normal; it is not stuck.
- Both `README.md` and `README-zh.md` exist. Updating only one is fine — say so
  in the PR and someone will follow up.
- Issues that describe a failure you actually hit are always welcome, even
  without a fix attached. The failure is the valuable part.
