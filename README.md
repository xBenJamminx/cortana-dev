# Cortana

Cortana is an AI executive assistant running on [Hermes Agent](https://github.com/NousResearch/hermes-agent). It handles research, content intelligence, communication, and operational workflows while keeping Ben in control of external actions.

## What Cortana Does

- **Monitors trends** across X, Reddit, Product Hunt, Hacker News, and YouTube
- **Tracks competitors** and surfaces useful content opportunities
- **Maintains continuity** through repository memory files and Hermes Agent's persistent memory
- **Communicates** through the Hermes messaging gateway (including Telegram) and optional voice integrations
- **Executes tasks** with web, file, terminal, browser, and integration tools
- **Delegates reasoning-heavy work** to isolated child agents with `delegate_task`
- **Runs durable automation** through Hermes `cronjob` jobs

## Current Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                           Cortana                            │
│                       (Hermes Agent)                         │
├──────────────────────────────────────────────────────────────┤
│ Model/provider: selected in ~/.hermes/config.yaml           │
│ Memory: Hermes persistent memory + repository notes         │
│ Tools: terminal, files, web, browser, skills, integrations  │
└──────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
  Messaging gateway      `delegate_task`      Cron scheduler
 (Telegram and more)    isolated subagents    durable agent runs
```

Top-level delegation is asynchronous but process-local. Use:

- `delegate_task` for isolated work that needs reasoning or judgment
- `terminal(background=true, notify_on_complete=true)` for tracked, bounded shell work
- `cronjob` for scheduled or durable work that must survive the current session

## Repository Layout

- `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md` — Cortana's operating context
- `memory/` — project notes, reports, handoffs, and historical records
- `skills/` — repository-owned Hermes-compatible skills
- `scripts/` — automation and integration scripts
- `workspace-os/` — optional Cortana workspace dashboard
- `docs/` — current operational documentation

The repository checkout is the workspace. Scripts should resolve paths from their checkout or a `CORTANA_WORKSPACE` environment variable rather than assuming `/root/clawd` or `/root/.openclaw/workspace`.

## Install and Configure Hermes Agent

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup --portal
hermes gateway setup
hermes gateway status
```

Hermes settings live in `~/.hermes/config.yaml`. Secrets belong in `~/.hermes/.env` or the relevant integration's secure credential store, never in this repository or in `config.yaml`.

Set the messaging gateway's working directory to this checkout through `terminal.cwd` in `~/.hermes/config.yaml`:

```yaml
terminal:
  cwd: /path/to/cortana-dev
```

For provider, gateway, platform, cron, security, and deployment configuration, use the authoritative [Hermes Agent documentation](https://hermes-agent.nousresearch.com/docs).

## Messaging and Automation

```bash
hermes gateway setup
hermes gateway start
hermes gateway status

hermes cron list
hermes cron status
```

Create scheduled agent work with the `cronjob` tool (or the `hermes cron` CLI). Do not install legacy `crontab` entries that invoke OpenClaw session-spawn wrappers. See [`scripts/MORNING-SCAN-SETUP.md`](scripts/MORNING-SCAN-SETUP.md) for the current morning-scan workflow.

## Development

Run the repository checks before committing:

```bash
bash -n scripts/*.sh
npm test --if-present
npm --prefix workspace-os test --if-present
```

For Python changes, run `python3 -m py_compile` on the files you touched. A repository-wide compile currently exposes pre-existing syntax errors in unrelated legacy scripts, so it is not a clean baseline check.

Some scripts require external services and are not safe to execute as generic tests. Never run posting, messaging, or credential-rotation scripts during validation unless explicitly authorized.

## Historical OpenClaw Material

The project migrated from OpenClaw. Historical incident reports, dated memory, cached social data, approved/draft posts about OpenClaw, and explicit migration notes retain the original names and paths so the records remain accurate. They are not current setup instructions. See [`docs/OPENCLAW-MIGRATION.md`](docs/OPENCLAW-MIGRATION.md).

## Related Projects

- [Cortana OS](https://github.com/xBenJamminx/cortana-os) — dashboard frontend
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) — current agent framework

---

*“I handle the ops. You handle the vision.”* — Cortana
