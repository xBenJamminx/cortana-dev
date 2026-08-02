# OpenClaw to Hermes Agent migration

Cortana's runtime is **Hermes Agent**. The repository no longer hardcodes
OpenClaw paths in executable code: every runtime path resolves through
`lib/paths.py`, secrets through `lib/env.py`, and gateway control through
`lib/gateway.py`.

## How paths resolve now

Everything derives from the checkout rather than an absolute path, so the same
code is correct whether the workspace lives at `/root/.openclaw/workspace`,
`/root/clawd`, or anywhere else. Agent-home lookups check Hermes first and fall
back to the legacy homes only for state that has not been moved yet.

| Concern | Resolver | Default |
|---|---|---|
| Workspace root | `lib.paths.WORKSPACE` | the checkout |
| Logs | `lib.paths.log_file(name)` | `<workspace>/logs` |
| Workspace memory files | `lib.paths.memory_file(name)` | `<workspace>/memory` |
| Agent memory sqlite | `lib.paths.memory_db()` | `~/.hermes/memory/main.sqlite` |
| Any agent-home file | `lib.paths.agent_file(name)` | `~/.hermes/<name>` |
| Secrets | `lib.env.load_env()` / `env_path()` | `~/.hermes/.env` |
| Gateway control | `lib.gateway.is_active()` / `.restart()` | `hermes gateway`, systemd fallback |
| Gateway unit name | `lib.paths.gateway_service()` | `hermes-gateway` |

### Environment variables

None are required — the defaults are correct for a normal checkout. Prefer the
generic `AGENT_*` names; the `CORTANA_*` names are honoured for backward
compatibility and lose to `AGENT_*` when both are set.

| Variable | Legacy alias | Effect |
|---|---|---|
| `AGENT_WORKSPACE` | `CORTANA_WORKSPACE` | workspace root |
| `AGENT_LOGS` | `CORTANA_LOGS` | log directory |
| `AGENT_MEMORY_DB` | `CORTANA_MEMORY_DB` | agent memory sqlite |
| `AGENT_GATEWAY_SERVICE` | `CORTANA_GATEWAY_SERVICE` | gateway systemd unit name |
| `HERMES_HOME` | — | Hermes home (default `~/.hermes`) |

## Porting to another Hermes agent (Scout, MiMoo, ...)

`lib/paths.py`, `lib/env.py`, and `lib/gateway.py` contain nothing
Cortana-specific. They discover the workspace from their own file location, so
they work in any agent's checkout with **zero configuration**.

### Automated

For a sibling agent on the same host, `scripts/port-hermes-resolvers.py` does
the mechanical work. Dry run is the default; nothing is written without
`--apply`, and re-running is a no-op.

```bash
# 0. find the sibling agents on this host (skips this repository)
python3 scripts/port-hermes-resolvers.py --discover

# 1. commit the target's current state first -- git is the only undo
git -C /path/to/scout add -A && git -C /path/to/scout commit -m "pre-migration"

# 2. see what would change
python3 scripts/port-hermes-resolvers.py --target /path/to/scout

# 3. apply
python3 scripts/port-hermes-resolvers.py --target /path/to/scout --apply

# 4. verify BEFORE restarting that agent
cd /path/to/scout
python3 -m py_compile $(git ls-files '*.py')
python3 -c "from lib.paths import WORKSPACE, LOGS; print(WORKSPACE, LOGS)"
#   ^ must print the target's checkout, not Cortana's
```

It installs the resolvers, rewrites hardcoded paths, converts shell `source`
lines to the Hermes-first loop, and replaces per-script `_load_env()` copies.
It skips dated memory, reports, published post copy, and legacy-removal
utilities, and prints anything it will not touch under **NEEDS MANUAL REVIEW**
— systemd unit names, crontabs, logrotate, and gateway HTTP endpoints. Work
through that list by hand; the same server-side steps in this document apply to
each agent separately.

### By hand

1. Copy the three modules into the other agent's `lib/` (create `lib/__init__.py`
   if it does not exist).
2. In each script, replace hardcoded paths with the resolvers, using the same
   four-line bootstrap this repository uses:

   ```python
   import os as _os
   import sys as _sys
   _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
   from lib.paths import log_file, memory_db
   ```

   Adjust the number of nested `dirname()` calls to the file's depth below the
   checkout root — one per level, so `scripts/foo.py` needs two.
3. Delete any per-script `_load_env()` copies and import `load_env` from
   `lib.env` instead. Divergent copies of that function are what broke key
   loading here in the first place.
4. Verify before deploying:

   ```bash
   python3 -m py_compile $(git ls-files '*.py')
   python3 -c "from lib.paths import WORKSPACE, LOGS; print(WORKSPACE, LOGS)"
   ```

   `WORKSPACE` must print that agent's checkout, not Cortana's.

Only set `AGENT_WORKSPACE` if the gateway runs the agent from a directory other
than the checkout.

Workspace OS has its own copy of this logic in `workspace-os/backend/paths.py`,
because it ships as a separate container image and cannot import from the
checkout. It also reads `CORTANA_GATEWAY_URL`, `CORTANA_GATEWAY_TOKEN`, and
`CORTANA_BROWSER_URL`, each falling back to its old `CLAWDBOT_*` name.

## Concept mapping

| Legacy concept | Hermes Agent equivalent |
|---|---|
| `~/.openclaw/openclaw.json` / `~/.clawdbot/clawdbot.json` | `~/.hermes/config.yaml` |
| `/root/.openclaw/workspace` / `/root/clawd` | the checkout, or `$CORTANA_WORKSPACE` |
| `spawn_task.sh`, `sessions_spawn` | `delegate_task` for isolated reasoning work |
| ad-hoc detached agent sessions | `terminal(background=true, notify_on_complete=true)` |
| system `crontab` invoking an agent wrapper | Hermes `cronjob` or `hermes cron` |
| `openclaw-gateway.service` | `hermes gateway setup\|start\|stop\|status` |
| OpenClaw channel configuration | `gateway` section of `~/.hermes/config.yaml` |

Delegation is not durable: session shutdown can cancel child agents. Use Hermes
cron for scheduled or durable agent runs.

## Server-side steps (not done by this repository)

The code no longer cares which layout exists, but these still need doing on the
host to finish the move:

1. **Confirm which secrets file is live.**
   `ls -la ~/.hermes/.env ~/.openclaw/.env`
   If both exist, consolidate into `~/.hermes/.env` — the loaders pick the
   first that exists and do **not** merge them.
2. **Move agent state** (memory database, `google_credentials.json`, media
   directories) from `~/.openclaw` or `~/.clawdbot` into `~/.hermes`, or set
   `CORTANA_MEMORY_DB` to keep it where it is.
3. **Set `CORTANA_WORKSPACE`** in the gateway environment if the checkout is
   not the working directory.
4. **Reinstall log rotation.** `config/logrotate-cortana.conf` replaces
   `logrotate-clawd.conf`; the workspace path inside it must be edited by hand,
   because logrotate expands neither `~` nor environment variables.
5. **Re-run `scripts/setup-cron.sh`** so crontab entries point at the checkout.
   It removes both the new marker and legacy `clawd` entries first.
6. **Confirm the gateway unit name.** `lib/gateway.py` prefers the `hermes` CLI
   and only falls back to systemd; if the unit is not `hermes-gateway`, set
   `CORTANA_GATEWAY_SERVICE`.

## Known gaps

- **Workspace OS gateway routes** (`workspace-os/backend/routers/ai.py`,
  `browser.py`) call the legacy gateway HTTP API (`/api/models`,
  `/api/ai/image`) on port 18789. The URLs are now configurable, but the
  endpoints themselves are unverified against Hermes.
- **Workspace OS config reads.** `paths.agent_config()` reads
  `~/.hermes/config.yaml` when present, but the Hermes schema differs from the
  old `clawdbot.json`, so lookups such as `agents.defaults.models` and
  `skills.entries` return empty until they are mapped. Callers keep their
  `.get(..., {})` defaults, so this degrades rather than crashes.
- **Watchdog process matching.** `scripts/watchdog.py` and
  `process-watchdog.py` still hunt for processes named `claude`. If Hermes runs
  a differently named provider process, that match needs updating.

## Intentionally retained OpenClaw references

Not stale, not to be bulk-renamed:

- `memory/`, dated root notes, `learnings_patch.md`, `ERROR_LOG.md` — historical
  records and legacy incident signatures
- `reports/`, `social_posts/`, `memory/content-drafts/`, and the drafted or
  published X posts in `scripts/scheduled-*-post.*` — published copy whose
  wording must stay faithful
- `skills/x-research/data/` — cached source material and an explicit OpenClaw
  watch target
- `scripts/cleanup-user-systemd.sh`, `scripts/sync-cli-sessions.sh` — utilities
  whose whole job is removing or reading OpenClaw state; they need the old names
- `scripts/morning-scan.sh` — a retired wrapper kept as a tombstone
- the `clawdbot` key in skill `metadata:` front matter — a loader schema key,
  not a path
- `topic-aggregator.py`'s `"openclaw"` keyword — a monitoring search term
- `openclaw` as an SSH host alias in `TOOLS.md` — a real host alias
- `<!-- openclaw:* -->` markers in `SOUL.md` — consumed by tooling
- root OAuth one-offs (`exchange_oauth_code.py`, `google_oauth_flow.py`,
  `generate_oauth_url.py`, and the `test_*google*.py` scripts) — archival
  bootstrap records; live code reads credentials via `agent_file()`

## Rules for new changes

1. Never hardcode `/root/clawd`, `~/.openclaw`, `~/.clawdbot`, `spawn_task.sh`,
   `sessions_spawn`, or `openclaw-gateway`. Use the resolvers.
2. Keep secrets in `~/.hermes/.env` or an integration's secure store, never in
   git. Saving a key is a secrets-file edit, not a commit — see
   `context/auth.md`.
3. Confirm current commands and configuration against
   <https://hermes-agent.nousresearch.com/docs>.
4. Do not rename historical quotes, incident details, social copy, or archival
   data.
