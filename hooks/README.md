# hooks/

Host-specific bounds for Claude Code. Opt-in for a portable reader, on by
default in this fork's own deployment. `CONTRIBUTING.md` states the tier and
its test; `docs/track-a2.md` is the plan that builds it.

House rule: no em dashes.

## What a hook is for here

The skill text is prose, and prose persuades an agent rather than bounding one.
`skills/old-coder/references/ceiling.md` is the published list of places where
that gap is real. A hook closes one of those places on one host. It is not a
better way to write the instruction; it is the point where the instruction
stops and enforcement starts, and the two are never blended.

So the tier's test has three clauses and all are required:

1. **A hook here is a bound.** It refuses something. A hook that injects,
   rewrites or logs is out of scope for this directory, because clause 2 is a
   proof of denial and a hook that never denies satisfies it by having nothing
   to prove.
2. **A hook ships with a control that proves it denies.** A hook without one is
   a bound that reports success while measuring nothing.
3. **The skill text never claims what only a hook enforces.** A reader on
   another host must be able to tell, from the text alone, which sentences are
   bounds for them and which are instructions.

## The two halves of every control, and why they are never merged

| Half | Proves | Where it runs |
|---|---|---|
| unit | the handler decides correctly for the inputs it is given | anywhere, including CI |
| registration | the hook file parses and some frontmatter references it | anywhere, including CI |
| host probe | Claude Code actually calls the handler, and the call is denied | only on the host, with a human watching |

The first two are cheap and run in the gauntlet. **Neither is the proof.** A
handler can be perfect and unregistered. A registration can be correct and the
runtime can decline to honour it. Only the host probe closes that, and it
cannot be automated here, because the thing under test is the agent runtime
itself.

State both halves inside every control, so nobody reads the CI half as the
proof. `hooks/test_spec_intent_scope.sh` says so in its own header.

## What a hook cannot do

**It cannot fail closed on its own absence.** If the handler is missing, not
executable, or its path does not resolve, Claude Code logs the failure and
carries on with the normal permission flow. That is the same as no hook at
all. Nothing inside the handler can change this, because the handler did not
run.

`tools/hooks_registered.py` is the mitigation, not the fix: it fails the
gauntlet when a frontmatter names a handler that is missing from `hooks/`, is
not a file, or is not executable. It grades the repository's copy rather than
your deployment, because the tier is opt-in and a check that reddens for a
reader's choice is a check people learn to ignore. So it catches the deletion,
and it does not catch a host that silently stops honouring frontmatter hooks,
nor one that never opted in. Rerun the host probes on every hook change, and
rebind them, for exactly that reason.

## The hooks

### `spec-intent-scope.sh`

Bounds `old-coder-spec-intent`'s `Read` to the directory its SPEC lives in.
This is the mechanism that would move EX-1, and it has not moved it: the row
reads `accepted` in `docs/loop-alignment.md` and stays there until the probes
below are recorded. The reviewer's brief says "do not go looking for the
codebase", and until a probe exists that is still an instruction.

Deny by default, allow by resolved path. Every path component is resolved
before the prefix test, the final one included, because a symlink inside the
spec directory pointing at a source file would otherwise pass while reading
exactly the file the bound exists to hide.

**Scope comes from `OLD_CODER_SPEC_DIR`.** The artifact directory is per-task
and dated, so no path can be baked in. Unset, empty, or not a directory denies
everything, including files that would otherwise be allowed. Set it to the
task's artifact directory before spawning the reviewer.

Decision contract, from the Claude Code hooks reference:

| Outcome | How | Effect |
|---|---|---|
| deny | `hookSpecificOutput` JSON, exit 0 | the Read is prevented; the reason is shown to the reviewer |
| no decision | no output, exit 0 | the normal permission flow continues |
| fail closed | exit 2 | a blocking error; stderr becomes the reason |

Exit 2 is used for every unexpected path: no `jq`, no `readlink -f`,
unreadable stdin, an empty payload, a payload that is not a JSON object. An
ordinary nonzero exit would be a non-blocking error and the call would proceed,
so nothing here is allowed to exit nonzero by accident.

**Registration.** In this fork the shipped agent file and the deployed agent
file are one file, reached by symlink, so the frontmatter in
`skills/old-coder/agents/old-coder-spec-intent.md` is live. It points at
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/spec-intent-scope.sh`. Deliberately
not `${CLAUDE_PROJECT_DIR}`: that is the project being reviewed, not this
checkout, so on every run except old-coder-on-old-coder the path would not
exist and the hook would not run at all.

To take it on another host:

```sh
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks"
ln -s "$PWD/hooks/spec-intent-scope.sh" \
  "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/spec-intent-scope.sh"
```

Then copy the `hooks:` block from this fork's agent frontmatter into yours.

#### Running the controls

```sh
sh hooks/test_spec_intent_scope.sh     # unit half, twelve cases
python3 tools/hooks_registered.py      # registration half
sh tools/test_hooks_registered.sh      # controls for the registration half
```

#### The host probes

Run both on every change to `spec-intent-scope.sh`, and record the output
verbatim with the date and the tree hash. Neither can be replaced by the
commands above.

**Negative control.** Set the scope, spawn the reviewer, ask it to read a
source file. Expect a refusal quoting the denial reason.

**Positive control.** Same scope, ask it to read the SPEC inside that
directory. Expect it to succeed and quote the file. Without this half the hook
is only proven to refuse, and a handler that denies everything also passes the
negative control.

Recorded probes live in `hooks/probes/`, one file per hook version, each
naming the tree hash it was run against.
