#!/usr/bin/env python3
"""
Cortana Daily Health Report — Telegram summary of system health.

Runs daily at 7 AM ET (12:00 UTC) before morning briefing.
Cron: 0 12 * * * /usr/bin/python3 /root/clawd/scripts/health-report.py >> /var/log/clawd/health-report.log 2>&1
"""
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

def _load_env():
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.replace("export ", "").strip()
                    if key and not os.environ.get(key):
                        os.environ[key] = val
_load_env()

sys.path.insert(0, "/root/clawd")

from lib.health import (
    check_gateway_http,
    check_disk_space,
    check_systemd_service,
    check_file_freshness,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("health-report")

# Telegram config
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Log directories
CLAWD_LOGS = Path("/root/clawd/logs")
SYSTEM_LOGS = Path("/var/log/clawd")
GATEWAY_LOGS = Path("/tmp/openclaw")


def send_telegram(message: str) -> bool:
    """Send message via Telegram."""
    import urllib.request
    import urllib.error

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode()

    try:
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        log.error("Telegram send failed: %s", e)
        return False


def get_24h_restart_count() -> int:
    """Count gateway restarts in last 24h from journal."""
    try:
        result = subprocess.run(
            ["journalctl", "-u", "openclaw-gateway", "--since", "24 hours ago",
             "--no-pager", "-o", "short"],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.count("Started OpenClaw Gateway")
    except Exception:
        return -1


def check_api_reachability() -> list:
    """Test if key external APIs are reachable (not authed, just DNS+TCP)."""
    import urllib.request
    import urllib.error

    endpoints = [
        ("Reddit JSON", "https://www.reddit.com/r/artificial/hot.json?limit=1"),
        ("Telegram API", f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"),
        ("YouTube", "https://www.youtube.com/"),
    ]

    results = []
    for name, url in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CortanaHealthCheck/1.0"})
            start = time.monotonic()
            with urllib.request.urlopen(req, timeout=10) as resp:
                latency = int((time.monotonic() - start) * 1000)
                results.append(f"  {name}: {resp.status} ({latency}ms)")
        except urllib.error.HTTPError as e:
            results.append(f"  {name}: HTTP {e.code}")
        except Exception as e:
            results.append(f"  {name}: FAIL ({e})")

    return results


def get_log_sizes() -> list:
    """Get sizes of key log files."""
    log_dirs = [CLAWD_LOGS, SYSTEM_LOGS, GATEWAY_LOGS]
    entries = []
    total_bytes = 0

    for d in log_dirs:
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.stat().st_size > 0:
                size = f.stat().st_size
                total_bytes += size
                if size > 1_000_000:  # Only show files > 1MB
                    entries.append(f"  {f.name}: {size / 1_000_000:.1f}MB")

    entries.append(f"  *Total*: {total_bytes / 1_000_000:.1f}MB")
    return entries


def get_recent_alerts(hours: int = 24, limit: int = 5) -> list:
    """Get recent alerts from the alert log."""
    alert_log = CLAWD_LOGS / "alerts.log"
    if not alert_log.exists():
        return ["  No alert log found"]

    cutoff = datetime.now() - timedelta(hours=hours)
    recent = []

    try:
        for line in alert_log.read_text().strip().split("\n"):
            if not line.strip():
                continue
            # Parse timestamp from [YYYY-MM-DD HH:MM:SS]
            try:
                ts_str = line[1:20]
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                if ts >= cutoff:
                    # Truncate long lines
                    msg = line[22:].strip()[:100]
                    recent.append(f"  {ts.strftime('%H:%M')} {msg}")
            except (ValueError, IndexError):
                continue
    except Exception as e:
        return [f"  Error reading alerts: {e}"]

    if not recent:
        return ["  No alerts in last 24h"]
    return recent[-limit:]


def get_cron_freshness() -> list:
    """Check freshness of cron job outputs."""
    jobs = [
        ("Morning briefing", "/root/clawd/logs/cron-morning.log", 26),
        ("Content intel", "/root/clawd/logs/cron-intel.log", 6),
        ("Twitter monitor", "/root/clawd/logs/twitter-cron.log", 8),
        ("YouTube monitor", "/root/clawd/logs/youtube-cron.log", 8),
        ("Content analytics", "/root/clawd/logs/analytics-cron.log", 26),
        ("Reddit monitor", "/root/clawd/logs/reddit-monitor.log", 26),
    ]

    results = []
    for name, path, max_hours in jobs:
        info = check_file_freshness(path, max_hours)
        if info["fresh"]:
            results.append(f"  {name}: {info['age_hours']:.1f}h ago")
        elif info["exists"]:
            results.append(f"  {name}: {info['age_hours']:.1f}h ago (STALE)")
        else:
            results.append(f"  {name}: MISSING")

    return results


def main():
    log.info("Generating daily health report...")

    # Collect all data
    gateway_http = check_gateway_http()
    gateway_svc = check_systemd_service()
    restart_count = get_24h_restart_count()
    disk = check_disk_space()
    apis = check_api_reachability()
    cron_status = get_cron_freshness()
    log_sizes = get_log_sizes()
    recent_alerts = get_recent_alerts()

    # Build the report
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    gw_icon = "running" if gateway_svc["active"] else "DOWN"
    gw_http = f"{gateway_http['status']}, {gateway_http['latency_ms']}ms" if gateway_http["healthy"] else f"FAIL: {gateway_http['error']}"
    disk_icon = "OK" if not disk["alert"] else disk["level"].upper()

    sections = []
    sections.append(f"*Cortana Daily Health Report*")
    sections.append(f"_{now}_\n")

    sections.append(f"*Gateway*: {gw_icon}")
    sections.append(f"  HTTP: {gw_http}")
    sections.append(f"  24h restarts: {restart_count}")
    sections.append(f"  Service restarts (total): {gateway_svc['restart_count']}\n")

    sections.append(f"*Disk*: {disk['usage_pct']}% used, {disk['free_gb']}GB free [{disk_icon}]\n")

    sections.append("*API Reachability*:")
    sections.extend(apis)
    sections.append("")

    sections.append("*Cron Jobs*:")
    sections.extend(cron_status)
    sections.append("")

    sections.append("*Log Sizes (>1MB)*:")
    sections.extend(log_sizes)
    sections.append("")

    sections.append("*Recent Alerts (24h)*:")
    sections.extend(recent_alerts)

    report = "\n".join(sections)
    log.info("Report:\n%s", report)

    # Send via Telegram
    if send_telegram(report):
        log.info("Health report sent to Telegram")
    else:
        log.error("Failed to send health report to Telegram")

    log.info("Done")


if __name__ == "__main__":
    main()
