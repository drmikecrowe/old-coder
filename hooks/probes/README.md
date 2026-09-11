# Recorded host probes

One file per hook version, named `<hook>-<tree-hash>.md`. Each records the
commands run, the output verbatim, the date, the tree hash, and **the sha256 of
the handler it graded**, on a line reading `handler sha256: <64 hex>`.

The hash is not bookkeeping. `tools/audit_sweep.py` reads it, and a record whose
hash does not match the current handler does not count: the audit row it would
support drops back and the gauntlet goes red. A record naming no hash counts for
nothing at all, because it cannot be matched to any version of the code. Get it
with `sha256sum hooks/<handler>.sh`.

These are the only proof that a hook denies. `hooks-registered` and
`hook-controls` are the CI half; they prove the wiring resolves and the handler
decides correctly, and they say so in their own output. Neither can prove that
Claude Code calls the handler, because the thing under test is the agent
runtime.

Rerun and rebind on every change to the handler. A probe bound to an older
version of the file is a record of a bound that no longer exists.

Each probe file records both directions or it is not a probe:

- the **deny** control, where the reviewer attempts a source read and reports
  that it could not;
- the **allow** control, where the reviewer reads the SPEC in its own directory
  and succeeds.

A handler that denies everything passes the deny control perfectly, which is
why the allow control is not optional.
