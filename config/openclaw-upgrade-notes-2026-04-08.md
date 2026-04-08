# OpenClaw Upgrade Notes - 2026-04-08

Applied safe config upgrades for Cortana-OS.

## Applied

- Enabled `plugins.slots.memory = "memory-core"`
- Enabled `plugins.entries.memory-core` with dreaming:
  - `enabled: true`
  - `frequency: "0 3 * * *"`
- Enabled `plugins.entries.memory-wiki` in `bridge` mode
- Configured wiki vault at `~/.openclaw/wiki/main`
- Enabled dashboards/backlinks and shared search corpus `all`
- Left `includeCompiledDigestPrompt` off to avoid prompt bloat

## Not Applied Automatically

- `openclaw update` to 2026.4.8, because that may restart the live gateway
- Telegram security tightening (`groupPolicy`, `dmPolicy`), because it may change who can reach Cortana and should be confirmed first
- Secret migration out of `openclaw.json`

## Recommended Next Commands

```bash
openclaw update --yes
openclaw doctor
openclaw wiki status
openclaw memory status --deep
```

## Security Follow-up

Current live config still exposes risky defaults:
- `channels.telegram.groupPolicy = open`
- `channels.telegram.dmPolicy = open`
- secrets embedded directly in `openclaw.json`

These should be cleaned up next.
