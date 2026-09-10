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

**Registration, and it is two steps, not one.** The repository is the source of
truth: the handler lives at `hooks/spec-intent-scope.sh` and is edited there.
The frontmatter in `skills/old-coder/agents/old-coder-spec-intent.md` points at
`${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/spec-intent-scope.sh`, which is the
same place the agents themselves are installed, so the handler is linked there
beside them:

```sh
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks"
ln -s "$PWD/hooks/spec-intent-scope.sh" \
  "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/spec-intent-scope.sh"
```

The address follows the agent, not the project. `old-coder` reviews other
people's repositories, so a project-relative address would resolve only when it
runs against this one. That is why the install is a real step rather than a
side effect of cloning, and why `tools/hooks_registered.py` prints the exact
`ln` command when the step has not been done.

`CLAUDE_PROJECT_DIR` is deliberate and it is not interchangeable. The hooks
reference guarantees three placeholders in a hook command:
`CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA`. Anything
else rests on what the host exports and on a hand-installed file somewhere
outside the checkout. Two things can then be wrong at once, the variable and
the install, and neither announces itself: an unresolved hook path does not
error, it does nothing, and the tool call proceeds.

**The consequence, stated rather than discovered.** `CLAUDE_PROJECT_DIR` is the
project being worked on. The bound therefore holds when the spec reviewer runs
inside a checkout that has this `hooks/` directory, and not otherwise. Running
`old-coder` against some other repository leaves the reviewer unbounded, and
nothing announces that. To carry the bound into another project, copy `hooks/`
into it and copy the `hooks:` block into your own agent file. That is the tier
being opt-in, and it is the cost of not installing anything globally.

#### Not `settings.json`

A hook in `settings.json` is session-wide: it fires for every agent's tool
calls, including the main session. The documented `PreToolUse` input fields
carry nothing identifying which subagent is calling, so a settings-based hook
could not tell the spec reviewer apart from anyone else and would bound every
`Read` in the session. Scoping a bound to one subagent is what frontmatter
hooks are for, and the cost is that they do not appear in `/hooks`.

**The unresolved piece.** The handler denies every `Read` unless
`OLD_CODER_SPEC_DIR` names the task's artifact directory, and nothing in the
skill sets it when it spawns the reviewer. Today that is the operator's job,
set in the environment of the `claude` process before the session starts. Until
something owns it, this bound is not wired into the workflow that creates the
dated artifact directory, and a run that forgets it will fail the allow half.

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
