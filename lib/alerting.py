"""
Dedup-aware alerting wrapper around the existing alert.py.

Prevents alert floods by tracking last-sent time per alert key.
State is stored in /tmp/clawd-alert-dedup.json.

Usage:
    from lib.alerting import send_alert, clear_alert

    send_alert("gateway_down", "Gateway is not responding", level="critical")
    send_alert("gateway_down", "Still down", level="critical")  # suppressed within cooldown

    clear_alert("gateway_down")  # allows "recovered" message to go through
"""
import json
import time
import logging
import sys
import os
from pathlib import Path

log = logging.getLogger("cortana.alerting")

DEDUP_STATE_FILE = Path("/tmp/clawd-alert-dedup.json")
DEFAULT_COOLDOWN = 1800  # 30 minutes

# Import the existing alert.py send_alert
sys.path.insert(0, "/root/clawd/scripts")
try:
    from alert import send_alert as _raw_send_alert
except ImportError:
    log.warning("Could not import alert.py, alerts will only log")
    def _raw_send_alert(message, level="warning", **kwargs):
        log.warning("[ALERT-NOOP] [%s] %s", level, message)
        return False


def _load_state() -> dict:
    try:
        if DEDUP_STATE_FILE.exists():
            return json.loads(DEDUP_STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Corrupt dedup state, resetting: %s", e)
    return {}


def _save_state(state: dict):
    try:
        DEDUP_STATE_FILE.write_text(json.dumps(state))
    except OSError as e:
        log.error("Failed to save dedup state: %s", e)


def send_alert(
    alert_key: str,
    message: str,
    level: str = "warning",
    cooldown: int = DEFAULT_COOLDOWN,
    force: bool = False,
    details: str = None,
) -> bool:
    """Send an alert with dedup protection.

    Args:
        alert_key: Unique identifier for this alert type (e.g. "gateway_down").
        message: The alert message text.
        level: "critical", "warning", or "info".
        cooldown: Seconds before the same alert_key can fire again.
        force: If True, bypass dedup and always send.
        details: Optional extra details for error log.

    Returns:
        True if alert was sent, False if suppressed or failed.
    """
    now = time.time()
    state = _load_state()

    if not force:
        last_sent = state.get(alert_key, 0)
        if now - last_sent < cooldown:
            remaining = int(cooldown - (now - last_sent))
            log.debug(
                "Alert '%s' suppressed (cooldown %ds remaining)", alert_key, remaining
            )
            return False

    result = _raw_send_alert(message=message, level=level, details=details)

    state[alert_key] = now
    _save_state(state)

    if result:
        log.info("Alert sent [%s/%s]: %s", alert_key, level, message[:80])
    else:
        log.error("Alert send failed [%s/%s]: %s", alert_key, level, message[:80])

    return result


def clear_alert(alert_key: str):
    """Remove an alert key from dedup state, allowing the next send to go through.

    Use this when a condition has recovered and you want to send a recovery notice.
    """
    state = _load_state()
    if alert_key in state:
        del state[alert_key]
        _save_state(state)
        log.info("Alert key '%s' cleared", alert_key)
