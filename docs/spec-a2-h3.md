# SPEC - H3. The adversary's shell, bounded by grammar

Track A2 object H3. H1, H2 and H2b landed; their SPECs are at
`docs/spec-a2-h1-h2.md` and `docs/spec-a2-h2b.md`.

House rule: no em dashes.

> **AWAITING APPROVAL.** The `Decide` block below carried four rulings and all
> four are in, recorded under each one. RED is open. The banner flips to LANDED
> with the landing commit. Everything outside `Decide` was settled before
> drafting and is recorded so it is not re-argued.

## Orientation

- **Change:** `old-coder-adversary` gains a `PreToolUse` hook on `Bash` that
  denies every command not matching a written allowlist grammar. Two walls move
  to let it count: `tools/audit_sweep.py` stops refusing to lift a shell tool
  under a stated and narrow condition, and `references/ceiling.md` distinguishes
  an allowlist over a tiny grammar from the blocklist over shell syntax it
  already rejects.
- **Why:** VE-1, EX-5 and EX-7 are one gap seen from three rules. The adversary
  declares `Read, Bash, Grep, Glob`, and `Bash` is a general write path:
  `sed -i`, `git checkout`, `git commit`, `git push`. The brief's "reach for
  `Bash` only for git" is an instruction, and EX-1 in the same audit says scope
  is absent capability, not instruction.
- **Touches:**
  - `hooks/adversary-bash-grammar.py` (new), `hooks/test_adversary_bash_grammar.sh` (new)
  - `hooks/harvest/` (new): the step-zero evidence and the harvester that produced it
  - `skills/old-coder/agents/old-coder-adversary.md` (frontmatter `hooks:` block only)
  - `tools/audit_sweep.py`, `tools/test_audit_sweep.sh`
  - `tools/agent_frontmatter.py` (handler extension lookup; see Settled)
  - `hooks/README.md`, `hooks/probes/RUNBOOK.md`
  - `docs/loop-alignment.md`, `skills/old-coder/references/ceiling.md`,
    `docs/track-a.md`, `docs/track-a2.md`
  - `demo-rate-limiter/spec.md` REVISION 14, `demo-rate-limiter/tools/gauntlet.sh`,
    `demo-rate-limiter/evidence.md` (rebind)
- **Decide:** four. Three are capability the reviewer loses, one is what
  `enforced` will mean on these rows.

## Step zero, and what it did to the plan

Step zero for this object was evidence, not design, and the evidence
contradicts the object's own sketch.

**Method.** Every recorded subagent transcript under the host's Claude Code
project directories, selected by `*.meta.json` where `agentType` or
`customAgentType` is `old-coder-adversary`. Eight sessions, every `Bash`
`tool_use` block, no sampling. The harvester and its 57-row output land in
`hooks/harvest/` so the citation beside the grammar is reproducible rather than
a remembered number.

**What ran.** 57 Bash calls across 8 adversary sessions: 19 `git` (17 `git`,
2 `/usr/bin/git`), 8 `python3`, 6 `cd`, 5 `rg`, 4 `echo`, 4 `set -u`, 3 `ls`,
2 `sed -n`, 2 `find`, 2 `cat`, 1 `tail`, 1 `head`. Reached in later segments,
not first: `printf`, `chmod`, `cp`, `rm -rf`, `mkdir -p`, `env -u`, `sh`,
`rtk proxy`. Shell features, counted per command and overlapping: 28 pipes,
22 `;` chains, 16 stderr redirects, 11 multiline, 8 `&&`, 6 leading `cd`,
5 `||`, 4 `$VAR`, 2 backticks, 1 `>` redirect.

**What that does to the sketch.** `docs/track-a2.md` proposes git only, plain
arguments, no metacharacter. Measured against the harvest, that grammar admits
**8 of 57**. It is not a bound on a rare escape hatch; it ends `Bash` for this
agent while claiming to have covered its use.

| admits | grammar |
|---|---|
| 8 / 57 | the sketch: git only, plain arguments, no metacharacter |
| 13 / 57 | any read-only binary, plain arguments, no metacharacter |
| 44 / 57 | **this SPEC's grammar** |

The single sharpest correction: **`;` is the reviewer's punctuation, not an
attack.** 22 of 57 commands use it, every one a sequence of reads
(`sed -n '420,478p' x; echo ===; sed -n ...`). The object's acceptance criteria
name `;` as an excluded class with a negative control. That requirement and
"the grammar covers observed use" cannot both hold. This SPEC keeps the second
and converts `;` into a **positive** control, and the ruling is Decide 1.

The second correction is uncomfortable and is recorded rather than smoothed
over. The H2 adversarial round built a fixture tree under `$CLAUDE_JOB_DIR/tmp`
with `rm -rf` and `mkdir -p`, then ran `env -u CLAUDE_CONFIG_DIR HOME=... python3`
and `sh` against it, to test whether a permissive matcher plus a no-op handler
silenced the sweep. It did, the finding was upheld, and H2 was hardened at
`4559a7c` because of it. **This object's bound forbids that round.** The write
was outside the repository under review, so it was not the harm VE-1 names, and
the grammar still denies it, because a grammar that admits `rm -rf` on the
strength of its argument is not a grammar. The reviewer loses its ability to
reproduce an attack in a sandbox. That is Decide 2, and it is the largest real
cost in this object.

## Settled before drafting, recorded rather than re-asked

- **The handler is Python, not `sh`.** The grammar's core is quote-aware
  tokenization: `rg -n "a|b" src/` must not be read as a pipe, and `echo "$(x)"`
  must be. `shlex` with `punctuation_chars=True` is exactly that lexer.
  Reproducing it in POSIX `sh` means hand-writing a tokenizer inside a
  fail-closed handler, which is the "second thing that can be wrong" the H2b
  handler's own comments warn about. `python3` is already a hard dependency of
  every tool in `tools/`. The tier's declared dependency list in
  `hooks/README.md` gains `python3` for this handler and keeps `jq` and
  `readlink -f` for the other.
- **`tools/agent_frontmatter.py` and `tools/audit_sweep.py` learn the extension.**
  `lifted()` currently resolves a handler as `hooks/<stem>.sh`. It gains `.py`
  as a second candidate. Nothing else about the lookup changes.
- **`cd` is in the grammar, one argument, no flags.** It is a builtin with no
  write path, and it recovers 6 harvested commands. Denying it would buy
  nothing a reviewer could not get with absolute paths, at the cost of six real
  denials.
- **No path scoping.** This bound is over verbs, not locations. The reviewer may
  still read any file the host lets it read. VE-1, EX-5 and EX-7 are about write
  capability; read reach is EX-1's shape and a different object. Decide 4 is
  whether `enforced` may be written knowing that.
- **The brief is not rewritten.** `agents/old-coder-adversary.md` gains a
  frontmatter `hooks:` block and nothing else. Its prose keeps saying "reach for
  `Bash` only for git", which stays an instruction for a reader on another host
  and is what the hook enforces here. Clause 3 of the tier's test forbids the
  text claiming the bound.
- **Deny by default, allow by grammar, fail closed.** Same three rules as
  `spec-intent-scope.sh`: exit 2 on every unexpected path, `deny` via
  `hookSpecificOutput` on a decision, no explicit `allow` ever, because an
  allow would skip permission rules the user set.

## The grammar

Written here, and written again in the handler beside the harvest citation.

**Stage 1, the whole string.** A command containing a newline is denied: the
grammar is one line. The two literal stderr forms `2>/dev/null` (and
`>/dev/null`) and `2>&1` are removed before tokenizing. Nothing else may
contain `>` or `<`.

**Stage 2, tokenize.** `shlex`, POSIX mode, `punctuation_chars=True`,
`whitespace_split=True`. A tokenization failure, such as an unbalanced quote,
denies. Quotes are consumed by the lexer, so a quoted `|` is a word and a bare
`|` is an operator, which is how the shell itself reads them.

**Stage 3, reject tokens.**

| Denied | Why |
|---|---|
| any operator token other than `;`, `&&`, `\|\|`, `\|` | `>`, `<`, `&`, `(`, `)` reach a file or a subshell the allowlist never approved |
| any word containing `$` | command substitution and parameter expansion both reach code the grammar cannot see |
| any word containing a backtick | the older spelling of the same thing |

**Stage 4, split into segments** on the four permitted operators and check each
one. A composition of reads is a read; that is the whole argument for admitting
them.

**Stage 5, per-command rules.** The head must be one of these, and nothing else.

| Command | Bound |
|---|---|
| `git`, `/usr/bin/git` | after optional `-C <path>` and `--no-pager`, the subcommand must be one of `diff show log status blame cat-file ls-files ls-tree rev-parse describe shortlog`. `-c`, `--exec-path` and `--output*` are denied wherever they appear: each reaches a command |
| `rg`, `grep` | any argument, except `--pre*` and `-f`/`--file`, which run or read a program |
| `sed` | `-n` only, and every script argument must match `^\d+(,\d+)?p(;\d+(,\d+)?p)*$`. A general sed script writes with `w` and `s///w` |
| `find` | predicates limited to `-name -iname -type -maxdepth -path -o -a -not`. `-exec`, `-ok`, `-delete`, `-fprintf`, `-fls` all execute or write |
| `tail` | any argument except `-f`/`--follow`, which never terminates |
| `cat head ls wc file sha256sum stat echo true` | any argument |
| `cd` | exactly one argument |

Everything else denies, `python3` and `sh` included, by name in the reason.

**Measured coverage: 44 of 57 harvested commands pass.** The 13 denials are
7 `python3` (6 multiline `-c`, 1 running a repo tool), 4 `set -u; VAR=...`
sequences including the H2 sandbox, 1 `rtk proxy` wrapper, and no accidents.
Every denial is a class this SPEC excludes on purpose.

## The first wall: `tools/audit_sweep.py`

Its `lifted()` hard-returns `False` for every tool in `SHELL`, and its docstring
says a future object that bounds a shell by an allowlist grammar changes the
rule deliberately and says so. This is that object, and the change carries its
own controls, because a rule that used to be "never" and becomes "sometimes" is
a rule that can now be earned by declaration.

A shell tool is lifted only when **all four** hold:

1. the matcher names the tool exactly, per the existing `names_exactly` rule;
2. the handler stem appears in a new module constant,
   `ALLOWLIST_SHELL_HANDLERS = frozenset({"adversary-bash-grammar"})`;
3. a probe record for that stem declares the handler's **current** sha256, which
   is the existing freshness rule;
4. the same record declares `grammar: allowlist` on its own line.

**What this does and does not prove, stated rather than discovered.** The sweep
cannot read a handler and decide whether it is an allowlist. Nothing short of
executing it could, and a sweep that executes handlers is a worse idea than the
one it replaces. So condition 2 is a human assertion living in the sweep's own
source, and condition 4 is the same assertion living in the probe record. Their
value is not that they stop an attacker: a contributor who edits the constant
can assert anything. Their value is that they cannot be reached by accident, and
that the sha256 binds both assertions to one version of the code. That sentence
goes in the docstring, not only here.

## The second wall: `references/ceiling.md`

It currently reads: bounding `old-coder-adversary`'s `Bash` would mean deciding
whether an arbitrary shell string writes, and a blocklist over shell syntax is
not a bound. **That sentence is correct and is not deleted.** It gains the
distinction it was missing: an allowlist over a tiny grammar is a different
claim, because it never decides what a string does. It decides whether a string
is one of a small number of shapes, and refuses everything else, including every
string whose effect it cannot determine. Deciding "does this write" is
undecidable in general; deciding "is this `git diff` with plain arguments" is a
pattern match.

The paragraph that replaces it states the cost in the same breath: the grammar
buys the bound by refusing 13 of 57 things the reviewer has actually done, and
the reviewer is worse at its job in exactly the way the numbers say.

## Scenarios

```gherkin
Feature: the adversary's Bash is bounded by an allowlist grammar
  Scenario: a plain read passes
    When  the handler receives `git diff main...HEAD --stat`
    Then  it does not deny

  Scenario: a sequence of reads passes
    When  the handler receives `sed -n '1,40p' a.py; echo ===; sed -n '90,99p' b.py`
    Then  it does not deny
    And   this is the case the object's sketch would have refused

  Scenario: a pipe into an allowed sink passes
    When  the handler receives `rg -n "a|b" src/ | head -30`
    Then  it does not deny
    And   the quoted pipe is a word, not an operator

  Scenario: stderr discard passes
    When  the handler receives `git log --oneline 2>/dev/null`
    Then  it does not deny

  Scenario: an in-place write is denied
    When  the handler receives `sed -i s/a/b/ src/x.py`
    Then  it denies, and the reason names the sed flag

  Scenario: a redirect is denied
    When  the handler receives `git diff > /tmp/out`
    Then  it denies, and the reason names the redirect

  Scenario: a substitution is denied
    When  the handler receives `echo $(git push)`
    Then  it denies, and the reason names the substitution

  Scenario: a backtick substitution is denied
    When  the handler receives "echo `git push`"
    Then  it denies

  Scenario: a write hidden behind an allowed head is denied
    When  the handler receives `git diff && rm -rf /tmp/x`
    Then  it denies, and the reason names rm

  Scenario: a git subcommand outside the grammar is denied
    When  the handler receives `git commit -m x` or `git push`
    Then  it denies, and the reason names the subcommand

  Scenario: git -c is denied wherever it appears
    When  the handler receives `git -c core.pager=touch\ x log`
    Then  it denies

  Scenario: an unbalanced quote is denied
    When  the handler receives `rg -n "unterminated src/`
    Then  it denies, and the reason says it could not tokenize

  Scenario: a non-Bash tool call gets no decision
    When  the handler receives a Read payload
    Then  it exits 0 with no output

  Scenario: the fail-closed paths
    When  stdin is empty, or is not JSON, or is not an object
    Then  the handler exits 2

  Scenario: every harvested read command passes
    Given hooks/harvest/harvest.jsonl
    When  each of the 44 in-grammar commands is checked
    Then  none is denied
    And   each of the 13 excluded commands is denied

Feature: the sweep lifts a shell tool only under the four conditions
  Scenario: all four hold
    Given an agent whose matcher names Bash exactly
    And   the handler stem is in ALLOWLIST_SHELL_HANDLERS
    And   a probe record names its current sha256 and `grammar: allowlist`
    When  the sweep runs over an audit where VE-1 reads enforced
    Then  it exits 0

  Scenario: a permissive matcher earns nothing
    Given a fixture agent with `matcher: .*` and a handler that exits 0
    When  the sweep runs
    Then  it exits 1, as it did before this object

  Scenario: an unlisted handler earns nothing
    Given a matcher naming Bash exactly and a handler stem not in the constant
    When  the sweep runs
    Then  it exits 1

  Scenario: a record without the grammar line earns nothing
    Given every other condition satisfied and no `grammar: allowlist` line
    When  the sweep runs
    Then  it exits 1

  Scenario: a stale record earns nothing
    Given the handler changed since the probe
    When  the sweep runs
    Then  it exits 1, naming the hash mismatch
```

## Must NOT

- No blocklist anywhere in the handler. Every rule is "this shape is allowed",
  and the default arm is a denial.
- The handler must not execute, expand, or resolve any part of the command it
  is judging. It reads a string and matches shapes.
- No path scoping smuggled in. If this object starts deciding which files the
  reviewer may read, it has become EX-1 and the rows it claims are wrong.
- `ALLOWLIST_SHELL_HANDLERS` holds one stem. It is not a mechanism for lifting
  future shells, and a second entry is a second object with a second probe.
- No change to `agents/old-coder-adversary.md` beyond the frontmatter block.
- The H2b probe record and EX-1's `enforced` are untouched. This object does not
  reopen a landed one.
- No em dash in authored prose. The harvested commands are a quoted transcript
  and keep their own punctuation exactly.

## Verification contract

Restated at the head of GREEN before any layer runs, per the loop.

The 21 computed layers from H2b's contract, unchanged, all exit 0, plus one new
layer, so `contract-ids` names 22.

| Row | What it proves | Threshold |
|---|---|---|
| `bash-grammar-controls` | the handler denies each excluded class and allows each harvested read | all cases pass; the driver reports failure against an always-allow handler |
| `audit-sweep-controls` | the shell lift is reachable only under all four conditions | all cases pass, the four negative cases included |
| `audit-sweep` | VE-1, EX-5, EX-7 reading `enforced` is supported | exit 0 |
| `ceiling-ids` | the audit and the ceiling name the same end states | exit 0 before and after the audit edit |
| `hooks-registered` | the frontmatter names a handler that exists and runs | exit 0 |
| `contract-ids` | the SPEC's contract and the harness agree | exit 0, 22 layers |

**Non-vacuity, and it is the point of the controls, not a formality.** Every
negative control is run twice: once against the real handler, where it must
deny, and once against a stub handler that exits 0 with no output, where the
driver must report failure. A control suite that passes against a handler which
allows everything is measuring nothing, which is this repository's oldest
failure mode.

Host rows, which cannot run in CI:

| Row | What it proves | Who runs it |
|---|---|---|
| negative control | the runtime denies the reviewer a write | Mike |
| positive control | the runtime allows the reviewer a harvested read | Mike |
| freshness | the record names the current handler's sha256 | derived, checked by the sweep |

Host probes are prepared by me and run by Mike. I write the commands and the
expected shape; I never write a result. The record declares
`handler sha256: <64 hex>` on its own line, and any edit to the handler,
including a comment, invalidates it.

**Two limits found while building it, recorded rather than left for the round.**

1. **Code reached through git's own configuration.** `git diff` honours
   `diff.external` and the textconv filters `.gitattributes` names, both read
   from the repository being examined. A repository that configures either runs
   that program when the reviewer diffs it, and the command string says only
   `git diff`. The grammar cannot see it, because the code is not in the
   command. This matters here specifically: the reviewer exists to read
   repositories somebody else wrote. Refusing `-c` and `--exec-path` closes the
   spelling where the command carries the configuration, not the spelling where
   the repository does. Closing it properly means forcing `-c diff.external=`
   and friends onto every invocation, which is a handler that rewrites tool
   calls, and clause 1 of the tier's test puts rewriting outside `hooks/`. So it
   is a stated limit, and it is no worse than the situation before the hook.

2. **Python is not linted by the gauntlet.** `ruff` and `mypy` run over the demo
   directory, so neither reaches `hooks/*.py` nor `tools/*.py`. The shell half
   does reach `../hooks/*.sh`. This object does not extend them: doing so drags
   pre-existing violations in `tools/` into an unrelated change. Named here
   because the handler ships unlinted, held only by its 115 behavioural cases,
   and a reader should know which instruments graded it.

**The conflict of interest, out loud.** This object bounds the reviewer that
reviews it. The adversarial round is spawned fresh, bound to the commit range
with the tree hash recorded, and runs **before the hook is registered in the
frontmatter**, so the reviewer that grades this work holds the same unbounded
`Bash` every previous round held. Registering first would grade the bound with
the bound applied, and a reviewer denied the tools it needs to falsify a claim
is a reviewer that returns no findings for the wrong reason. The evidence record
states which of the two orders was used, and it will say "before registration".

Budget: two rounds. The same failure signature twice stops the object and
records it, rather than earning a third round.

Review layers: human SPEC approval, and one adversarial round.

## Decide

Four rulings. Nothing else in this file is open.

**1. `;`, `&&` and `|` are in the grammar, and `;` becomes a positive control.**
The object's acceptance criteria name a chain (`;`) as an excluded class needing
a negative control. The harvest says 22 of 57 real commands use it for
sequencing reads. I am proposing the grammar admit it, and that the negative
control for the chain class be `git diff && rm -rf /tmp/x` instead: a chain
whose second segment is not in the allowlist. That keeps a control on the class
of harm (a chain reaching a denied command) and drops the control on the class
of syntax. Three of your four negative controls survive as written.
*Ruling needed: approve the substitution, or hold the criterion and take the
13-of-57 grammar.*

**RULED: allow.** The grammar admits `;`, `&&` and `|`, each segment checked
separately. The chain-class negative control is `git diff && rm -rf /tmp/x`.

**2. `python3` is denied entirely, and so is the sandbox reproduction.**
This costs the reviewer two things it has demonstrably used. Six multiline
`python3 -c` invocations parsed `evidence.md` tables, checked `gauntlet.sh`
layer registration, and ran verdict regexes: those produced findings. One call,
`python3 tools/contract_ids.py`, re-ran a repo check to falsify a claimed-green
row, which is a reviewer verifying rather than believing. And the H2 round's
fixture sandbox, which produced an upheld finding against this very tier, is
forbidden. There is no version of this bound that keeps them: `python3 -c` is
arbitrary code, and a grammar admitting it admits everything.
*Ruling needed: accept the loss as specified, or name a carve-out and accept
that it is a hole in the bound.*

**RULED: deny, no carve-out.** The ruling was taken against the eight calls
read one by one, not against the principle, so the cost is recorded as measured
rather than as feared.

| Call | What it did | In the grammar |
|---|---|---|
| 1 | three regex patterns over `evidence.md`, every match | `rg -n`, and `rg -U` for the one multi-line pattern |
| 2 | list and count `run_layer` names in `gauntlet.sh` | `rg -n '^run_layer'` |
| 3 | **run `tools/contract_ids.py`** | **nothing reaches it** |
| 4 | find lines mentioning the gauntlet in `evidence.md` | `rg -n` |
| 5 | count layer calls, count table rows, compare | two or three `rg`/`sed -n` calls in place of one |
| 6 | count pass/fail/unverified rows | one `rg -c` per status |
| 7 | find a table's header line | `rg -n` |
| 8 | search a saved diff for `sha256` and `probe` lines | `rg -n`, a direct translation |

Seven of eight were Python used as a richer grep, and the grammar reaches all
seven, at a cost of roughly one extra call where the reviewer was counting two
things to compare them. Against a 10-call budget that is a squeeze, not a wall.

**Call 3 is the real loss and it does not survive.** The reviewer can no longer
re-run a repo check to test whether a row the author reported green is green. A
carve-out for `python3 <path>` was considered and refused: the only rule that
admits call 3 is "Python may run a file from the repository", and the
repository is the thing under review. EX-8 already holds that repo content is
untrusted input and that a file directing the reviewer is a finding in its own
right. A grammar refusing `-c` while executing `tools/anything.py` out of the
tree under review has a hole shaped exactly like the threat the audit already
names.

The mitigation is not in this object. When the reviewer cannot verify a
claimed-green row it reports it unproven rather than passing it, which is
already how VE-5 handles absent evidence. Writing that into the brief is a
separate change.

**3. `2>/dev/null` and `2>&1` are the only redirects in the grammar.**
Your negative-control list names a redirect (`>`). 16 of 57 commands use a
stderr redirect. I am proposing the two literal spellings above be permitted,
because `/dev/null` is a fixed sink and `2>&1` is a descriptor dup, and that
`git diff > /tmp/out` remain the negative control for the redirect class. The
grammar therefore admits the `>` character in exactly two byte sequences and
nowhere else.
*Ruling needed: approve, or deny all redirects and lose those 16.*

**RULED: approved.** Those two spellings only. Every other use of `>` or `<`
denies.

**4. What `enforced` will mean on VE-1, EX-5 and EX-7.**
After this lands, `old-coder-adversary` cannot write through `Bash` on this
host, and can still read any file the host lets it read. VE-1 is "the verifier
holds no write capability", so the row is honestly closed. But a reader who sees
three rows flip may hear a broader claim than the one made. I propose the
evidence column on all three say plainly: bounded on Claude Code by
`hooks/adversary-bash-grammar.py`, instruction-only elsewhere, write capability
only, read reach unbounded and deliberately out of scope.
*Ruling needed: approve that wording as the end state, or say the rows stay
`delegated` until read reach is bounded too.*

**RULED: agreed.** The three rows move to `enforced` and each evidence column
states the three limits: write capability only, Claude Code only, read reach
unbounded on purpose.

## Revisions

**Adversarial round 1, 2026-09-12.** Spawned fresh, bound to `4c34bde...19a2a36`,
tree `f4543ac8af211553`, run **before the hook was registered** in
`agents/old-coder-adversary.md`, so the reviewer grading this object held the
same unbounded `Bash` every previous round held. Budget 10 calls, all spent.

Two findings, no escape from the grammar.

**Finding 1, upheld and fixed.** `tail -F` was allowed. The grammar refuses
`tail -f` on the ground that it never terminates, and `-F` is GNU's
`--follow=name --retry`, which hangs exactly as long. Reproduced before fixing:
the handler exited 0 with no output on `tail -F /var/log/syslog`. The fix closes
the class rather than the spelling, because short options cluster and `-fn10`
follows too: any short-option argument containing `f` or `F`, and any long
option starting with `--follow` or `--retry`, now denies. Three controls added.

**Finding 2, rejected with evidence.** `find -print0` and `find --` are denied,
and the round called them false denials. They are denials, and they are correct
under this SPEC's rule. Neither appears anywhere in the 57-row harvest, so
neither is observed use. The round's own example, `find ... -print0 | xargs -0`,
is denied a second time at `xargs`, which is not in the grammar and is not
proposed for it, so admitting `-print0` would not make that pipeline work. The
grammar covers what the reviewer was measured doing; widening it for a plausible
command nobody ran is how an allowlist decays into a list of things somebody
thought of. Recorded as rejected rather than silently left.

**One observation, checked and closed.** The round noted that
`tools/audit_sweep.py` resolved a handler by stem, so a frontmatter naming
`adversary-bash-grammar.sh` when only `.py` exists would credit the lift for a
file the runtime cannot run. It labelled this an observation rather than a
finding, and it was right that another layer catches it:
`tools/hooks_registered.py` resolves by full basename and goes red. But the
mismatch was introduced by this object's own suffix probing, so it is closed
here rather than left to two modules disagreeing about one string. `handler_path`
now honours an explicit suffix and probes only when the command names none, with
a control for the mismatch case.

Counts after the round: `bash-grammar-controls` 118, `audit-sweep-controls` 24.

**Approved 2026-09-12.** All four rulings answered: 1 allow, 2 deny with no
carve-out, 3 approved, 4 agreed. The grammar in this file is unchanged by them,
because each ruling confirmed what the SPEC proposed. Decide 2 gained the
per-call table above, which was produced to answer the ruling and is kept as the
record of what the bound costs.
