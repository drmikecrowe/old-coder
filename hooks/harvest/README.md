# hooks/harvest/

Step zero for track A2 object H3: what `old-coder-adversary` actually ran,
harvested from recorded sessions rather than recalled.

House rule: no em dashes.

## Why this directory exists

`adversary-bash-grammar.py` is an allowlist. An allowlist is only as good as the
evidence of what it must admit, and the failure it produces when that evidence
is missing is not a leak but a refusal: the hook denies a legitimate read
mid-review, and you find out in production. So the grammar cites this file, and
the file is here rather than quoted in a document, because a number nobody can
re-derive is a number that drifts.

It also records a disagreement. `docs/track-a2.md` sketched H3 as a git-only
grammar. Measured against this harvest, git-only with plain arguments admits
8 of 57. The SPEC at `docs/spec-a2-h3.md` argues the wider grammar from these
rows, and the argument is checkable because the rows are here.

## The files

| File | What it is |
|---|---|
| `harvest.py` | the harvester. Walks a Claude Code projects root, selects subagent transcripts whose `.meta.json` names `old-coder-adversary`, emits every `Bash` call |
| `redact.py` | rewrites home paths for publication |
| `harvest.jsonl` | the result, 57 rows from 8 sessions, redacted |

## Reproducing it

```sh
python3 hooks/harvest/harvest.py ~/.claude/projects /tmp/raw.jsonl
python3 hooks/harvest/redact.py /tmp/raw.jsonl hooks/harvest/harvest.jsonl "$HOME"
```

Your own transcripts will not match these rows. That is the point of the
harvester being committed rather than only its output: a reader adopting this
tier on another host can measure their own reviewer and find out whether this
grammar fits it, instead of trusting one author's eight sessions.

`harvest.py` exits 1 on an empty harvest. A grammar written against no evidence
is exactly what step zero exists to prevent, so finding nothing is a failure
rather than a clean run.

## The one redaction, declared

The command strings are verbatim apart from a single substitution:
`/home/<user>` becomes `/redacted`. 33 of the 57 rows carried such a path.

The placeholder deliberately carries no `$`. The grammar denies any word
containing `$`, so a `$HOME`-shaped placeholder would flip rewritten rows from
allowed to denied and quietly destroy the positive control these rows are used
as. Verified both ways: the redacted file and the raw file produce the same 44
allowed and 13 denied.

Nothing else is altered. Two rows contain backticks and several contain `$`
expansions that the grammar denies; they are kept as they were run, because a
harvest edited to make the grammar look better is not evidence.

## What the rows say

57 calls across 8 sessions. Leading command: 19 `git`, 8 `python3`, 6 `cd`,
5 `rg`, 4 `echo`, 4 `set -u`, 3 `ls`, 2 `sed -n`, 2 `find`, 2 `cat`, 1 `tail`,
1 `head`. Reached later in a command, never first: `printf`, `chmod`, `cp`,
`rm -rf`, `mkdir -p`, `env -u`, `sh`, `rtk proxy`.

Shell features, per command and overlapping: 28 pipes, 22 `;` chains, 16 stderr
redirects, 11 multiline, 8 `&&`, 6 leading `cd`, 5 `||`, 4 `$VAR`, 2 backticks,
1 `>` redirect.

The uncomfortable row is the H2 round's sandbox: `rm -rf` and `mkdir -p` under a
scratch directory, then `env -u ... python3` and `sh`, to reproduce an attack on
the hook it was grading. The finding was upheld and hardened the tier. This
grammar denies that command, and the SPEC says so rather than leaving it to be
discovered.
