#!/usr/bin/env python3
"""
Run a Cortana script by name, wherever this environment happens to keep it.

Cron prompts and skills should call scripts through this wrapper instead of
hardcoding /root/cortana/scripts/..., which only exists on the production box.
When the script genuinely is not reachable, this prints every location tried and
why each one failed, instead of a bare [Errno 13] Permission denied.

Usage:
    python3 scripts/cortana-run.py hungryroot_api.py --help
    python3 scripts/cortana-run.py --which hungryroot_api.py

Exit codes:
    127  script could not be resolved (diagnosis on stderr)
    else the wrapped script's own exit code
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.paths import ScriptNotFound, resolve_script  # noqa: E402


def main(argv):
    args = list(argv)
    which_only = False

    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    if args[0] == "--which":
        which_only = True
        args = args[1:]
        if not args:
            print("--which needs a script name", file=sys.stderr)
            return 2

    name, script_args = args[0], args[1:]

    try:
        path = resolve_script(name)
    except ScriptNotFound as e:
        print(e, file=sys.stderr)
        return 127

    if which_only:
        print(path)
        return 0

    os.execv(sys.executable, [sys.executable, str(path), *script_args])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
