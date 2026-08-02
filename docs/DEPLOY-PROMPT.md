# Deploy prompt (run from a machine with server access)

Paste the block below into Claude Code on a machine that can `ssh` to the agent
host. It is self-contained and assumes no prior conversation.

---

You're working on my Cortana agent repo. A finished migration is sitting on a
branch and needs deploying to my server. A sibling agent called Scout needs the
same treatment.

Context:

- Repo `xBenJamminx/cortana-dev`, branch `claude/cortana-key-saving-ie4p92`, not merged.
- My server is reachable as `ssh cortana` (alias in my `~/.ssh/config`).
- Two Hermes agents run on that box: **Cortana** and **Scout**. Scout is **not**
  in git, so it has no undo except the backup the tooling makes.
- The branch finishes an OpenClaw -> Hermes migration that had previously been
  documentation-only, so runtime paths were still resolving to the old layout.

`docs/OPENCLAW-MIGRATION.md` on that branch is the authoritative runbook. Read
it before doing anything.

Steps:

1. Locally: fetch and check out `claude/cortana-key-saving-ie4p92`. Skim
   `docs/OPENCLAW-MIGRATION.md`.

2. On the server, find Cortana's workspace — likely `/root/.openclaw/workspace`
   or `/root/clawd`, but confirm rather than assume. Run `git status` there. If
   it is dirty, commit or stash before touching anything.

3. Put the branch on the server checkout:
   `git fetch origin && git checkout claude/cortana-key-saving-ie4p92`

4. Verify the resolvers work there before going further:

   ```bash
   python3 -c "from lib.paths import WORKSPACE, LOGS; print(WORKSPACE, LOGS)"
   python3 -c "from lib.env import env_path; print(env_path())"
   ```

   `WORKSPACE` must be Cortana's checkout. `env_path()` must print a real
   secrets file. If it prints nothing, stop and work out which `.env` is live.

5. Find Scout: `python3 scripts/port-hermes-resolvers.py --discover`

6. Dry run first, read the output, then apply:

   ```bash
   python3 scripts/port-hermes-resolvers.py --target <scout>
   python3 scripts/port-hermes-resolvers.py --target <scout> --apply
   ```

   Scout has no git, so `--apply` writes a timestamped `.tar.gz` of everything
   it overwrites and prints the `tar -xzf` that reverses it. Keep that path.

7. Verify Scout **before** restarting it:

   ```bash
   cd <scout>
   python3 -m py_compile $(find . -name '*.py' -not -path './.git/*')
   python3 -c "from lib.paths import WORKSPACE; print(WORKSPACE)"
   ```

   That must print Scout's own path, not Cortana's.

8. Do the "Server-side steps" section of the runbook **separately for each
   agent**:
   - `ls -la ~/.hermes/.env ~/.openclaw/.env` — if both exist, consolidate into
     `~/.hermes/.env`. The loader takes the first that exists and does **not**
     merge them.
   - Move agent state (memory sqlite, `google_credentials.json`, media dirs)
     from `~/.openclaw` or `~/.clawdbot` into `~/.hermes`, or set
     `AGENT_MEMORY_DB` to leave it where it is.
   - Install `config/logrotate-cortana.conf` to `/etc/logrotate.d/cortana` and
     **edit the workspace path inside it by hand** — logrotate expands neither
     `~` nor environment variables. Validate with `logrotate -d`.
   - Re-run `scripts/setup-cron.sh`.
   - Confirm the gateway systemd unit name. If it is not `hermes-gateway`, set
     `AGENT_GATEWAY_SERVICE`.

9. Work through everything the porter printed under **NEEDS MANUAL REVIEW**
   (systemd units, crontabs, logrotate, gateway HTTP endpoints). Those were
   deliberately not auto-edited.

10. Only once verification passes, restart the gateways and confirm both agents
    respond.

Known gaps, already documented — don't be surprised by them:

- `workspace-os` gateway routes still call the legacy HTTP API (`/api/models`,
  `/api/ai/image`). URLs are configurable now, endpoints unverified against Hermes.
- Hermes `config.yaml` has a different schema from the old `clawdbot.json`, so
  `workspace-os` config lookups return empty until mapped. Degrades, doesn't crash.
- Both watchdogs still match processes named `claude`. If the provider process
  is named something else now, auto-recovery is silently dead. Check this.

Report back: Scout's path, what changed, what you had to do by hand, and
anything that did not work.
