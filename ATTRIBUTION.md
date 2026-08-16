# Attribution and Provenance

This repository is a **fork**. The loop it implements, the gauntlet that enforces
it, and the demo that proves it are not original work here. They were designed and
built upstream, and this document exists so that no reader has to guess which
parts are which.

## Origin

| | |
|---|---|
| Upstream | **[amazingang/old-coder](https://github.com/amazingang/old-coder)** |
| License | MIT — `Copyright (c) 2026 amazingang` (see `LICENSE`) |
| First fork point | `57ead18` — *"Merge pull request #5 from AmazingAng/fix/verification-followup"*, 2026-08-10 |
| Last merged from upstream | `01f8fe9` — *"Align README claims with current evidence"*, 2026-08-15 |

**This fork is in sync with upstream as of `01f8fe9`.** Upstream is an ancestor
of this branch, so the divergence below is additive: this fork contains
everything upstream has, plus its own work.

### Staying in sync

The intent here is collaboration, not a hard fork. Two working rules follow from
that, and the merge at `f6fc5ea` applied both:

- **Where upstream and this fork say the same thing, take upstream's wording.**
  Divergence that buys nothing makes every future merge more expensive. Two of
  this fork's changes were dropped in favour of upstream's text on exactly that
  basis, and one was dropped because upstream's rule was simply better — ours
  forbade hand-rolled mutation runners, which contradicted this repo's own demo.
- **Contribute upstream rather than accumulate locally.** Upstream has already
  accepted two changes from this fork (PRs #6 and #8), in modified form. See
  `CONTRIBUTING.md`, which is upstream's.

## The underlying idea is not upstream's either

The strategy originates with **Robert C. Martin (Uncle Bob)**, in
[this tweet](https://x.com/unclebobmartin/status/2080257779395154409):

> My current strategy is to not read any of the code written by my agents. […]
> What I do instead is to surround the agents with extreme constraints. Unit
> tests, gherkin tests, QA procedures, quality metrics, mutation testing, test
> coverage, and a plethora of others.

Upstream turned that paragraph into an executable loop. That translation — from
an aphorism to a procedure an agent can actually follow — is the substance of
the project, and it is upstream's.

## Who wrote what

### Inherited from upstream, then modified here

- `skills/old-coder/SKILL.md` — the loop, the tier model, the anti-gaming rules
- `skills/old-coder/references/gauntlet.md` — the layer catalogue and the risk model
- `skills/old-coder/references/verifier.md`, `verifier-case-study.md`
- `demo-rate-limiter/` — the worked example, including six rounds of independent
  verification and the honest notes about what those rounds found
- `README.md`, `README-zh.md`, `assets/`

### Added by this fork

- `skills/old-coder/references/setup.md` — `.old-coder.toml`, isolation, artifact layout
- `skills/old-coder/references/templates.md` — the SPEC and EVIDENCE templates
- `agents/adversary.md`, `agents/spec-intent.md` — the two reviews as agent definitions

### Upstream contributors

Credit for the inherited files belongs to the people who wrote them:

| Contributor | Commits at upstream HEAD |
|---|---|
| Li, Amazing Ang (`0xAA`) | 48 |
| Mike Crowe | 2 |
| klmtseng | 1 |
| tninja | 1 |

## What this fork changed

Nine commits, oldest first. Everything else is upstream's.

| Commit | Change |
|---|---|
| `f94737b` | Isolation (worktree/branch), independent review, and durable artifact directories |
| `bcd3c70` | Skill corrections and the setup procedure |
| `f5e6e00` | An answer to a question is not an approval — tightened the approval gate |
| `7e92f2c` | Offer the loop before starting it; clickable artifact paths |
| `c60ff89` | Close the gap between rules that exist and rules that fire |
| `6783698` | `may` → `is permitted to` in the permission model, so authorization does not read as capability |
| `1f7bd7e` | Ship the two reviewers as agent definitions; add the SPEC intent review |
| `ae437e1` | Drop the integration-tree layer, keep the warning it was built around |
| `b0f8df5` | Artifact TL;DRs, destination config (`spec_to`/`evidence_to`), and a hallucination hunt class |
| `0989b52` | This file, the license notice, and a correction to the demo claims |
| `f6fc5ea` | Merge upstream `01f8fe9`, resolving toward upstream wherever the meaning matched |

### Contributed back

| Upstream PR | Status |
|---|---|
| #6 — An answer to a question is not an approval | merged |
| #8 — Prefer the real mutation tool, and make a hand-rolled runner prove it ran | merged |
| #7 — Offer the loop before starting it | open, changes requested (shorten and reposition) |
| #9 — Config and isolation | open, split requested: isolation yes, `.old-coder.toml` deferred |
| #10 — Move the templates into `templates.md` | open, partially accepted |

## Third-party material

**`adversarial-agent-review` v1.0.1** — Apache-2.0.
<https://lobehub.com/skills/sharp-skills-skills-adversarial-agent-review?activeTab=skill>

One failure class was adapted from that skill's "hallucination audit" vector into
`references/gauntlet.md` and `agents/adversary.md`: names a change invokes that
may not exist — methods, flags, config keys, version constraints. **The adapted
text was rewritten and rescoped**, narrowed to the cases a type checker and test
suite cannot see. Its remaining six vectors were already covered by existing
lenses, and its framing ("failure = saying looks good") was deliberately rejected
as an incentive to fabricate findings. No other material from that skill is used.

## License

This fork is MIT, the same as upstream. The upstream copyright notice is retained
in `LICENSE` as MIT requires, with a second line covering modifications made here.
MIT grants no trademark rights; the project name and the banner artwork are not
covered by the copyright grant.
