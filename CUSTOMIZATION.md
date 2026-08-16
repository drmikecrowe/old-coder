# Customizing old-coder

This skill has **no config file.** It reads its settings from the rule files your
agent already loads — `CLAUDE.md`, `AGENTS.md`, a rules directory, `.cursor/rules`.

A config format would be a second thing every agent has to know about, and the
skill's premise is that it is plain markdown any agent can follow. Rules are the
mechanism that already exists.

## The one thing to get right: scope

| Scope | In the repo? | Put this here |
|---|---|---|
| **User rules** — `~/.claude/CLAUDE.md`, your user rules directory, user `AGENTS.md` | No | **Grants** — may commit, may install, may post to a tracker, may fill a PR body |
| **Project rules** — the repo's `CLAUDE.md` / `AGENTS.md` / `.cursor/rules` | Yes | **Facts and restrictions** — the real commands, required signing, isolation, tighter limits |

**A grant in a committed file is not a grant.** A repo saying "may commit without
asking" would authorize every agent run by everyone who clones it, so the skill
ignores it. Restrictions travel with the repo; grants stay on your machine.

**No rule means ask first.** Every setting defaults to the restrictive value, so a
rule that fails to load costs you a question, never a surprise.

Two things are not grantable at all: the skill **never pushes** and **never opens a
pull request**, in any configuration.

The mechanism behind all of this — detection, isolation, artifact layout — is in
`skills/old-coder/references/setup.md`.

## No frontmatter, and no schema

Every rule below is a plain sentence naming the skill. There is nothing to
declare, no `applies-to:` header, no file the skill goes looking for. The words
`old-coder` in the sentence are the whole binding, which is why it works in any
rule format — including ones that do not exist yet.

If your agent's rule system is file-based with frontmatter (Cursor `.mdc`, a rules
directory), wrap these sentences in whatever envelope it expects. The content is
what matters; the envelope is your agent's business, and the skill neither reads
nor requires it.

One consequence worth stating plainly: the skill reads whatever your agent has
already put in its context. It does not search the repo for rule files. A rule in
a file your agent never loads is a rule that does not exist, and the skill will
quietly ask you first — which is the safe direction, but it will not tell you the
rule was missed.

---

Each one names the file to edit and gives text you can paste. The wording does not
have to match; the skill reads prose, not a schema.

## Let it commit as it goes

Checkpoint commits make the work reviewable and let the spec-drift check work at
all. Without this, the skill asks before each one.

**Where:** your *user* rules.

```markdown
old-coder may create checkpoint commits without asking.
```

If your repo requires signed commits or a trailer, that is a project fact, not a
grant — it belongs in the repo so it applies to everyone:

**Where:** the repo's `CLAUDE.md`.

```markdown
old-coder: sign every commit with -S.
```

## Commit the SPEC and EVIDENCE with the change

The default. Artifacts land in `.old-coder/<task>/` and are committed with the
work, which is what makes later spec drift a plain `git diff`.

Nothing to configure. To move where they land:

**Where:** the repo's `CLAUDE.md`.

```markdown
old-coder: write artifacts to docs/evidence/ instead of .old-coder/.
```

## Put EVIDENCE in the pull request body

The skill writes `EVIDENCE.md` to the artifact directory either way. This adds a
short projection — verdict, what is proven, what is not, and a link to the full
report — into the body of a PR **you have already opened**.

**Where:** your *user* rules.

```markdown
old-coder may write an evidence summary into the body of an open pull request.
Draft pull requests only.
```

Drop the second line to allow it on ready-for-review PRs too. The skill will not
create the PR — if none is open, it writes the block to the artifact directory
and tells you.

To make this the habit for one repo rather than a standing grant, put the
*intent* in project rules and leave the grant in user rules:

```markdown
old-coder: this repo reviews by PR — plan for the evidence summary to go in the
PR body.
```

## Post a roll-up to the issue tracker

A short note back to the issue the SPEC names: what was built, what was left
undone, traps for whoever picks up next.

**Where:** your *user* rules.

```markdown
old-coder may post its completion roll-up to the issue the spec names.
```

Without this the note is written to `ROLLUP.md` in the artifact directory for you
to post.

## Keep it out of my working tree

**Where:** the repo's `CLAUDE.md`.

```markdown
old-coder: always use a git worktree, never work in the checkout directly.
```

Worth knowing: a fresh worktree contains no gitignored files, so the gauntlet
sometimes cannot run there. The skill will tell you when that happens rather than
reporting green from a tree that never ran the suite.

## Pin the project's real commands

Detection reads `package.json`, `Makefile`, `pyproject.toml`, and the CI workflow.
When it guesses wrong, or when the real command carries setup the raw tool call
skips, say so.

**Where:** the repo's `CLAUDE.md`.

```markdown
old-coder: tests are `pnpm test:ci`, types are `pnpm typecheck`, lint is
`pnpm lint`. Do not call vitest directly — the wrapper sets up the test database.
```

This is the highest-value rule in the file. A guessed command does not fail
loudly; it produces confident, wrong evidence.

## Let it install tools unattended

The gauntlet needs a mutation tool, a coverage tool, and so on. By default the
skill lists what is missing in the SPEC and waits.

**Where:** your *user* rules.

```markdown
old-coder may install development tools it needs, pinned, without asking.
```

## Lock it down harder than the default

Restrictions are honored from any scope, so these can be committed.

**Where:** the repo's `CLAUDE.md`.

```markdown
old-coder: never install anything in this repo — report missing tools as
UNAVAILABLE. Never write outside .old-coder/ and the source tree.
```

## Unattended runs — cron, scheduled wakes, agent-to-agent

An unattended run has nobody to answer a question, so every ungranted setting
stays at its restrictive default and the run reports what it could not do. If you
want a scheduled run to get further, the grants must be in your user rules
*before* it fires.

The one thing no rule can substitute for is **spec approval**. An unattended run
records `spec approval: not obtained (autonomous run)` and claims lower
confidence. That is not a setting; it is the honest state of a run nobody
reviewed.

If your tracker carries the approval — a comment or a label from a named human —
say so, and the skill can cite that instead:

```markdown
old-coder: an approving comment from a maintainer on the linked issue counts as
spec approval. Cite it in the evidence report.
```

---

---

## Where these are read

The skill reads whatever your agent puts in its context. It cannot verify that a
rule file loaded, so it fails closed: no rule visible means ask first. If you
granted something and the skill still asks, the rule did not reach its context —
check the scope and the filename your agent actually reads.

The evidence report states which grants were in effect, so a reader can tell
whether a run had standing permission or was asking as it went.
