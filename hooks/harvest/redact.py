#!/usr/bin/env python3
"""Rewrite the harvest's home paths before it is committed.

The harvest is a quoted transcript: the command strings are verbatim apart from
the home path, which becomes `/redacted`. Two spellings, because Claude Code
also names a project by slugifying its path: `/home/<user>` and the slug form
`-home-<user>` both go, or the second leaks the first back through a transcript
path that happens to appear inside a command.

The placeholder carries no `$` on purpose. The grammar denies any word
containing `$`, so a `$HOME`-shaped placeholder would turn every rewritten
command into a denial and silently destroy the positive control this file
exists to be.

Usage: redact.py <source.jsonl> <destination.jsonl> <home-prefix>
"""

import json
import sys


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    source, destination, home = argv[1], argv[2], argv[3]
    home = home.rstrip("/")
    slug = home.replace("/", "-")
    rows = [json.loads(line) for line in open(source, encoding="utf-8") if line.strip()]
    rewritten = 0
    with open(destination, "w", encoding="utf-8") as out:
        for row in rows:
            command = row["command"]
            if home in command or slug in command:
                rewritten += 1
                command = command.replace(home, "/redacted").replace(slug, "-redacted")
            out.write(
                json.dumps(
                    {"session": row["session"], "desc": row["desc"], "command": command}
                )
                + "\n"
            )
    print(f"{len(rows)} rows, {rewritten} carried a home path and were rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
