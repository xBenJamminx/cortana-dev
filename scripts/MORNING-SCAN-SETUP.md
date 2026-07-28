# Morning Scan — Hermes Agent Setup

## What it does

Every weekday at 9:00 AM Eastern, Cortana:

1. Pulls the last 24 hours from the configured Slack channels.
2. Posts a concise daily briefing to the team updates channel.
3. Notifies Ben through the configured Hermes messaging destination.

The workflow prompt is [`morning-scan-prompt.md`](morning-scan-prompt.md). The protected production implementation is `morning-scan-v2.py`; do not edit or deploy it casually.

## Prerequisites

```bash
hermes gateway setup
hermes gateway status
hermes cron status
```

- Configure provider and messaging settings in `~/.hermes/config.yaml`.
- Set `timezone: America/New_York` in `~/.hermes/config.yaml` so the cron expression follows Eastern time and daylight-saving transitions.
- Keep Composio and integration credentials in `~/.hermes/.env` or their secure credential stores.
- Verify the Slack connected-account and channel IDs in the target environment. Do not copy example IDs blindly.
- Set `terminal.cwd` to the deployed `cortana-dev` checkout.

## Create the schedule

Use the Hermes `cronjob` tool to create a durable agent run. Recommended job definition:

- **Name:** `cortana-morning-scan`
- **Schedule:** `0 9 * * 1-5`
- **Timezone:** inherited from the top-level `timezone: America/New_York` Hermes configuration
- **Prompt:** Read `scripts/morning-scan-prompt.md`, execute it completely, and deliver the result through the destinations configured in that prompt.
- **Working directory:** the deployed `cortana-dev` checkout

Hermes cron accepts cron expressions and natural schedules. Creating this as an agent cron job avoids the old `crontab` plus session-spawn-wrapper architecture and handles daylight saving time when the timezone is configured.

After creation:

```bash
hermes cron list
hermes cron status
```

Trigger the job once with the `cronjob` tool or `hermes cron run <job-id>`, inspect the actual Slack/Telegram delivery, and only then leave the schedule enabled.

## Delegation and long-running work

- The scheduled run itself is durable because it is a Hermes cron job.
- Inside the run, use `delegate_task` only for isolated reasoning-heavy subtasks.
- Use `terminal(background=true, notify_on_complete=true)` for bounded long-running commands.
- Do not use `spawn_task.sh`, `sessions_spawn`, detached shell agents, or OpenClaw session targets.

## Legacy wrapper

`morning-scan.sh` is now a non-executing migration notice. It remains only to fail safely for hosts with stale references. Remove old system `crontab` entries after the Hermes cron job is verified.

Authoritative documentation: <https://hermes-agent.nousresearch.com/docs/user-guide/features/cron>
