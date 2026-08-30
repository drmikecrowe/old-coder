#!/bin/sh
# Stable entry point for evidence.md; the Python implementation avoids shell
# pipelines that can hide an intermediate read failure.
set -eu
# CDPATH= is a deliberate one-command env prefix, so a user's CDPATH cannot
# make `cd` resolve elsewhere and print a different directory. Not a stray
# space -- see https://www.shellcheck.net/wiki/SC1007
# shellcheck disable=SC1007
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/source_state.py"
