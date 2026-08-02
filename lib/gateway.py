"""Messaging gateway control.

Cortana runs on Hermes Agent, whose gateway is managed with
`hermes gateway start|stop|status` (AGENTS.md). Some boxes still run the
gateway as a systemd unit, so every operation tries the Hermes CLI first and
falls back to systemd.

Usage:
    from lib.gateway import is_active, restart

    if not is_active():
        restart()
"""
import logging
import shutil
import subprocess

from lib.paths import gateway_service

log = logging.getLogger("cortana.gateway")

TIMEOUT = 30


def _have_hermes() -> bool:
    return shutil.which("hermes") is not None


def _run(cmd: list[str], timeout: int = TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def is_active() -> bool:
    """True if the gateway is running."""
    if _have_hermes():
        try:
            result = _run(["hermes", "gateway", "status"], timeout=10)
            if result.returncode == 0:
                out = (result.stdout + result.stderr).lower()
                # Only trust an explicit negative; otherwise rc==0 means up.
                return not any(w in out for w in ("stopped", "not running", "inactive"))
        except (subprocess.TimeoutExpired, OSError) as e:
            log.warning("hermes gateway status failed, trying systemd: %s", e)

    try:
        result = _run(["systemctl", "is-active", gateway_service()], timeout=10)
        return result.stdout.strip() == "active"
    except (subprocess.TimeoutExpired, OSError) as e:
        log.error("could not determine gateway state: %s", e)
        return False


def restart() -> bool:
    """Restart the gateway. Returns True on success."""
    if _have_hermes():
        try:
            result = _run(["hermes", "gateway", "restart"])
            if result.returncode == 0:
                log.info("gateway restarted via hermes CLI")
                return True
            log.warning("hermes gateway restart failed: %s", result.stderr.strip())
        except (subprocess.TimeoutExpired, OSError) as e:
            log.warning("hermes gateway restart errored, trying systemd: %s", e)

    try:
        result = _run(["systemctl", "restart", gateway_service()])
        if result.returncode == 0:
            log.info("gateway restarted via systemd")
            return True
        log.error("systemctl restart failed: %s", result.stderr.strip())
    except (subprocess.TimeoutExpired, OSError) as e:
        log.error("could not restart gateway: %s", e)
    return False
