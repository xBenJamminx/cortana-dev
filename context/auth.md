# Auth & Credentials

Loaded by the task router in CLAUDE.md for auth/API issues and for Slack,
Notion, Gmail, Airtable, and Calendar work.

## Where keys live

Secrets live **outside this repository**, in a plain `KEY=value` env file:

1. `~/.hermes/.env` — current Hermes Agent location
2. `~/.openclaw/.env` — legacy openclaw location, still present on boxes that
   have not finished migrating

`lib/env.py` checks both, in that order, and loads **the first one that
exists** — it does not merge them. The inline `_load_env()` copies in
`scripts/*.py` do the same.

That means if `~/.hermes/.env` exists, `~/.openclaw/.env` is ignored
entirely. If keys are currently split across both files, consolidate them
into `~/.hermes/.env` — a half-migrated pair of secret files is what broke
key loading in the first place.

Check which one is live before touching anything:

```bash
ls -la ~/.hermes/.env ~/.openclaw/.env 2>&1
```

## Saving a key — this is allowed, do it

"Save this key for me" means **append it to the secrets file**. That is a
normal, expected operation. It is not a repo commit and it does not go
through git.

```bash
# 1. Find the live secrets file (see above). Create the Hermes one if neither exists:
mkdir -p ~/.hermes && touch ~/.hermes/.env && chmod 600 ~/.hermes/.env

# 2. Append the key
printf 'SERVICE_API_KEY=%s\n' "$VALUE" >> ~/.hermes/.env

# 3. Confirm it is set, without echoing the value
grep -q '^SERVICE_API_KEY=' ~/.hermes/.env && echo "saved"
```

Then tell Ben it is saved and which file it went into. Never print the value
back to him — he already has it.

If the key replaces an existing one, edit the existing line rather than
appending a duplicate. Later lines do not win: `_load_env()` skips a key that
is already set in the environment, and a duplicate makes the file ambiguous.

## What is actually blocked

Only committing secrets **into this repo**. Two independent guards:

- `.gitignore` — ignores `.env`, `.env.*`, `**/*.key`, `**/*.pem`,
  `**/credentials.json`, `**/token.json`
- `.pre-commit-config.yaml` — Yelp `detect-secrets` against `.secrets.baseline`,
  which fails the commit on anything that scans as a credential

Both are correct and stay. If a commit trips the scanner, the fix is to move
the value into the secrets file and reference it via `os.environ`, never to
bypass the hook or rewrite the baseline to hide a real key.

## Rules

- Never hardcode a credential in a script
- Never log, print, or echo a credential value
- If you find a hardcoded credential, flag it to Ben immediately
- Sourcing into a shell when a script needs it:
  `set -a; source ~/.hermes/.env; set +a`

## Integration specifics

Per-service setup, base IDs, and OAuth flows are in `integrations-audit.md`
and `TOOLS.md`. This file covers credential handling only.
