"""Canonical env loading for Cortana scripts.

AGENTS.md and TOOLS.md both point here for the `_load_env()` pattern.

Secrets live outside this repository. We check the Hermes location first and
fall back to the legacy openclaw location so scripts keep working on boxes
that have not finished the migration.

Usage:
    from lib.env import load_env

    load_env()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
"""
import os

ENV_PATHS = (
    "~/.hermes/.env",
    "~/.openclaw/.env",
)


def env_path() -> str:
    """Return the first secrets file that exists, or "" if none do."""
    for candidate in ENV_PATHS:
        expanded = os.path.expanduser(candidate)
        if os.path.exists(expanded):
            return expanded
    return ""


def load_env() -> str:
    """Load the secrets file into os.environ without clobbering existing vars.

    Returns the path that was loaded, or "" if no secrets file was found.
    """
    path = env_path()
    if not path:
        return ""
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            if key and not os.environ.get(key):
                os.environ[key] = val
    return path


# Alias matching the name used by the inline copies in scripts/.
_load_env = load_env
