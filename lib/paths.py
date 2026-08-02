"""Canonical runtime path resolution for a Hermes agent workspace.

Single source of truth. Nothing outside this module should hardcode
`/root/clawd`, `/root/.openclaw`, or `/root/.clawdbot`.

Design: derive everything from the checkout rather than from an absolute
path. The checkout is the workspace (README.md), so a script resolves the
same correct paths whether it runs from `/root/.openclaw/workspace`,
`/root/clawd`, or anywhere else. That makes this behavior-preserving on an
unmigrated box and correct on a migrated one, with no flag day.

PORTABLE ACROSS AGENTS: nothing here is Cortana-specific. Copy this module,
`env.py`, and `gateway.py` into any sibling agent's workspace (Scout, MiMoo,
...) and they work unmodified, because the workspace is discovered from the
file's own location. No environment variables are required.

Override with environment variables when the layout differs. The generic
`AGENT_*` names work in every agent's workspace; the `CORTANA_*` names are
honoured for backward compatibility with this deployment.

    AGENT_WORKSPACE / CORTANA_WORKSPACE     workspace root (default: this checkout)
    AGENT_LOGS / CORTANA_LOGS               log directory  (default: <workspace>/logs)
    AGENT_MEMORY_DB / CORTANA_MEMORY_DB     agent memory sqlite
    AGENT_GATEWAY_SERVICE /
        CORTANA_GATEWAY_SERVICE             gateway systemd unit name
    HERMES_HOME                             Hermes home (default: ~/.hermes)

Usage:
    from lib.paths import WORKSPACE, LOGS, MEMORY, memory_db, log_file

    LOG_FILE = log_file("competitor-monitor.log")
"""
import os
from pathlib import Path


def _env(*names: str) -> str | None:
    """First environment variable that is set and non-empty."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


# ---------------------------------------------------------------- workspace

def _default_workspace() -> Path:
    # lib/paths.py -> lib -> checkout root
    return Path(__file__).resolve().parent.parent


WORKSPACE = Path(_env("AGENT_WORKSPACE", "CORTANA_WORKSPACE") or _default_workspace())
LOGS = Path(_env("AGENT_LOGS", "CORTANA_LOGS") or WORKSPACE / "logs")
MEMORY = WORKSPACE / "memory"
SCRIPTS = WORKSPACE / "scripts"
ERROR_LOG = WORKSPACE / "ERROR_LOG.md"

# ------------------------------------------------------------------- hermes

HERMES_HOME = Path(_env("HERMES_HOME") or os.path.expanduser("~/.hermes"))
HERMES_CONFIG = HERMES_HOME / "config.yaml"
GATEWAY_LOG = HERMES_HOME / "logs" / "gateway.log"

# Legacy agent homes, newest first. Only used to locate pre-existing state
# that has not been moved yet.
_LEGACY_HOMES = (
    "~/.openclaw",
    "~/.clawdbot",
)

# --------------------------------------------------------------------- api

def log_file(name: str) -> Path:
    """Path to a log file, ensuring the log directory exists."""
    LOGS.mkdir(parents=True, exist_ok=True)
    return LOGS / name


def memory_file(name: str) -> Path:
    """Path to a file under the workspace memory directory."""
    MEMORY.mkdir(parents=True, exist_ok=True)
    return MEMORY / name


def agent_file(name: str) -> str:
    """Locate a file inside the agent home.

    Returns the first path that already exists, checking Hermes before the
    legacy homes. If none exist, returns the Hermes path so anything newly
    created lands in the right place.
    """
    hermes = HERMES_HOME / name
    candidates = [hermes] + [
        Path(os.path.expanduser(h)) / name for h in _LEGACY_HOMES
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(hermes)


def memory_db() -> str:
    """Locate the agent memory sqlite database. AGENT_MEMORY_DB overrides."""
    return _env("AGENT_MEMORY_DB", "CORTANA_MEMORY_DB") or agent_file("memory/main.sqlite")


def gateway_service() -> str:
    """Systemd unit name for the messaging gateway.

    Prefer the `hermes gateway` CLI for control (see lib/gateway.py). This is
    only for direct systemd interaction, and is overridable because the unit
    name differs between deployments.
    """
    return _env("AGENT_GATEWAY_SERVICE", "CORTANA_GATEWAY_SERVICE") or "hermes-gateway"
