# Cron Script Paths

## The failure

A cronjob whose prompt hardcodes a production-box path dies like this:

```
python3: can't open file '/root/cortana/scripts/hungryroot_api.py': [Errno 13] Permission denied
```

"Permission denied" is misleading here. Python raises `EACCES` in two different
situations:

1. The file exists but the running user cannot read it.
2. Some **parent directory** cannot be searched — `/root` is `drwx------`, so any
   process not running as root gets `EACCES` on `/root/anything`, whether or not
   the file is there.

Case 2 is the common one. Cortana does not only run on the production box: cron
fires can land in ephemeral Claude Code containers that hold a fresh clone of
`cortana-dev` at a different root and no `/root/cortana` tree at all. An absolute
server path is wrong there by construction, and the error text sends you hunting
for a permission bug that does not exist.

## The fix

Call scripts through the resolver instead of by absolute path:

```bash
python3 scripts/cortana-run.py hungryroot_api.py --help   # resolve and run
python3 scripts/cortana-run.py --which hungryroot_api.py  # just print the path
```

It searches, in order: `$CORTANA_HOME`, this repo, `~/cortana`, `/root/cortana`,
`~/clawd`, `/root/clawd` — checking `scripts/` then the root of each. On a miss it
prints every location tried and what was actually wrong with each one:

```
Could not resolve script 'hungryroot_api.py'. Tried:
  /home/user/cortana-dev/scripts/hungryroot_api.py  ->  not found
  /root/cortana/scripts/hungryroot_api.py  ->  unsearchable parent /root (running as uid 1000)
```

Exit code is `127` when unresolved, otherwise the wrapped script's own exit code.
From Python, use `lib.paths.resolve_script(name)`, which raises `ScriptNotFound`
carrying the same report.

## Writing cron prompts

- Never hardcode `/root/cortana/...` or `/root/clawd/...` in a cronjob prompt.
- If a scheduled job needs a script, that script belongs in this repo under
  `scripts/` so every environment gets it from the clone.
- A script that lives only on the production box can only be run by a job that is
  pinned to that box. Say so in the prompt rather than letting the job fail
  midweek and report a phantom permission problem.
