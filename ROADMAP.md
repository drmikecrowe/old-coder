# Upstream Roadmap

The plan for moving this fork's work into
[AmazingAng/old-coder](https://github.com/AmazingAng/old-coder), one proposal at
a time. Written for the agent executing it. Companion to `UPSTREAM-AUDIT.md`
(what diverged and why) and `ATTRIBUTION.md` (provenance and PR history).

## Re-cutting an existing PR — the procedure

Validated on #10 (2026-08-17), which went from a #9-dependent diff carrying
`setup.md` and two rejected fields to a standalone `+214/−82`, restacked off
`upstream/main` and left in draft. Follow it step for step; each step exists
because skipping it produces a specific, nameable defect.

### Read the ruling

1. **Read the maintainer's comments on the PR itself**, not this file's summary
   of them: `gh api repos/AmazingAng/old-coder/issues/<n>/comments --jq '.[].body'`.
   Also read the PR's current title and body
   (`gh pr view <n> -R AmazingAng/old-coder --json title,body`) — it is usually
   stale by the time you re-cut, and you are about to be judged against what it
   currently claims.
2. **Write down the take-list and the leave-out-list verbatim before touching a
   file.** Every later step is a check against those two lists. On #10 the
   leave-out list was the per-layer wall-clock column and the Config header
   line; both had to be absent from the final diff *and* named as absent in the
   re-cut comment.

### Build the branch

3. **Fork main is a superset; the port selects, it never copies.** "Take main
   and apply it to upstream" means take the in-scope subset. Before porting,
   enumerate what main's version of each file carries that this PR must *not* —
   on #10 that was wall-clock, `Grants in effect`, `setup.md` references, the
   `Isolation` field, Orientation, the projections machinery, and the Phase 4
   agent references. If you cannot list the exclusions, you have not read main's
   version closely enough to port from it.
4. **Work in that PR's own worktree.** Each open PR has a persistent one — see
   `git worktree list`. Restack it with `git reset --hard upstream/main`. Never
   cherry-pick fork commits and never merge fork main into a contrib branch;
   both drag the whole divergence along, which is what put #9's commits on #10.
5. **Port by editing upstream's files.** Open fork main's version with
   `git show main:<path>`, copy the sections the phase names, and rewrite
   fork-only vocabulary into upstream's. Config, grant, and artifact-directory
   vocabulary are the usual offenders — they read as ordinary prose and quietly
   carry a dependency on deferred work.
6. **Respect this file's own sequencing.** A later phase that *extends* this PR
   must not be pre-merged into it. #10 deliberately omits the five-status closed
   vocabulary because 3e extends #10's three-way split and has to diff against
   upstream's then-current text.

### Verify before anyone sees it

7. **Sweep the changed files for out-of-scope vocabulary.** Expect zero hits:

   ```sh
   rg -in 'setup\.md|CUSTOMIZATION|Orientation|wall-clock|old-coder\.toml|adversar|spec-intent|grant|projection|/home/|ROADMAP|ATTRIBUTION|Isolation' <changed files>
   ```

   Every hit is either a defect or a carry you can defend out loud.
8. **After a move, hunt what now dangles** — repo-wide, in both directions:
   `rg -n '<old section heading>|<old file>|<new file>' .`. Reachability counts
   too: a template nothing points at is the F3 defect class, in public.
9. **Ask what else the change touches** — anything hashed, parsed, linted, or
   run in CI — and answer with command output rather than a guess. On #10 that
   meant checking `demo-rate-limiter/tools/source_state.sh` (confirmed
   `evidence.md` is outside its hashed set, so relabelling it does not
   invalidate the recorded tree hash) and confirming no script or workflow
   parses `evidence.md`.
10. **Commit signed (`-S`), and let the message name what was excluded** and on
    whose instruction. The exclusions are the part a reviewer cannot see.
11. **Get an independent review before pushing.** Spawn a context-free subagent;
    give it the worktree path, the base commit, the PR number, and the primary
    sources — and *not* your conclusions, or it will confirm them. Tell it
    explicitly to use `rg`/`fd` and never `grep`/`find`; subagents do not
    inherit those rules. Treat its output as claims to verify, not verdicts: on
    #10 its README finding was wrong, because upstream's README already omitted
    two other reference files, and checking took one command.

### Publish

12. **Mike's explicit yes, then** `git push --force-with-lease origin <branch>`.
    Force-pushing to the existing head branch is the expected move for a re-cut:
    it preserves the review threads and does not clear draft status. **Leave the
    PR in draft.**
13. **Never rewrite the PR body.** The maintainer's review answers the text that
    was there, and replacing it orphans the thread. Prepend a banner instead,
    keeping the original intact:

    > ⚠️ **Re-cut — the description below is the original and no longer matches
    > the diff.** It is kept as written so your review still reads against the
    > text it answered. See [the re-cut comment](<url>) for what this PR now
    > contains.

    Leaving a stale body *unbannered* is the worse failure: on #10 it advertised
    the two fields the maintainer had just rejected, at the top of the page,
    above his own review.
14. **Prefix the title `RE-CUT: `** so the change of state is visible in a list
    view. Prefer it to `RENAMED:`, which reads as a claim about the codebase
    rather than about the PR.
15. **Post the re-cut comment first, then edit the body** — the banner needs the
    comment's URL:
    `gh api repos/AmazingAng/old-coder/issues/<n>/comments --jq '.[-1].html_url'`.
16. **What the re-cut comment must contain**, in this order: that it is
    restacked, and on what; what was dropped, naming the objection it answers;
    what it carries now; **what the mechanism does when it is broken** —
    honestly, so if it is prose with no checker, say that rather than implying a
    gate; every field added *beyond* the accepted list, flagged as yours with an
    offer to strike it; every hunk outside the skill directory, offered as
    droppable; and every deliberate non-change disclosed. Disclose rather than
    let it surface in review — the proposal is stronger for answering the
    question itself.

## Standing rules — read before every proposal

1. **One proposal at a time, smallest first.** The maintainer reviews carefully
   and has accepted every well-scoped change so far. A small, self-contained
   change is quick to read and easy to say yes to; an omnibus PR is neither —
   #9 was split on exactly this.
2. **Frame every mechanism with the maintainer's own test:** *what does it do
   when it is broken?* They have stated it twice ("a mechanism that reports
   success while doing nothing… if the answer is 'reports success', it is not
   yet a check"). A proposal that answers that question in its own body gets a
   different reading than one that makes the reviewer ask it.
3. **Respect the field bar for anything touching EVIDENCE:** *a field earns its
   place if its absence would let a reader believe something false.* Stated on
   #10; it will be applied to everything.
4. **Branch mechanics.** Each PR branch cut fresh off `upstream/main`, carrying
   only its own diff. Re-cuts of existing PRs are `git push --force-with-lease`
   to the same branch so review threads survive — the maintainer asked for
   re-cuts; rewriting the branch is the expected move. Open as **draft**.
5. **After a merge, sync down.** Merge upstream into fork main and take
   upstream's wording wherever the meaning matches (the ATTRIBUTION rule).
   Fork main must remain a superset of upstream that merges cleanly.
6. **Every push and every PR/issue/comment needs Mike's explicit go-ahead.**
   Prepare branches and texts; do not post them unprompted. Commits are signed
   (`-S`).

## Submission mechanics — the concrete facts

**Repos and remotes** (as configured in this checkout):

| Remote | URL | Role |
|---|---|---|
| `origin` | `git@github.com:drmikecrowe/old-coder` | the fork; PR head branches live here |
| `upstream` | `https://github.com/amazingang/old-coder` | the target; `upstream-main` local branch mirrors its `main` (currently `01f8fe9`) |

PRs are opened **from `origin` branches against `AmazingAng/old-coder` `main`**
with `gh pr create -R AmazingAng/old-coder --draft` (except re-cuts, which
reuse the PR's existing branch). Keep the conventions the series already uses:
draft by default, a body that leads with the problem and states what the
mechanism does when broken, the series footer linking `drmikecrowe/old-coder`,
and the `🤖 Generated with Claude Code` line.

**Existing PR head branches** (re-cuts force-with-lease to these; never delete
or rename them, the review threads hang off them):

| PR | Branch on `origin` | Draft |
|---|---|---|
| #7 | `contrib/opening-gate` | no |
| #9 | `contrib/config-isolation` | yes |
| #10 | `contrib/templates` | yes |

**How to build a feature branch.** Always branch off upstream, never off fork
main — fork main carries the whole divergence and a branch cut from it drags
everything along:

```sh
git fetch upstream
git checkout -b contrib/<slug> upstream/main
```

Then **port by editing upstream's files, not by cherry-picking fork commits.**
The fork's commits are entangled (a8f6ba7 alone touches 11 files across eight
findings); the unit of contribution is a section of prose, not a commit. Open
the fork's version of the file (`git show main:<path>`), copy the sections the
phase names, and adapt them to upstream's surrounding text — upstream's SKILL.md
is 305 lines with different structure, so line numbers from the fork do not
transfer. Sanity-check every ported section for fork-only references
(`setup.md`, `CUSTOMIZATION.md`, `Orientation`, grants/scopes, wall-clock,
`old-coder-adversary` before Phase 4) — a dangling reference in an upstream PR
is the F3 defect class, in public.

**Where the source content lives** (all on fork `main`):

| Content | File on fork main |
|---|---|
| Offer gate (long form to be cut down) | `skills/old-coder/SKILL.md` §"First: was this loop asked for?" |
| Isolation invariant + worktree trap | `skills/old-coder/SKILL.md` §"Setup and configuration" → **Isolation**; `references/setup.md` §"Isolation detection chain" |
| Templates + accepted fields | `skills/old-coder/references/templates.md` |
| Checker notes / negative controls | `skills/old-coder/SKILL.md` §5 GAUNTLET, "Checker note" + two following notes |
| Mutation hardening + entry-point guard | `references/gauntlet.md` §"Manual mutation procedure", §"Gauntlet entry point" |
| Egress | `skills/old-coder/SKILL.md` layer table row 1; `references/gauntlet.md` §"Egress" |
| Move-vs-modify | `skills/old-coder/SKILL.md` §2 RED, "A pure move has no RED"; `references/gauntlet.md` relocated-code callout |
| Five statuses + anti-gaming 5–6 | `skills/old-coder/SKILL.md` §6 EVIDENCE + §Anti-Gaming |
| Adversarial layer | `references/gauntlet.md` §"Adversarial review by an independent agent" |
| Agents + two-ways-to-run | `skills/old-coder/agents/*.md`; `SKILL.md` §"The bundled agents" |
| Orientation + mechanical check | `references/templates.md` (commit `3e8407b`) |
| Rules/permission model (Phase 2 issue) | `references/setup.md` §§"Where settings come from"–"The permission combining rule"; `CUSTOMIZATION.md` |

**Reading the maintainer's rulings.** Their full re-cut instructions are
comments on the PRs themselves — read them before cutting, do not work from
this file's summary alone:
`gh api repos/AmazingAng/old-coder/issues/<n>/comments --jq '.[].body'`
for n = 7, 9, 10. Their two doctrine statements (the "reports success" test on
#6, the field bar on #10) are quoted in `UPSTREAM-AUDIT.md`'s preamble.

**Before any push:** the pre-publish review applies — read every line of the
branch diff, check for fork-only references and personal paths, and get Mike's
explicit yes. Pushing to `origin` contrib branches is outward-facing (the PRs
render immediately); it is never done on this roadmap's authority alone.

---

## Phase 1 — the three open PRs (maintainer has already ruled)

### 1a. PR #7 — Offer the loop · re-cut: shorten and reposition

Maintainer verdict: wants it, "not at this size or in this position."

- Cut the 37-line opening section to **~10 lines containing exactly the five
  rules the maintainer listed** (their comment on #7 names them):
  1. nobody asked + high-stakes heuristic → one-sentence offer, name the
     domain, two choices, stop
  2. create nothing before the answer
  3. a configured invocation naming this skill IS the ask; do not re-offer
  4. no addressee → autonomous rules, never a stalled run
  5. the offer is not spec approval
- **Position: immediately after the thesis paragraph** ("The human will NOT
  read your implementation…"), not above it. Drop all supporting argument —
  "the rules carry themselves."
- **Frontmatter description:** keep the PR's version, plus the F11 fix from
  fork commit `a8f6ba7` ("…and stop — but only when a reply is possible; an
  autonomous run records the domain and proceeds"). Explain in one comment
  sentence: the description contradicting the body is the same defect class
  the maintainer flagged on #6, and they singled out the autonomous clause as
  the part worth keeping.
- **After merge:** replace fork main's long-form section with the merged short
  form. Do not keep the long version locally.

### 1b. PR #9 — Config and isolation · re-cut: isolation only

Maintainer verdict: "take now: isolation… re-cut as isolation only, roughly 12
lines folded into the existing Setup section, with no new reference file.
Defer: `.old-coder.toml`."

- Survives (~12 lines in upstream SKILL.md's Setup section):
  - the invariant: *do not mutate the user's working tree to do your work*
  - declare the mechanism (worktree / branch / none) in the SPEC so the human
    can veto it before work starts
  - the trap: a fresh worktree contains no gitignored content; two acceptable
    outcomes (rebuild and run there, or fall back to a branch and record why),
    never report green from a tree that never ran the suite
  - the landing-tree caveat: an isolated tree and the landing tree can differ
    by ignored content; EVIDENCE says so when it applies
- Does **not** survive in this PR: the detection-chain table, artifact layout,
  durable-root split, `setup.md` itself, and anything permission-shaped. Those
  stay fork-local pending Phase 2.

### 1c. PR #10 — Templates · re-cut: split + accepted fields, standalone

Maintainer verdict: yes to the fields-only re-cut AND the split is "fine by me
if it comes independent of #9."

- Restack the branch directly off `upstream/main` (it currently shows #9's
  commits).
- Carries: `references/templates.md` holding the SPEC template, EVIDENCE
  template, Gherkin template, and tracker roll-up; `gauntlet.md` keeps a
  two-line pointer. Plus the four accepted fields:
  - the `N-A` / `UNAVAILABLE` / `SUBSTITUTED` split for layers not run
  - the Dismissed-findings section (one line each, naming the disproof)
  - the Structural-blind-spot line
  - the `## Revisions` section in SPEC
- Must **not** carry (explicitly rejected or dependent on deferred work):
  - the per-layer wall-clock column (rejected — stays a fork divergence;
    record it as deliberate in ATTRIBUTION)
  - the Config / Grants-in-effect header lines (depend on Phase 2)
  - the Orientation section and its mechanical check (Phase 5)
  - the projections machinery (fork-local, see "Stays local")
  - any reference to `setup.md`

**Land order: #10 → #7 → #9.** #10 is the accepted one and touches only
reference files; #7 is a positioning decision the maintainer said they expect
to land; #9's isolation cut is smallest but lands cleanest after the other two
stop touching the same SKILL.md region.

---

## Phase 2 — the config positioning question (issue, not PR)

The maintainer deferred `.old-coder.toml` because "a config file with
permission keys… changes what old-coder is — from a methodology in markdown to
a tool with a config format that every agent must now look for," and asked for
the question to be decided on its own. The fork has since **replaced** the TOML
with the rules-based model (`references/setup.md`, `CUSTOMIZATION.md`), which
answers that objection directly: no format, no file to look for — settings read
from the rule files every agent already loads.

- **Open an issue first, not a PR.** They framed this as a repo-owner
  positioning decision; an issue respects that, costs a read instead of a
  review, and invites the decision rather than presuming it.
- Lead with the two things they said they did not want lost, both upgraded:
  - **the restrict-only asymmetry**, now expressed as scope: grants live only
    in user-scope rules (not in the repo), committed rules carry facts and
    restrictions only
  - **the combining rule**: proceeds if policy permits AND (reversible OR
    approver present); policy cannot manufacture a human
- Include the **F1 attribution rule** up front: a grant is honored only when
  its provenance can be positively established as outside the repo (host
  label, path outside the tree, or `git ls-files --error-unmatch` failing);
  unattributable = absent. Disclose this rather than leaving it to surface in
  review — it is the first question the model invites, and the proposal is
  stronger for answering it itself.
- PR only after they signal. If they decline, the model stays fork-local and
  CUSTOMIZATION.md remains the fork's own doc; nothing else in this roadmap
  depends on it.

---

## Phase 3 — small pure wins (one PR each, this order)

Each of these is a universal fix in the maintainer's own doctrine, small
enough to review in one sitting. Sources are fork main; strip anything that
references fork-only files.

### 3a. Checker notes: fail-closed and negative controls

- Source: SKILL.md "Checker note" + the two follow-on notes (prove the control
  is non-vacuous; a control proves one case, not the constraint).
- Pitch: home-grown checks (grep gates, custom scripts, manual mutation
  runners) fail open by default; off-the-shelf tools have earned their failure
  behavior, home-grown ones have not. Grounded in the demo's own history: the
  first negative control was itself vacuous and was caught only because it was
  tested for its ability to fail (`demo-rate-limiter/evidence.md`, honest
  notes). The purest match to their "what does it do when broken" test in the
  whole fork — propose it first.

### 3b. Manual-mutation hardening + the gauntlet entry-point guard

- Source: gauntlet.md "Manual mutation procedure" (the runner must prove it
  executed each mutant; mutants as a committed data table; restore verified by
  `git diff --exit-code`; control mutant) and "Gauntlet entry point" (the
  skeleton, the `SPEC.md`-exists guard on the delete, `set -e` rationale,
  must-find-nothing grep exit codes).
- Pitch: the demo's own war story — same-size mutants sharing a bytecode
  cache, kills reported for mutants never run, a defect that can only inflate
  the score and therefore can never surface as red.

### 3c. The egress layer

- Source: SKILL.md layer-table row + gauntlet.md "Egress: what the change lets
  data reach" (origin / control / destination / bounds / precedent; removing
  the channel beats redacting it).
- Pitch: coverage and mutation report that a line ran; neither can ask whether
  the data on it *belongs* where it goes. A question no existing layer can ask
  is the cleanest possible case for a new one.

### 3d. Move-vs-modify: a pure move has no RED

- Source: SKILL.md "A pure move has no RED" (byte-identity via
  `git show <base>:<path>` diff; mutation on relocated code) + gauntlet.md's
  relocated-code callout (patch-by-location tests silently stop applying).
- Pitch: a green suite immediately after a move is the case most likely to be
  hollow; inventing a RED for a move produces a test that asserts the refactor
  happened — a named anti-pattern, not a substitute.

### 3e. Five-status closed vocabulary + anti-gaming rules 5–6

- Only after #10's three-status split has merged — this extends it, so it must
  be a diff against upstream's then-current text.
- Source: SKILL.md EVIDENCE step (closed list `PASSED / FAILED / N-A /
  UNAVAILABLE / SUBSTITUTED`, "a substitute is never a pass", the mutation row
  has no prose form), rewritten anti-gaming rule 5 (a substitute wearing a
  pass is fabricated even when every number is real), and rule 6 (never label
  a property you did not test; the pre-EVIDENCE sweep of docstrings and test
  names for behavioral claims).

---

## Phase 4 — the adversarial layer and the bundled agents (the big one)

Propose **last among the mechanism PRs**, once Phases 1 and 3 have landed the
smaller pieces: it is the largest addition (+~200 lines of gauntlet.md, two agent
files, SKILL.md wiring) and changes upstream's Tier 3 definition (upstream has
a self-attack "adversarial pass"; this replaces its ceiling with an
independent reviewer).

Likely two PRs:

1. **The layer** — gauntlet.md "Adversarial review by an independent agent":
   fresh context / no inheritance (fork-style = rubber stamp), assigned lenses
   with security mandatory on new output surfaces, the failure-class list, the
   dismissal burden ("dismissing a finding costs more than fixing one", an
   unfalsifiable dismissal is a CONFIRMED finding you did not fix), SHA binding
   (a review is a claim about a commit), finding-fixes are new code, the
   behavioural-vs-description grading with the human deciding, the two-round
   cap, and "what this layer cannot prove" (the self-report honesty section).
   SKILL.md gains the layer-table row and the Tier 3 mandate.
2. **The agents** — `agents/old-coder-adversary.md` and
   `agents/old-coder-spec-intent.md`, the two-ways-to-run contract (registered
   = enforced tools, bundled brief = honored tools, EVIDENCE says which), and
   the deliberate two-agent split (the spec reviewer must not reach the
   codebase). Include the intent-review step at end of SPEC.

Carry-alongs that must travel with PR 1:

- **The hallucination failure class** ("names the diff invokes that may not
  exist") **with its Apache-2.0 provenance note intact** — the adapted-from
  comment in gauntlet.md and the ATTRIBUTION paragraph. Do not ship the class
  without the attribution.
- The answer to the obvious question, stated without waiting to be asked:
  `review.log` is written
  by the author, so the layer rests on self-report — the "what this layer
  cannot prove" section IS the answer to "what does it do when broken," and
  the PR body should say so in those words.

If the size is a concern: the fallback split is failure-class list + dismissal
burden first (pure review discipline, no agents), SHA binding + grading
second, agents third.

---

## Phase 5 — Orientation (last, with its defense attached)

The renamed summary sections (fork commit `3e8407b`) walk straight into the
maintainer's field-bar caution from #10, so this goes last and arrives with its
defense already stated:

- The **"reader summarizes anyway" defense** (templates.md): the alternative
  to your summary is the reader's own skim-formed one, worse than one written
  from the tables — that is the argument that passes their bar, and it must be
  in the PR body, not just the file.
- The **mechanical check** that runs every task (verdict only over all-green
  tables; every non-passed row named; every number verbatim from a table) plus
  the verifier attack item and the adversary hunt item — the summary is a
  claim WITH a checker, which is the difference between this and a TL;DR.
- The **rename rationale**: "TL;DR" names and licenses the behavior the skill
  is fighting; "Orientation" is definitionally preparatory.
- Expect pushback on the digest bullets and "Delivered"; be ready to trim to
  Verdict / Proven / Not proven / Read first if that is the price of the
  mechanism landing. The check matters more than the field count.

---

## Stays fork-local (do not propose)

- **Per-layer wall-clock + cost-and-yield tier tuning** — explicitly rejected
  on #10. Keep; record in ATTRIBUTION as a deliberate divergence.
- **Projections / destinations-in-SPEC / ROLLUP–PR-body machinery** — fork
  workflow plumbing; depends on the Phase 2 grant model; propose only if
  Phase 2 resolves toward the rules model and they ask what else it enables.
- **Artifact layout, durable-root split, absolute-path option**
  (setup.md) — same dependency.
- **CUSTOMIZATION.md** — the fork's user doc for the fork's model.
- **README fork framing, ATTRIBUTION.md, UPSTREAM-AUDIT.md, this file.**

## Bookkeeping after each merge

1. Merge `upstream/main` into fork main; resolve toward upstream's wording
   wherever the meaning matches.
2. Update ATTRIBUTION.md's PR table and "what this fork changed."
3. Re-check the "Stays fork-local" list — anything upstream absorbed comes off
   the divergence ledger.
4. Rerun the sweep from UPSTREAM-AUDIT F2: a merge is exactly when stale
   vocabulary reappears.
