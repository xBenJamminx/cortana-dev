"""Runtime path and config resolution for Workspace OS.

Mirrors lib/paths.py in the repository root, but Workspace OS ships as its own
container image and cannot import from the checkout, so the logic lives here.

Environment overrides:
    WORKSPACE_ROOT        workspace root (docker-compose sets /workspace)
    CORTANA_AGENT_HOME    agent home (default: ~/.hermes, legacy fallback)
    CORTANA_GATEWAY_URL   messaging gateway base URL
    CORTANA_GATEWAY_TOKEN gateway auth token
    CORTANA_BROWSER_URL   browser-control base URL
"""
import json
import os
from pathlib import Path

_LEGACY_HOMES = ("~/.openclaw", "~/.clawdbot")


def workspace_root() -> str:
    """Workspace root. Falls back to the repo checkout containing this file."""
    env = os.getenv("WORKSPACE_ROOT")
    if env:
        return env
    # backend/paths.py -> backend -> workspace-os -> checkout
    return str(Path(__file__).resolve().parent.parent.parent)


def agent_dir() -> str:
    """Agent home directory: Hermes first, legacy homes as fallback."""
    env = os.getenv("CORTANA_AGENT_HOME")
    if env:
        return env
    hermes = Path(os.path.expanduser(os.getenv("HERMES_HOME") or "~/.hermes"))
    if hermes.exists():
        return str(hermes)
    for legacy in _LEGACY_HOMES:
        path = Path(os.path.expanduser(legacy))
        if path.exists():
            return str(path)
    return str(hermes)


def _env_with_legacy(new: str, legacy: str, default: str) -> str:
    return os.getenv(new) or os.getenv(legacy) or default


def gateway_url() -> str:
    return _env_with_legacy(
        "CORTANA_GATEWAY_URL", "CLAWDBOT_GATEWAY_URL", "http://127.0.0.1:18789"
    )


def gateway_token() -> str | None:
    return os.getenv("CORTANA_GATEWAY_TOKEN") or os.getenv("CLAWDBOT_GATEWAY_TOKEN")


def browser_url() -> str:
    return _env_with_legacy(
        "CORTANA_BROWSER_URL", "CLAWDBOT_BROWSER_URL", "http://127.0.0.1:18791"
    )


def agent_config() -> dict:
    """Load agent config.

    Hermes uses config.yaml; the legacy runtime used clawdbot.json. Reads
    whichever is present.

    NOTE: the two files do not share a schema. Callers that reach for legacy
    keys (agents.defaults.models, skills.entries, ...) will get empty results
    against a Hermes config until those lookups are mapped to the Hermes
    schema. Callers must keep their `.get(..., {})` defaults.
    """
    base = Path(agent_dir())

    yaml_path = base / "config.yaml"
    if yaml_path.exists():
        try:
            import yaml  # optional dependency
        except ImportError:
            return {}
        try:
            with open(yaml_path) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    for legacy_name in ("clawdbot.json", "openclaw.json"):
        legacy_path = base / legacy_name
        if legacy_path.exists():
            try:
                with open(legacy_path) as f:
                    return json.load(f)
            except Exception:
                return {}
    return {}
