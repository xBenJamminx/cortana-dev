"""
Health check primitives for Cortana monitoring.

Usage:
    from lib.health import check_gateway_http, check_disk_space, capture_diagnostics
"""
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

log = logging.getLogger("cortana.health")

DIAGNOSTICS_DIR = Path("/root/clawd/logs/diagnostics")


def check_gateway_http(port: int = 18789, timeout: float = 5.0) -> dict:
    """HTTP probe against the gateway.

    Returns:
        {"healthy": bool, "status": int|None, "latency_ms": float|None, "error": str|None}
    """
    import urllib.request
    import urllib.error

    url = f"http://127.0.0.1:{port}"
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = (time.monotonic() - start) * 1000
            return {
                "healthy": True,
                "status": resp.status,
                "latency_ms": round(latency, 1),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        latency = (time.monotonic() - start) * 1000
        # Gateway responding with non-2xx is still "alive"
        return {
            "healthy": True,
            "status": e.code,
            "latency_ms": round(latency, 1),
            "error": None,
        }
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return {
            "healthy": False,
            "status": None,
            "latency_ms": round(latency, 1),
            "error": str(e),
        }


def check_port_holder(port: int = 18789) -> list:
    """Find PIDs listening on a port using ss.

    Returns:
        List of {"pid": int, "name": str}
    """
    try:
        result = subprocess.run(
            ["ss", "-tlnp", f"sport = :{port}"],
            capture_output=True, text=True, timeout=5,
        )
        holders = []
        for line in result.stdout.strip().split("\n")[1:]:
            # Parse pid from users:(("name",pid=123,fd=4))
            if f"pid=" in line:
                import re
                for match in re.finditer(r'"([^"]+)",pid=(\d+)', line):
                    holders.append({"pid": int(match.group(2)), "name": match.group(1)})
        return holders
    except Exception as e:
        log.error("check_port_holder failed: %s", e)
        return []


def check_disk_space(threshold_warn: int = 80, threshold_crit: int = 90) -> dict:
    """Check disk usage on /.

    Returns:
        {"usage_pct": int, "free_gb": float, "alert": bool, "level": str|None}
    """
    try:
        stat = os.statvfs("/")
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - (stat.f_bfree * stat.f_frsize)
        pct = int((used / total) * 100) if total else 0
        free_gb = round(free / (1024 ** 3), 1)

        level = None
        if pct >= threshold_crit:
            level = "critical"
        elif pct >= threshold_warn:
            level = "warning"

        return {
            "usage_pct": pct,
            "free_gb": free_gb,
            "alert": level is not None,
            "level": level,
        }
    except Exception as e:
        log.error("check_disk_space failed: %s", e)
        return {"usage_pct": -1, "free_gb": -1, "alert": False, "level": None}


def check_systemd_service(name: str = "openclaw-gateway") -> dict:
    """Check systemd service status.

    Returns:
        {"active": bool, "state": str, "sub_state": str, "restart_count": int}
    """
    try:
        result = subprocess.run(
            ["systemctl", "show", name,
             "--property=ActiveState,SubState,NRestarts"],
            capture_output=True, text=True, timeout=5,
        )
        props = {}
        for line in result.stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                props[k] = v

        state = props.get("ActiveState", "unknown")
        return {
            "active": state == "active",
            "state": state,
            "sub_state": props.get("SubState", "unknown"),
            "restart_count": int(props.get("NRestarts", 0)),
        }
    except Exception as e:
        log.error("check_systemd_service failed: %s", e)
        return {"active": False, "state": "error", "sub_state": str(e), "restart_count": -1}


def check_file_freshness(path: str, max_age_hours: float = 24) -> dict:
    """Check if a file was modified recently enough.

    Returns:
        {"exists": bool, "age_hours": float|None, "fresh": bool}
    """
    p = Path(path)
    if not p.exists():
        return {"exists": False, "age_hours": None, "fresh": False}

    mtime = p.stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    return {
        "exists": True,
        "age_hours": round(age_hours, 1),
        "fresh": age_hours <= max_age_hours,
    }


def capture_diagnostics(reason: str = "unknown") -> str:
    """Capture a diagnostic snapshot and save to disk.

    Returns the path to the diagnostics file.
    """
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    diag_file = DIAGNOSTICS_DIR / f"diag-{timestamp}.txt"

    sections = []
    sections.append(f"=== Cortana Diagnostics ===")
    sections.append(f"Timestamp: {datetime.now().isoformat()}")
    sections.append(f"Reason: {reason}")
    sections.append("")

    commands = [
        ("Memory", "free -h"),
        ("Disk", "df -h /"),
        ("Port 18789 holders", "ss -tlnp sport = :18789"),
        ("Top processes (CPU)", "ps aux --sort=-%cpu | head -15"),
        ("Top processes (MEM)", "ps aux --sort=-%mem | head -15"),
        ("Gateway service", "systemctl status openclaw-gateway --no-pager -l"),
        ("Journal (last 30 lines)", "journalctl -u openclaw-gateway --no-pager -n 30"),
        ("Recent gateway log", "tail -50 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log 2>/dev/null || echo 'no log'"),
    ]

    for title, cmd in commands:
        sections.append(f"--- {title} ---")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            sections.append(result.stdout.strip())
            if result.stderr.strip():
                sections.append(f"STDERR: {result.stderr.strip()}")
        except Exception as e:
            sections.append(f"ERROR: {e}")
        sections.append("")

    content = "\n".join(sections)
    diag_file.write_text(content)
    log.info("Diagnostics saved to %s", diag_file)
    return str(diag_file)
