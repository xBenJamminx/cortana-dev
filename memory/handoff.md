# Session Handoff

- **Topic:** Infrastructure / Hermes migration (Cortana + Scout)
- **What we were doing:** Ben reported Cortana refusing to save keys. Root cause
  was the Jul 28 Hermes docs migration (`b8a6c99`) that changed prose only. Fixed
  the key-saving path, then completed the full OpenClaw -> Hermes migration in code.
- **Status:** Done, pushed to `claude/cortana-key-saving-ie4p92`
  (`09b0604`, `b1c3b34`, `355be8f`). No PR opened — Ben has not asked for one.
- **Key context:**
  - Full write-up in `memory/2026-08-02.md`
  - Three resolvers now own all runtime paths: `lib/paths.py` (workspace, logs,
    memory, agent home, gateway unit), `lib/env.py` (secrets, single loader),
    `lib/gateway.py` (hermes CLI, systemd fallback)
  - Paths derive from the checkout, so code is correct on migrated and
    unmigrated boxes alike. No flag day required.
  - `context/auth.md` is the credential playbook. Saving a key = editing the
    secrets file, never a repo commit. Scanner and .gitignore untouched.
  - **Blocked on Ben — server-side, this repo cannot do it:** confirm which env
    file is live (`ls -la ~/.hermes/.env ~/.openclaw/.env`) and consolidate;
    move agent state into `~/.hermes`; edit the workspace path inside
    `config/logrotate-cortana.conf` by hand (logrotate expands no variables);
    re-run `scripts/setup-cron.sh`; confirm the gateway systemd unit name.
    Full runbook in `docs/OPENCLAW-MIGRATION.md`.
  - **Known gaps, documented not fixed:** workspace-os gateway HTTP routes
    unverified against Hermes; Hermes `config.yaml` schema differs from
    `clawdbot.json` so workspace-os config lookups return empty; watchdogs still
    match processes named `claude`.
  - **SCOUT — next action, Cortana's to run.** Scout is a sibling Hermes agent
    on the same host. The resolvers are agent-neutral (they discover the
    workspace from their own file location, zero config), and
    `scripts/port-hermes-resolvers.py` automates the port:

    ```bash
    git -C <scout> add -A && git -C <scout> commit -m "pre-migration"
    python3 scripts/port-hermes-resolvers.py --target <scout>           # dry run
    python3 scripts/port-hermes-resolvers.py --target <scout> --apply
    cd <scout> && python3 -m py_compile $(git ls-files '*.py')
    cd <scout> && python3 -c "from lib.paths import WORKSPACE; print(WORKSPACE)"
    ```

    `WORKSPACE` must print Scout's checkout, not Cortana's. Dry run is the
    default, it is idempotent, and it refuses to target cortana-dev. Whatever it
    lists under NEEDS MANUAL REVIEW (systemd units, crontabs, logrotate, gateway
    HTTP endpoints) is a human job — the server-side steps in
    `docs/OPENCLAW-MIGRATION.md` apply to each agent separately.
  - Ben has not given Scout's workspace path yet; it was never needed here
    because Cortana runs the port on the host.
  - **Still unresolved from earlier:** `BRAIN.md`, `LEARNINGS.md`,
    `memory/index.md` and most `context/*.md` router targets are referenced by
    CLAUDE.md but absent from the repo. Not fabricated.
