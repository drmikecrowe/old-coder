# One-Time Setup: `.old-coder.toml`, Isolation, Artifacts

This procedure configures the skill for a repo once, and can be re-run any time.
It **detects and proposes, then confirms** — it does not interrogate the human
with questions whose answers are already visible in the repo.

Nothing here is a precondition. **Missing config is never a blocker**: run with
the restrictive defaults below and mention in one line that setup exists. A
skill that stops to be configured deadlocks every unattended run on a fresh
repo, which is worse than running conservatively.

## The config file

Written at the repo root as `.old-coder.toml`:

```toml
isolation   = "auto"        # auto | worktree | branch | none
install     = "propose"     # propose | allow
commit      = "propose"     # propose | allow
commit_args = []            # flags the repo mandates on every commit, e.g. ["-S"]
tracker     = "propose"     # propose | allow — posting the roll-up to an issue
pr          = "propose"     # propose | allow — writing into a pull request body
pr_mode     = "draft"       # draft | ready — which kind of PR may be filled
artifacts   = ".old-coder"  # dir for per-task SPEC/EVIDENCE/logs; absolute when the config is local

spec_to     = "file"        # file | file+tracker
evidence_to = "file"        # file | file+tracker | file+pr

[commands]
test  = "..."   # detected from package.json scripts / Makefile / pyproject / CI config
lint  = "..."
types = "..."
```

| Key | Meaning | Default when absent |
|---|---|---|
| `isolation` | how work is kept out of the user's working tree | `auto` — run the detection chain below |
| `install` | is the skill permitted to install packages/tools without in-task approval? | `propose` — put it in the SPEC's setup plan and wait |
| `commit` | is the skill permitted to create checkpoint commits without in-task approval? | `propose` |
| `commit_args` | flags the repo *mandates* on every commit — signing (`-S`), a trailer, a sign-off. Policy says **whether** you are permitted to commit; this says **how** the repo requires it done | `[]` — but detect: a repo rule or CI check requiring signed commits is a mandate the skill must honor, not a preference |
| `tracker` | is the skill permitted to post the completion roll-up to the issue the SPEC names, without in-task approval? | `propose` — write the note into the artifact directory and let the human post it |
| `pr` | is the skill permitted to write a projection into a pull request body without in-task approval? **Never grants PR *creation*** — see "Filling a PR is not opening one" | `propose` |
| `pr_mode` | which PRs may be filled: `draft` only, or `ready` ones too | `draft` — a ready PR requests review from people, a draft does not |
| `artifacts` | root directory for per-task SPEC, EVIDENCE, and logs. Repo-relative, or **absolute** when the config is gitignored — see "Which tree each artifact is written in" | `.old-coder` at the repo root |
| `spec_to` / `evidence_to` | where each artifact is **published**, on top of the file that is always written — see "Destinations" | `file` — local only |
| `commands.test` / `.lint` / `.types` | the project's real commands | detect; if detection finds nothing, fall back to the ecosystem tables in `gauntlet.md` |

Values are only ever these spellings. Use the same key names verbatim in SPEC
and EVIDENCE when you cite them.

## Destinations

`spec_to` and `evidence_to` say where an artifact is **published**. They never
say where it lives. Every value begins with `file` because the local artifact is
written in every configuration, and that is not a formality:

- **Drift detection is a `git diff`.** An approved `SPEC.md` committed at
  approval makes later drift mechanically visible (`templates.md`). A tracker
  **issue body is mutable in place**, and its edit history is not something any
  reviewer will diff. Publishing to a tracker *comment* keeps the append-only
  property; publishing to the issue description does not. Prefer a comment.
- **Citations must resolve.** EVIDENCE cites `logs/tests.log`. Nothing published
  into a PR body or an issue can carry those logs, so a published-only report is
  one whose every citation dangles.
- **Tampering has a backstop.** A PR body is editable after review, by the author
  and by others, and binds to no SHA. The committed file is what makes
  anti-gaming rule 5 checkable at all.
- **The loop must terminate offline.** Tracker down, credentials absent, no
  network: the run still has to end at an artifact.

So publishing is a **projection**: re-derived from the file, idempotent, and
regenerated whenever the source state moves. A projection that is rebuilt cannot
go stale; a hand-maintained PR body is the worst case for freshness precisely
because it always looks current.

A projection is **short** — it is the roll-up mechanism (`templates.md`) pointed
at a new surface, not a copy of EVIDENCE. Full Tier 3 EVIDENCE is hundreds of
lines and the wrong thing to paste into a body with a character cap. Publish the
TL;DR, the verdict, the gauntlet headline, and a path to the full artifact.

**Hybrid needs no setting.** `spec_to` and `evidence_to` are independent, so
"SPEC in the tracker, EVIDENCE in the PR" is just two values that differ. There
is no mode to select and no combination to enumerate.

**Destination and permission stay orthogonal.** `spec_to`/`evidence_to` choose a
surface; `tracker`/`pr` decide whether this run may write to it unattended.
`evidence_to = "file+pr"` with `pr = "propose"` is coherent and common: build the
projection, write it to the artifact directory, and let the human paste it.

### Filling a PR is not opening one

`pr = "allow"` permits writing into the body of a pull request **that already
exists**. It never permits creating one. This skill does not open pull requests
in any configuration — the human opens the PR, the skill fills it.

The distinction is the whole safety argument. Filling a body the human already
published changes text on a surface they chose. Opening a PR requests review from
people and cannot be un-sent, which is the boundary this skill declines to cross
in its own description. If no PR exists, write the projection to the artifact
directory and say so; that is the `propose` outcome, not a failure.

`pr_mode = "draft"` restricts filling to draft PRs. A draft notifies far fewer
people, which makes it the honest default for a surface whose gate is "propose".

## Procedure (idempotent)

1. **Read the existing config** if there is one. Re-running setup is a normal
   operation: show the current value of every key and let the human change one
   without restating the rest.
2. **Detect**, don't ask:
   - commands: `package.json` scripts, `Makefile` targets, `pyproject.toml`
     (`[tool.pytest]`, script entries), `justfile`, `.mise.toml` tasks, and the
     CI workflow — CI is the most reliable source, because it is the invocation
     the project actually gates merges on.
   - isolation: whether this is a git repo, and whether the tree is dirty.
   - artifacts: whether a directory already exists from a previous run.
   - `commit_args`: repo rules and CI checks that mandate a commit style —
     required signatures, required trailers.
3. **Propose the whole file** as a diff-shaped block, each value annotated with
   where it came from ("test: from package.json scripts.test").
4. **Confirm once.** The human accepts, or corrects individual lines.
   **Write nothing before this point — including `.old-coder.toml` itself.**
   Setup proposes a config that grants the skill permissions; writing it and
   then asking inverts the gate. If nobody is present to confirm, do not write
   the file: run with the restrictive defaults and say so in EVIDENCE.
5. **Write `.old-coder.toml` and add it to `.gitignore`**, together with
   `<artifacts>/*/logs/` (see "Gitignored by default" and "Tracked or
   ignored?"). Skip the second entry when `artifacts` points outside the repo —
   there is nothing for git to track.
6. **Report** what was written; do not re-propose on later tasks unless asked or
   unless detection now disagrees with the recorded commands.

## Gitignored by default

Add `.old-coder.toml` to `.gitignore` when writing it. This is not tidiness: it
makes every permission **grant** local by construction. A grant that lives in
the repo is a grant to every agent run by everyone who clones it.

If the human explicitly wants the file tracked — a team standardizing the
commands — that is fine, subject to the next rule.

## Restrict-only asymmetry

Check whether it is tracked — do not assume:

```sh
git ls-files --error-unmatch .old-coder.toml   # exit 0 = tracked, non-zero = not
```

If `.old-coder.toml` is **tracked by git**, honor only the settings that
*tighten* permissions, and ignore the ones that *loosen* them:

| Setting | Tracked file is permitted to set it to | Ignored if tracked |
|---|---|---|
| `install` | `propose` | `allow` |
| `commit` | `propose` | `allow` |
| `tracker` | `propose` | `allow` |
| `isolation` | `worktree`, `branch`, `auto` | `none` |
| `artifacts`, `commit_args`, `[commands]` | any value — these grant nothing | an **absolute** `artifacts` path: it names one machine's filesystem, so fall back to the default and say so in EVIDENCE |

Rationale: a committed grant silently authorizes agents run by anyone who
clones the repo, including on an untrusted fork or a PR branch you did not
write. Tightening carries no such risk, so tightening travels with the repo and
loosening stays local. When you ignore a loosening setting, say so once in
EVIDENCE (`install = allow ignored: config is tracked`) rather than silently.

## The permission combining rule

State it once, apply it everywhere:

> An operation proceeds if **policy permits it AND (it is reversible OR an
> approver is present)**. Policy can grant standing permission; it cannot
> manufacture a human.

- **Reversible work proceeds unattended**: writing test files, running the
  suite, running the gauntlet, writing SPEC/EVIDENCE artifacts.
- **Installs, commits, and tracker posts are not reversible in the same cheap
  way**, so they need either standing policy permission (`install = "allow"` /
  `commit = "allow"` / `tracker = "allow"`) or an in-task approver. With
  `propose` and nobody there, do not do it — record the consequence in EVIDENCE
  and continue.

A tracker post is the one operation here that can reach beyond the repo: on a
hosted tracker it notifies people and cannot be un-sent. That is why it is
gated, and why `propose` means *write the note, do not post it*. The skill ends
at EVIDENCE; `tracker = "allow"` is the human moving that boundary themselves,
for one tracker, on one machine, in a file that is not committed.

## Isolation detection chain

The invariant, not the mechanism, is what matters:

> **Never mutate the user's working tree to do your work, and verify in the
> tree that will actually receive the merge.**

With `isolation = "auto"`, choose by detection. Declare the chosen mechanism in
the SPEC so the human can see and veto it.

| Condition | Isolation |
|---|---|
| Not a git repo | `none` — propose `git init` in the SPEC's setup plan |
| Git repo, parallel agents running or the user is actively working in the tree | `worktree` |
| Git repo, exclusive access | `branch` is sufficient |
| Worktree created but the gauntlet cannot run there | fall back to `branch`, and record why in EVIDENCE |

That last row is the common one, and it is not obvious: **a fresh worktree
contains no gitignored content.** No `node_modules`, no `.venv`, no build
outputs, no local `.env`. In many projects the gauntlet simply cannot run in a
new worktree until the dependency tree is rebuilt, which can cost minutes per
task. Two acceptable outcomes, and no third:

1. Rebuild the dependencies in the worktree and run the gauntlet there.
2. Fall back to a branch in the main tree, and write in EVIDENCE:
   `isolation: branch (worktree lacked <what> and could not run the gauntlet)`.

**Never report green from a tree that never ran the suite.** "Isolation
succeeded" is not a gauntlet result.

Whenever the isolated tree and the tree the change lands in differ by ignored or
untracked content, say so in EVIDENCE. A suite that passed in a worktree lacking
the main tree's `.env`, build outputs, or installed dependencies has not been run
against the tree that will actually receive the change.

## Artifacts layout

One directory **per task**, not per session — a session runs several tasks and
they would collide. Name it at SPEC time and keep using it for the whole task:

```
<artifacts>/<YYYYMMDD-HHMMSS>-<slug>/
  SPEC.md
  EVIDENCE.md
  ROLLUP.md        # only when the SPEC names a tracker issue
  logs/
    tests.log
    types.log
    ...
```

- `logs/` is created at the start of the gauntlet run, before any redirect. A
  redirect into a directory that does not exist runs the command not at all —
  no log, no result, and an EVIDENCE row citing a path that was never written.
- Timestamp is **UTC** (`date -u +%Y%m%d-%H%M%S`). Local time can produce two
  identical directory names across a DST fall-back.
- **No colons** anywhere in the name — illegal in Windows paths.
- Slug is lowercased and reduced to `[a-z0-9-]`, capped at roughly 40
  characters, so the full path stays inside path-length limits.

Per-task **outputs** live in this directory. Reusable **scripts**
(`tools/mutants.py`, `tools/gauntlet.sh`) stay at repo level, because EVIDENCE
promises the human can rerun them later; a script inside a dated task directory
is an output, not a tool.

Both scripts are **files the SPEC's setup plan must name by path**. That is what
turns "EVIDENCE promises the human can rerun them" into something that happens:
an unnamed, unauthorized script gets replaced under time pressure by a throwaway
edit in a scratch directory, and EVIDENCE ends up honestly reporting a gap
instead of citing a command. If the repo already has them from a previous task,
say so in the setup plan instead — reuse is the cheap case, silence is the
failure case.

### Tracked or ignored?

**Track `SPEC.md` and `EVIDENCE.md`; ignore `logs/`.** That is the default, and
the first half of it is not a preference.

**Gitignoring the artifact directory silently disables the spec-drift
mechanism.** The skill's enforcement for "the spec is append-only, never
silently drift" is: commit `SPEC.md` at approval, so any later divergence is a
`git diff`. A gitignored `SPEC.md` can never be committed, so there is nothing
to diff against — the rule survives as an instruction the agent may follow, and
loses the mechanism that made it checkable. Nothing warns you: the skill keeps
running, EVIDENCE keeps claiming append-only, and the guarantee is gone.

So the honest cost table:

| Choice | Audit trail | "Reproducible from the repo alone" | Spec-drift detection |
|---|---|---|---|
| Track `SPEC.md` + `EVIDENCE.md`, ignore `logs/` | travels with the repo | true, except log paths are local | **intact** |
| Track everything | travels with the repo | literally true | intact |
| Ignore the whole directory | local only | false | **gone** |

Ignoring the whole directory is defensible only where the evidence reaches
reviewers by some other durable route (pasted into a review, attached to a
ticket) *and* the owner accepts losing drift detection. If you choose it, say
both things in EVIDENCE — "artifacts gitignored; spec-drift detection not
available this run" — because a reader cannot infer it.

Whichever is in effect, state it in EVIDENCE. When `logs/` is ignored, note that
the log paths EVIDENCE cites are local only.

### Which tree each artifact is written in

Under `isolation = "worktree"` the tracked/ignored split above also decides
*where* the file is written. A worktree is deleted when the task ends, and
nothing gitignored inside it is committed, merged, or recoverable — it dies with
the directory.

| Artifact | Tracked? | Written in |
|---|---|---|
| `SPEC.md`, `EVIDENCE.md`, `ROLLUP.md` | yes | the **worktree** — they are committed with the change and reach the human through the merge |
| `logs/`, and anything else the repo ignores | no | the **durable root** (below) — it outlives the task |
| the whole task directory, when `artifacts` is gitignored | no | the **durable root** |

Both errors are silent. A tracked file written outside the worktree becomes an
uncommitted change in the human's working tree — the exact mutation isolation
exists to prevent. An ignored file written into the worktree is deleted, unread,
at cleanup, and EVIDENCE goes on citing its path.

Resolve the durable root from the **shared git directory**, not from the CWD or
the worktree's parent:

```bash
dirname "$(git rev-parse --path-format=absolute --git-common-dir)"
git check-ignore -q <path>    # exit 0 = ignored → durable root, not the worktree
```

In an ordinary repo that is the main checkout (`.git`'s parent). In a bare +
worktrees layout it is the container directory holding `.bare/` and the
checkouts — not itself a working tree, which is harmless: only gitignored files
go there, and durability is the whole requirement.

Do **not** take `git worktree list`'s first entry as "the main checkout". In a
bare layout the first entry is the bare repo, and the remaining entries are peer
worktrees in registration order with no canonical one among them.

Use the **same** `<YYYYMMDD-HHMMSS>-<slug>` directory name in both places, so the
two halves are recognizable as one task.

This applies to worktree isolation only. Under `branch` or `none` there is one
tree and everything goes in it; when `artifacts` already points outside the repo
the whole directory is durable and there is nothing to split.

When the halves are split, say so in EVIDENCE and cite the moved paths
**absolutely** (`/home/you/proj/main/.old-coder/<task>/logs/tests.log`) — a path
relative to the worktree does not exist there and will not exist anywhere once
the worktree is gone.

### Or skip the split: an absolute `artifacts` path

`.old-coder.toml` is gitignored by default, and a local config may hold a
machine-local value. So set `artifacts` to an **absolute path** and the whole
task directory is durable by construction — one location, resolved identically
from every worktree, nothing to compute, nothing lost at cleanup. Prefer this
when the repo already ignores the artifacts directory: it is the same outcome as
the table above, minus the two-place bookkeeping.

Two conditions, both hard:

- **Only in a gitignored config.** An absolute path in a tracked `.old-coder.toml`
  names one machine's filesystem and is wrong on every other clone — ignore it
  per the restrict-only table.
- **Only where you have already accepted losing spec-drift detection.** Nothing
  outside the repo can be committed, so `SPEC.md` is never a commit and later
  divergence is never a `git diff` ("Tracked or ignored?", row 3). Keeping that
  mechanism means a repo-relative `artifacts` and the split.

That is the real choice, and it is not about paths: **durable-and-unverifiable
versus verifiable-and-split.** State which one is in effect in EVIDENCE — the
reader cannot infer it from a path.
