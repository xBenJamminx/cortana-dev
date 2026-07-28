# OpenClaw to Hermes Agent migration

Cortana's active runtime is **Hermes Agent**. OpenClaw is retained where required for historical accuracy or compatibility, and in legacy code that has not yet been safely migrated and deployment-tested.

## Current equivalents

| Legacy concept | Current Hermes Agent equivalent |
|---|---|
| `~/.openclaw/openclaw.json` / `~/.clawdbot/clawdbot.json` | `~/.hermes/config.yaml` |
| `/root/.openclaw/workspace` / `/root/clawd` | this repository checkout, optionally exposed as `$CORTANA_WORKSPACE` |
| `spawn_task.sh`, `sessions_spawn` | `delegate_task` for isolated reasoning work |
| ad-hoc detached/background agent sessions | `terminal(background=true, notify_on_complete=true)` for bounded shell work |
| system `crontab` invoking an agent wrapper | Hermes `cronjob` or `hermes cron` |
| `openclaw-gateway.service` | `hermes gateway setup|start|stop|status` |
| OpenClaw channel configuration | Hermes messaging gateway under `gateway` in `~/.hermes/config.yaml` |

Delegation is not durable: session/process shutdown can cancel child agents. Use Hermes cron for scheduled or durable agent runs.

## Intentionally retained OpenClaw references

The following are records or compatibility artifacts, not current instructions. Some legacy scripts still contain OpenClaw paths because they have not been deployment-tested on Hermes; they are not Hermes-ready merely because this documentation changed.

- `memory/`, dated root notes, and `learnings_patch.md`: historical events and migration records
- `ERROR_LOG.md`: historical OpenClaw incident signatures and remediations; consult only when maintaining a legacy instance
- `reports/`, `social_posts/`, `memory/content-drafts/`, and `skills/x-research/data/cache/`: previously published/drafted/cached source material whose wording must remain faithful
- `skills/x-research/data/watchlist.json`: an explicit watch target for the OpenClaw project
- legacy maintenance scripts such as `sync-cli-sessions.sh` and `cleanup-user-systemd.sh`: OpenClaw-only compatibility/removal utilities
- other scripts that still contain OpenClaw paths: unmigrated legacy code; review and test each one before use rather than bulk-renaming production paths
- sacred production workflow scripts (`meeting-wrap-v1.py`, `morning-scan-v2.py`, `fam-sync-analyze.py`, `fam-sync-write.py`): intentionally not edited during repository modernization; migrate only in a separately approved, deployment-tested change
- filenames and product labels such as `clawdbot_router.png` or old database/table names: archival identifiers

## Rules for new changes

1. Do not introduce new `.openclaw`, `.clawdbot`, `/root/clawd`, `spawn_task.sh`, `sessions_spawn`, or `openclaw-gateway` dependencies.
2. Resolve repository paths relative to the checkout or `$CORTANA_WORKSPACE`.
3. Keep secrets in `~/.hermes/.env` or an integration's secure store, never in git.
4. Confirm current commands and configuration against <https://hermes-agent.nousresearch.com/docs>.
5. Do not blindly rename historical quotes, incident details, social content, or archival data.
