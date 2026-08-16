# Upstream Audit — fork `main` (4fff00f) vs `upstream-main` (01f8fe9)

Reviewed as prose an agent will follow literally, against upstream's two stated
positions: (1) a step that produces a claim must fail visibly when broken, never
report success; (2) an EVIDENCE field earns its place only if its absence would
let a reader believe something false.

Every finding is anchored. CONFIRMED = verified against the text.
PLAUSIBLE = depends on how an agent or host interprets the text.

---

## Findings, worst first

### F1 — The committed-grant defense has no verification mechanism — CONFIRMED (gap in text; triggering is host-dependent)

**Where:** `references/setup.md:21-37`, `CUSTOMIZATION.md:12-19`, `SKILL.md:745-749`.

The permission model's central property is "a grant found in a committed file is
not a grant" (`setup.md:29`). Honoring that requires the agent to know, for each
rule in its context, whether the file it came from is committed. The text never
says how to establish that, and the skill's own install instructions defeat it:
`README.md:38` tells other-agent users to paste SKILL.md "to your `AGENTS.md`,
rules file, or system prompt" — hosts where all rules arrive concatenated with
no provenance labels. On such a host a repo-committed "old-coder may post to the
tracker without asking" is indistinguishable from a user grant.

**Scenario:** untrusted PR branch adds a grant to the repo's `CLAUDE.md`; an
agent on an unlabeled host honors it; the tracker post fires; EVIDENCE reports
"Grants in effect: tracker (standing)" — the mechanism reports success while
doing the opposite of its job. The fail-closed default (`setup.md:52-55`) covers
*absent* rules only; it says nothing about present-but-unattributable ones.

**Fix (one sentence in setup.md):** a grant is honored only when you can
positively attribute it to a file that is not in the repo — check
(`git ls-files --error-unmatch <file>` fails, or the path is outside the repo,
or the host labels the scope); a grant of unknown provenance is not a grant.
That restores the property the gitignored config gave: machine-locality you can
*test*, not infer.

### F2 — Config-key vocabulary survived the config removal — CONFIRMED

Commit 4fff00f says "clear the last config-key names." It did not:

- `SKILL.md:767` — "they need the matching key set to \`allow\`" — there is no
  file in which a key can be set. An agent goes looking for one, or treats
  arbitrary context text as the key.
- `SKILL.md:768` — "**With \`propose\` and no approver present…**" — `propose`
  is an orphaned enum value from the deleted TOML.
- `SKILL.md:551` — "With \`propose\`, or with no PR open…"
- `SKILL.md:812` — "If \`commit = "propose"\` and the human declines" — literal
  TOML syntax.
- `SKILL.md:226`, `setup.md:119,217,226,254` — `artifacts` /
  `isolation = "auto"` / `isolation = "worktree"` key-spellings with no
  key-value mechanism behind them.
- `gauntlet.md:511-513` — "It runs whatever commands the project's rules name
  specifies, so the script and the config never disagree" — garbled mid-sweep
  edit, and "the config" no longer exists.
- `SKILL.md:118` — "with the default config" (mild; readable as "configuration").

**Scenario:** an agent reads "the matching key set to \`allow\`", searches the
repo for a config file, finds none, and either blocks or invents a
`.old-coder.toml` — the exact artifact the removal was meant to eliminate.
These should all be rewritten in rule-scope vocabulary ("a standing user-scope
grant" / "with no grant and no approver").

### F3 — setup.md points the human at a file that does not exist — CONFIRMED

`setup.md:16`: "`RULES.md` at the repo root is the user-facing guide." The file
is `CUSTOMIZATION.md` (`SKILL.md:756-757` says so; `RULES.md` does not exist).
An agent following setup.md tells the human to open a nonexistent file. Note
the irony: the fork's own new adversary failure class is "names the diff invokes
that may not exist" (`agents/old-coder-adversary.md:42-45`).

### F4 — The fork README's install claim is false for the command it gives — CONFIRMED

`README.md:23` installs `https://github.com/amazingang/old-coder` — upstream,
which has no `agents/`, no `templates.md`, no `setup.md`. `README.md:26`
(fork-added) then asserts: "That installs everything, including the two review
agents." A user runs the command, gets a skill without the agents, and the
README told them the agents are included — reports success while doing nothing.
Also `README.md:38` names `adversary.md`; the file is `old-coder-adversary.md`.

Either point the install command at this fork, or scope the sentence:
"once merged upstream; today these ship only in this fork."

### F5 — The projection-staleness rule is addressed to nobody — CONFIRMED

`templates.md:367`: "**Regenerate it on every push.**" The skill never pushes
(`SKILL.md:103-105`) and ends at EVIDENCE. After the run ends there is no actor;
the human pushes later and the PR body silently describes a dead commit — the
STALE fallback (`templates.md:369-371`) requires the same absent actor. The SHA
footer is the real mitigation, but only for a reader who thinks to compare SHAs.

**Fix:** make the projection self-expiring instead of maintained — its verdict
line should read `PASSED WITH LIMITS — valid only for <sha>; if HEAD differs,
this body is stale`, so staleness is announced by the artifact rather than
prevented by an agent that no longer exists. Keep "regenerate" only as an
instruction for reruns of the skill itself.

### F6 — The fork's skill rules make the demo non-compliant, and the fork-authored TL;DR hides it — CONFIRMED

The fork made adversarial review mandatory at Tier 3 (`SKILL.md:623-628`: "not
optional at this tier") and added the Egress layer (`SKILL.md:342`). The demo is
Tier 3. Its gauntlet table (`demo-rate-limiter/evidence.md:113-127`) has neither
row — understandable, it predates both — but the TL;DR the *fork* wrote on top
(`evidence.md:16-19`, "Not proven:") omits both, while the fork's own template
requires Not-proven to list "every substituted or not-run layer"
(`templates.md:103-104`).

**Scenario:** a reader studies the showcase to learn what compliant output looks
like and learns that a mandated layer can be silently absent. The demo is the
best evidence the skill works; here it is evidence against the fork's own rule.
Fix is two lines in the demo TL;DR: "adversarial review: not run (layer
postdates this demo); egress: not run (ditto)."

### F7 — The TL;DR is a new claim-producing step with no check — PLAUSIBLE

`templates.md:245-262` guards the EVIDENCE TL;DR with prose only: "write it
last", "the tables are authoritative", anti-gaming rule 5 extended to it. Ask
upstream's question: what does a broken TL;DR do? A `PASSED` verdict over a
table containing a `SUBSTITUTED` row is caught by nothing — the adversary
attacks the diff, the gauntlet attacks the code, and `verifier.md`'s attack
order does not name TL;DR-vs-table consistency. The fork concentrated the
reader's attention ("the part most readers finish") on the least-checked part of
the report.

This is upstream-consistent risk — EVIDENCE prose was always self-reported — but
the fork added the amplifier. Cheap fix: one line in `verifier.md`'s attack
order and the adversary's brief for re-review rounds: *diff the TL;DR against
the tables; any disagreement is a finding.* That gives the claim a checker.

### F8 — CUSTOMIZATION's tracker-approval rule has no scope and loosens the strongest gate — CONFIRMED (minor)

`CUSTOMIZATION.md:187-193`: the example rule "an approving comment from a
maintainer on the linked issue counts as spec approval" is the only rule in the
file with no "**Where:**" line. It loosens the approval gate, so under the
fork's own model a committed copy must be ignored — yet the surrounding prose
reads repo-scoped ("If your tracker carries the approval"). It is also
redundant: `SKILL.md:192-195` already accepts tracker approval unconditionally.
Delete it, or give it "**Where:** your *user* rules" and say it merely restates
the default.

### F9 — SKILL.md is 816 lines against upstream's 305, and part of the growth is not load-bearing — CONFIRMED

Every line loads on every task. Concrete deletions that lose nothing an agent
needs mid-task:

- `SKILL.md:709-722` — the token-billing measurement ("a 26K baseline over 38
  turns was 46% of the total bill…") and the MCP-tooling advisory. This is
  rationale for a design decision, not instruction; it belongs in the agent
  files or ATTRIBUTION. ~14 lines.
- The never-push/never-PR rule is stated three times in SKILL.md alone
  (`:103-105`, `:219-221`, `:549-551`) and once each in setup.md,
  CUSTOMIZATION.md, templates.md. One statement plus one reminder at the
  projection site suffices; the third is drift surface.
- `SKILL.md:762-770` restates `setup.md:74-91` (the permission combining rule)
  — and the SKILL.md copy is the one carrying the stale `allow`/`propose`
  vocabulary (F2). State it once in setup.md; reference it from SKILL.md.
- `SKILL.md:784-815` (Setup section) overlaps `setup.md` §§ isolation/commit;
  after F2's rewrite, half of it can become pointers.

Order ~60-80 lines recoverable without losing a rule. Not found: padding in
gauntlet.md — its +507 lines are procedure (adversarial review, dismissal
burden, SHA binding, mutation hardening, entry-point skeleton), each answering
"what does this do when broken."

### F10 — ATTRIBUTION.md describes setup.md by its deleted mechanism — CONFIRMED (minor)

`ATTRIBUTION.md:62`: "`references/setup.md` — `.old-coder.toml`, isolation,
artifact layout." The file no longer mentions a TOML; the line describes the
current file falsely. (The `spec_to`/`evidence_to` mention at `:91` is fine — it
describes a historical commit.)

### F11 — Frontmatter and body disagree on the offer gate — PLAUSIBLE (minor)

`SKILL.md:3` (description): "then offer the loop in one sentence and stop" —
unconditional. Body `:27-33`: on autonomous runs, do *not* stop with an offer.
The description is what a host may read alone to decide behavior; an autonomous
host following it stalls into an empty room, the exact failure the body's
paragraph was added to prevent. Add "(when a reply is possible)" to the
description.

### Checked, no finding

- Adversary "one round" (`SKILL.md:705`) vs the two-round limit
  (`gauntlet.md:337`): reconcilable — one round per spawn, two rounds per layer.
  Not a contradiction.
- Demo TL;DR numbers (28/28 scenarios, 41 tests, 22/22 mutants, 13 layers, six
  rounds, round-6 `failed`): verified against the tables; all accurate.
- Scope conflict (user grant vs committed restriction): restriction wins, via
  "honor it only where it tightens" (`SKILL.md:749`) — adequately specified.
- The bundled-brief path: the fork *did* add the honest treatment — "say in
  EVIDENCE which path ran" (`SKILL.md:735-736`), the `review.log` † footnote
  (`templates.md:199-203`), and gauntlet.md's "What this layer cannot prove."
  Residual self-report ("registered" claimed while spawning generic) is
  inherent to any subagent claim and already covered by that section.
- LICENSE / third-party attribution (Apache-2.0 class adaptation): provenance
  recorded where it will be read; rejection of the "failure = saying looks
  good" incentive is the right call and is documented.

---

## The six questions

### 1. Does the divergence earn its place?

- **`setup.md` — keep.** The worktree artifact split ("Which tree each artifact
  is written in") prevents two genuinely silent losses (tracked file leaking
  into the human's tree; logs deleted unread at cleanup), and the durable-root
  resolution is executable, not aspirational. Loaded on demand, so its length
  is cheap. Defects: F2, F3.
- **`templates.md` — keep.** The closed status table, "mutation row has no
  prose form," and "a path to a file that does not exist is a fabricated
  citation" are checks in upstream's sense. PR #10 is already partially
  accepted. Defect: F5, and the TL;DR digest (see Q4).
- **`agents/` — keep.** Both briefs are executable and correctly asymmetric
  (spec reviewer blinded from the codebase; adversary bounded). The
  hallucination class is well-scoped to where type checker and suite are blind.
- **`CUSTOMIZATION.md` — keep** (user doc, never loaded per task). Defect: F8.
- **`ATTRIBUTION.md` — keep**; exactly what a contributing fork owes. Defect: F10.
- **`SKILL.md` +606 — mostly earns it**; delete list in F9. The additions that
  pay their way: the closed status vocabulary, the checker/negative-control
  notes, the approval-is-not-an-answer gate, the move-vs-modify split, the
  offer gate.
- **`gauntlet.md` +507 — earns it**; nothing to delete found.

### 2. Did the config removal work?

Partially — the problem moved. What was gained: no second format, and the
restrictive default fails closed, which a config file never did ("file missing"
vs "file missing but agent proceeds"). What was lost: **verifiability**. A
gitignored config was positively machine-local — a file at a known path whose
git status the skill could test. A rule's scope is only as attributable as the
host makes it, the text never tells the agent to attribute it, and the README's
own install path (paste into AGENTS.md) produces hosts where attribution is
impossible (F1). Facts moved too: pinned commands now depend on the host loading
a rule file the skill cannot check, backstopped only by detection — acceptable,
because detection order 1-2-3 (`gauntlet.md:3-10`) is explicit and CI-anchored.
Verdict: the removal was right (upstream's objection was real), but the model is
one sentence short of being reliable — add the attribution rule from F1, and
the fork is describing a mechanism it can rely on.

### 3. New instances of "reports success while doing nothing"?

- **Rules-based permissions: yes** — the worst one (F1). Broken (unattributable
  grant honored), it posts outward and EVIDENCE reports the grant as standing.
- **Projection: yes** (F5). Broken (nobody regenerates), a PR body asserts a
  stale verdict as current, indefinitely.
- **TL;DR: amplifier, not a new mechanism** (F7). Broken, it overstates to
  exactly the reader who stops at the top; no layer checks it.
- **Bundled-brief path: no.** The fork built the disclosure in; the residual
  self-report is the pre-existing property of the whole review layer, and
  gauntlet.md states it plainly.

### 4. Does the TL;DR pass upstream's field bar?

EVIDENCE TL;DR (`templates.md:99-116`), field by field:

- **Verdict** — passes. `PASSED WITH LIMITS` vs `PASSED` encodes information
  whose absence lets a skimming reader believe the stronger claim.
- **Not proven** — passes; it is the load-bearing field, and templates.md says
  so itself.
- **Proven** — borderline pass: the layer-carrying-the-weight clause adds
  information the tables don't state.
- **Delivered** — fails. Restates the SPEC header; absence misleads no one.
- **Read first** — fails. Navigation, not evidence; no false belief prevented.
- **The five-bullet "writeup below, in brief" digest** (mapping / gauntlet /
  review / limits / honest notes) — fails as a block. Each bullet duplicates a
  table one screen down, and each duplicate is a fresh surface for
  summary-vs-table disagreement — the defect class templates.md then needs a
  paragraph to legislate against (`:245-252`). The reader with a fixed
  attention budget is better served by four bullets than ten.

SPEC TL;DR: **Decide** passes (it surfaces the calls to overrule — genuinely
prevents a false "nothing contentious here"); **Out of scope** passes;
**Change/Why/Touches/Covers/Must NOT** are orientation that duplicates the
contract below. Recommendation: EVIDENCE TL;DR = Verdict / Proven / Not proven;
SPEC TL;DR = Change / Decide / Out of scope. That is the version upstream's bar
accepts, and it halves F7's attack surface.

### 5. Where does the fork contradict itself, or upstream?

- Stale config vocabulary vs "there is no config file": F2.
- `RULES.md` vs `CUSTOMIZATION.md`: F3.
- Skill mandates Tier 3 adversary + egress; the demo (the worked example) has
  neither and the fork's TL;DR doesn't disclose it: F6.
- Demo keeps upstream's status vocabulary ("Skipped layers", no
  `UNAVAILABLE`/`SUBSTITUTED` labels) that the fork has since replaced with a
  closed list — a kept-rule-upstream-changed case in miniature, except the fork
  is the one that changed it. One relabeling pass on `evidence.md:138-144`
  closes it.
- Description vs body on offer-and-stop: F11.
- Permission rule stated twice, one copy stale: F2/F9.

### 6. What should go upstream?

**Universal — any user of the skill wants these** (propose as separate PRs):

1. **Closed status vocabulary + anti-gaming rule 5 rewrite** (`SKILL.md`
   §EVIDENCE, `templates.md` status table). This is upstream's own "reports
   success" doctrine turned into a mechanism; the strongest single contribution
   in the fork.
2. **The checker notes** — fail-closed home-grown checks, negative controls,
   prove-the-control (`SKILL.md:406-427`). Grounded in the demo's own found
   bug (the vacuous negative control, `evidence.md:235-241`).
3. **Adversarial review as a bounded layer** — SHA binding, dismissal burden,
   grading, two-round cap, the agents split (`gauntlet.md:161-368`,
   `agents/`, commit 1f7bd7e). Big, but it answers the position upstream
   stated: every step of it says what it does when broken.
4. **The egress layer** (`SKILL.md:342`, `gauntlet.md:134-159`) — coverage and
   mutation structurally cannot ask its question.
5. **The hallucination failure class** (commit b0f8df5, the class only) — with
   its Apache-2.0 provenance note, already written.
6. **Manual-mutation hardening + the gauntlet.sh guard/skeleton**
   (`gauntlet.md:405-576`) — the mtime/bytecode fix is the demo's own war story.
7. **Move-vs-modify split, byte-identity check, mutation-on-relocated-code**
   (`SKILL.md:281-299`).
8. **Templates split** — already in flight as PR #10; land the TL;DR trimmed
   per Q4 or expect the field-bar objection.

**Fork opinion — keep local, or propose with a weaker claim:**

- **The rules-based permission model** (setup.md scopes, grants,
  CUSTOMIZATION.md). It is genuinely better than the TOML on upstream's own
  criterion (no new format), but it still is the thing upstream deferred: a
  permission model, an isolation chain, and an artifacts layout. Honor the
  split they asked for on #9 — isolation first, permissions later, and only
  after F1's attribution rule exists, or you would be upstreaming a mechanism
  with a known hole.
- **Projections / destinations-in-SPEC** — workflow plumbing for this fork's
  multi-agent setup; carries F5.
- **The token-economics rationale** (`SKILL.md:709-722`) — this fork's
  measurement, not doctrine.
- **The long offer-gate + autonomous exception** — upstream already asked
  (PR #7) to shorten and reposition; the fork's main still carries the long
  form. Align main with what upstream will merge, or the superset property
  costs a conflict on every future sync.

---

## Coherence

The divergence is one thesis and one workflow. The thesis — *every claim must
name the mechanism that would catch it lying, and every mechanism must fail
closed* — runs through the status vocabulary, the checker notes, the
adversarial layer, the egress layer, and the mutation hardening; those read as
a single mind applying upstream's own stated position more ruthlessly than
upstream has yet, and they are upstreamable as a coherent argument. The second
thing is plumbing for this user's environment — rule-scoped permissions,
artifact durability under worktrees, projections, TL;DRs — justified in the
thesis's vocabulary but not by its necessity, and it is where every loose end
in this audit lives (F1, F2, F3, F5, F8): the mechanisms that check claims got
finished; the mechanisms that grant permissions did not. Finish F1 and sweep
F2/F3, and the fork is a superset upstream can absorb in slices; ship as-is and
the plumbing is the part a skeptical reader would quote back.

---

## Addendum — revision to Q4 and F7 after author review

*Appended after the report above was already circulated; the original text is
unchanged. This section supersedes the Q4 recommendation and sharpens F7.*

The author's stated design intent: the TL;DR exists because the EVIDENCE report
is detailed enough that a reviewer needs a high-level overview to know **how to
read the detail**. That rationale changes the assessment.

**Q4, revised.** A reader facing a 250-line report summarizes it themselves
regardless — they skim the first screen and stop. The real alternative to a
TL;DR is not "reader consults the tables"; it is "reader forms their own
summary, worse than the author's." Framed that way, the TL;DR as a whole
*passes* upstream's field bar: its absence would let the reader believe
something false — whatever their skim produced. "Read first" in particular is
withdrawn from the fail list: it is the field that most directly does the
navigational job (in the demo it steers the skeptic to *Independent
verification — it is where the downgrade lives*, which is exactly right). The
trim recommendation (cut to Verdict/Proven/Not-proven) is **withdrawn**.

What stands from the original Q4:

- Read literally, upstream's bar as stated still fails "Delivered" and the
  five-bullet digest — they restate rather than prevent a false belief. Treat
  the original Q4 as a **prediction of upstream's objection**, not a verdict.
  The counter-argument ("the reader will summarize anyway; better they read
  ours, written from the tables") currently exists nowhere in the fork's text.
  Write it down where upstream will read it — in the PR description, or as one
  sentence in `templates.md` beside "write it last" — so the TL;DR arrives
  upstream with its defense attached instead of waiting to be flagged.
- The digest's drift cost is real but is a **priced trade** (navigation bought
  with duplication), not a defect — *conditional on F7's checker existing*.

**F7, sharpened — now the load-bearing finding.** F7 is independent of the
TL;DR's size: the part most readers finish is the only part nothing checks,
whether it is four bullets or ten. The fix is one line in two places:

> Diff the TL;DR against the tables; any disagreement is a finding.

added to `verifier.md`'s attack order and to the adversary's re-review brief.
With the checker, the TL;DR is a mechanism upstream's doctrine endorses — a
summary that fails visibly when it lies. Without it, ten restated claims are
ten unwatched drift surfaces, and the original F7 stands in full.

**Net for the PR-update agent:** keep the TL;DR, keep "Read first", do not
trim; add the checker line to `verifier.md` and the adversary brief; carry the
"reader summarizes anyway" defense into the upstream PR text.
