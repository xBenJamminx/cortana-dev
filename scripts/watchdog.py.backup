#!/usr/bin/env python3
"""
Cortana Watchdog v2 — Comprehensive health monitor and auto-recovery.

Runs every 2 minutes via cron with flock to prevent duplicate execution:
  */2 * * * * /usr/bin/flock -n /tmp/watchdog.lock python3 /root/clawd/scripts/watchdog.py >> /var/log/clawd/watchdog.log 2>&1

Features:
  - Gateway health: systemd state + HTTP probe
  - Failed state recovery: reset-failed before restart
  - Orphan port cleanup before restart
  - Alert dedup (30-min cooldown per alert type)
  - Recovery notices when issues resolve
  - Diagnostic snapshots after consecutive failures
  - Cron job freshness monitoring
  - Disk space monitoring
  - Stuck process detection
"""
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup paths before importing lib
sys.path.insert(0, "/root/clawd")

from lib.alerting import send_alert, clear_alert
from lib.health import (
    check_gateway_http,
    check_disk_space,
    check_systemd_service,
    check_port_holder,
    check_file_freshness,
    capture_diagnostics,
)

# --- Configuration ---
STATE_FILE = Path("/tmp/clawd-watchdog-state.json")
LOG_DIR = Path("/var/log/clawd")
MAX_CONSECUTIVE_FAILURES = 3
MAX_CLAUDE_RUNTIME_SECS = 1800  # 30 min - kill stuck claude processes (was 600, too aggressive for long tasks)
GATEWAY_PORT = 18789

# Cron jobs to monitor for freshness (path, max_age_hours, description)
CRON_JOBS = [
    ("/root/clawd/logs/cron-morning.log", 26, "Morning briefing"),
    ("/root/clawd/logs/cron-intel.log", 6, "Content intel"),
    ("/root/clawd/logs/twitter-cron.log", 8, "Twitter monitor"),
    ("/root/clawd/logs/youtube-cron.log", 8, "YouTube monitor"),
    ("/var/log/clawd/watchdog.log", 0.1, "Watchdog itself"),
]

# --- Logging ---
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("watchdog")


# --- State management ---
def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return {"consecutive_failures": 0, "last_restart": 0, "last_ok": 0}


def save_state(state: dict):
    try:
        STATE_FILE.write_text(json.dumps(state))
    except OSError as e:
        log.error("Failed to save state: %s", e)


# --- Gateway checks ---
def reset_and_restart_gateway() -> bool:
    """Reset failed state if needed, kill orphans, then restart."""
    svc = check_systemd_service()

    # Reset failed state if the service hit its start limit
    if svc["state"] == "failed":
        log.info("Service in failed state, running reset-failed...")
        subprocess.run(
            ["systemctl", "reset-failed", "openclaw-gateway"],
            capture_output=True, timeout=10,
        )
        time.sleep(1)

    # Kill any orphan processes holding the port
    holders = check_port_holder(GATEWAY_PORT)
    if holders:
        log.info("Killing %d orphan process(es) on port %d", len(holders), GATEWAY_PORT)
        for h in holders:
            try:
                os.kill(h["pid"], signal.SIGKILL)
                log.info("  Killed PID %d (%s)", h["pid"], h["name"])
            except ProcessLookupError:
                pass
            except PermissionError:
                log.warning("  Permission denied killing PID %d", h["pid"])
        time.sleep(2)

    # Restart the service
    log.info("Restarting openclaw-gateway...")
    result = subprocess.run(
        ["systemctl", "restart", "openclaw-gateway"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0:
        log.info("Gateway restart command succeeded")
        # Give it a moment to come up
        time.sleep(5)
        # Verify it's actually running
        http = check_gateway_http()
        if http["healthy"]:
            log.info("Gateway confirmed healthy after restart (HTTP %s, %sms)",
                     http["status"], http["latency_ms"])
            return True
        else:
            log.warning("Gateway not responding after restart: %s", http["error"])
            return False
    else:
        log.error("Gateway restart failed: %s", result.stderr.strip())
        return False


def check_gateway():
    """Main gateway health check with state tracking and alerting."""
    state = load_state()

    # Check systemd status
    svc = check_systemd_service()
    log.info("Service: state=%s sub=%s restarts=%d",
             svc["state"], svc["sub_state"], svc["restart_count"])

    # Check HTTP health
    http = check_gateway_http()
    log.info("HTTP probe: healthy=%s status=%s latency=%sms",
             http["healthy"], http["status"], http["latency_ms"])

    # Determine overall health
    is_healthy = svc["active"] and http["healthy"]

    if is_healthy:
        # Recovery detection
        if state["consecutive_failures"] > 0:
            log.info("Gateway recovered after %d consecutive failures", state["consecutive_failures"])
            clear_alert("gateway_down")
            send_alert(
                "gateway_recovered",
                f"Gateway recovered after {state['consecutive_failures']} check failures",
                level="info",
                cooldown=60,  # Allow recovery notices more frequently
            )
        state["consecutive_failures"] = 0
        state["last_ok"] = time.time()
        save_state(state)
        return

    # --- Gateway is unhealthy ---
    state["consecutive_failures"] += 1
    failures = state["consecutive_failures"]
    log.warning("Gateway unhealthy (failure #%d)", failures)

    # Attempt restart
    restarted = reset_and_restart_gateway()

    if restarted:
        state["last_restart"] = time.time()
        send_alert(
            "gateway_down",
            f"Gateway was down (failure #{failures}) — auto-restarted successfully.\n"
            f"Service was: {svc['state']}/{svc['sub_state']}\n"
            f"HTTP probe: {http.get('error', 'no response')}",
            level="warning",
        )
        state["consecutive_failures"] = 0
        state["last_ok"] = time.time()
    else:
        send_alert(
            "gateway_restart_failed",
            f"Gateway restart FAILED (failure #{failures}).\n"
            f"Service: {svc['state']}/{svc['sub_state']}\n"
            f"HTTP: {http.get('error', 'no response')}\n"
            f"Manual intervention may be needed.",
            level="critical",
        )

        # Capture diagnostics after repeated failures
        if failures >= MAX_CONSECUTIVE_FAILURES:
            diag_path = capture_diagnostics(
                reason=f"Gateway down for {failures} consecutive checks"
            )
            send_alert(
                "gateway_diagnostics",
                f"Diagnostics captured after {failures} failures: {diag_path}",
                level="info",
                cooldown=3600,
            )

    save_state(state)


# --- Stuck process detection ---
def check_stuck_processes():
    """Kill claude processes running longer than MAX_CLAUDE_RUNTIME_SECS."""
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,etimes,cmd"],
            capture_output=True, text=True, timeout=10,
        )
        killed = 0
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split(None, 2)
            if len(parts) >= 3 and "claude" in parts[2] and "grep" not in parts[2]:
                pid = int(parts[0])
                runtime = int(parts[1])
                if runtime > MAX_CLAUDE_RUNTIME_SECS:
                    log.warning("Killing stuck process PID %d (runtime %ds): %s",
                                pid, runtime, parts[2][:80])
                    try:
                        os.kill(pid, signal.SIGKILL)
                        killed += 1
                    except (ProcessLookupError, PermissionError):
                        pass

        if killed:
            send_alert(
                "stuck_processes",
                f"Killed {killed} stuck claude process(es) running >{MAX_CLAUDE_RUNTIME_SECS}s",
                level="warning",
                cooldown=600,
            )
    except Exception as e:
        log.error("Stuck process check failed: %s", e)


# --- Cron freshness ---
def check_cron_freshness():
    """Verify cron job outputs are fresh."""
    stale_jobs = []
    for path, max_hours, desc in CRON_JOBS:
        result = check_file_freshness(path, max_hours)
        if not result["fresh"]:
            age = result.get("age_hours")
            if age is not None:
                stale_jobs.append(f"{desc}: {age:.1f}h old (max {max_hours}h)")
            else:
                stale_jobs.append(f"{desc}: output file missing ({path})")

    if stale_jobs:
        msg = "Stale cron jobs detected:\n" + "\n".join(f"  - {j}" for j in stale_jobs)
        log.warning(msg)
        send_alert("cron_stale", msg, level="warning", cooldown=3600)


# --- Disk monitoring ---
def check_disk():
    """Check disk space and alert if needed."""
    disk = check_disk_space()
    log.info("Disk: %d%% used, %.1fGB free", disk["usage_pct"], disk["free_gb"])

    if disk["level"] == "critical":
        send_alert(
            "disk_critical",
            f"DISK CRITICAL: {disk['usage_pct']}% used, {disk['free_gb']}GB free",
            level="critical",
        )
    elif disk["level"] == "warning":
        send_alert(
            "disk_warning",
            f"Disk warning: {disk['usage_pct']}% used, {disk['free_gb']}GB free",
            level="warning",
            cooldown=3600,
        )
    elif disk["alert"] is False:
        # Disk recovered
        clear_alert("disk_critical")
        clear_alert("disk_warning")


# --- Main ---
def main():
    log.info("=== Watchdog v2 check ===")

    check_gateway()
    check_stuck_processes()
    check_cron_freshness()
    check_disk()

    log.info("=== Check complete ===")


if __name__ == "__main__":
    main()
