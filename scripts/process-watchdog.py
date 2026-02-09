#!/usr/bin/env python3
"""
Cortana Watchdog - Monitor for stuck processes and auto-recover
Runs every 2 minutes via cron
"""
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Config
MAX_CLAUDE_RUNTIME = 600  # 10 minutes - kill if running longer
ERROR_LOG = Path("/root/clawd/ERROR_LOG.md")
WATCHDOG_LOG = Path("/root/clawd/logs/watchdog.log")
ALERT_SCRIPT = "/root/clawd/scripts/alert.py"

def log(message: str):
    """Log to both stdout and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(WATCHDOG_LOG, "a") as f:
        f.write(line + "\n")

def send_alert(message: str, level: str = "warning"):
    """Send alert using centralized alert system"""
    try:
        subprocess.run([ALERT_SCRIPT, message, "--level", level], timeout=30)
    except Exception as e:
        log(f"Failed to send alert: {e}")

def get_claude_processes():
    """Get list of running claude processes with their runtime"""
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,etimes,cmd"],
            capture_output=True, text=True
        )
        processes = []
        for line in result.stdout.strip().split("\n")[1:]:
            parts = line.split(None, 2)
            if len(parts) >= 3 and "claude" in parts[2] and "grep" not in parts[2]:
                pid = int(parts[0])
                runtime = int(parts[1])  # elapsed time in seconds
                cmd = parts[2]
                processes.append({"pid": pid, "runtime": runtime, "cmd": cmd})
        return processes
    except Exception as e:
        log(f"Error getting processes: {e}")
        return []

def kill_process(pid: int):
    """Kill a process by PID"""
    try:
        subprocess.run(["kill", "-9", str(pid)], check=True)
        return True
    except Exception as e:
        log(f"Error killing PID {pid}: {e}")
        return False

def restart_gateway():
    """Restart the openclaw-gateway service"""
    try:
        subprocess.run(["systemctl", "restart", "openclaw-gateway"], check=True)
        return True
    except Exception as e:
        log(f"Error restarting gateway: {e}")
        return False

def check_gateway_status():
    """Check if gateway is running"""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "openclaw-gateway"],
            capture_output=True, text=True
        )
        return result.stdout.strip() == "active"
    except:
        return False

def main():
    log("Watchdog check starting...")

    # Check 1: Is gateway running?
    if not check_gateway_status():
        log("Gateway is down! Restarting...")
        if restart_gateway():
            log("Gateway restarted successfully")
            send_alert("Gateway was down - automatically restarted by watchdog", "warning")
        else:
            log("Failed to restart gateway!")
            send_alert("CRITICAL: Gateway down and failed to restart!", "critical")
        return

    # Check 2: Are there stuck claude processes?
    processes = get_claude_processes()
    stuck_processes = [p for p in processes if p["runtime"] > MAX_CLAUDE_RUNTIME]

    if stuck_processes:
        log(f"Found {len(stuck_processes)} stuck claude process(es)")
        for proc in stuck_processes:
            log(f"  Killing PID {proc['pid']} (running for {proc['runtime']}s)")
            kill_process(proc["pid"])

        # Wait a moment, then restart gateway to ensure clean state
        time.sleep(2)
        log("Restarting gateway for clean state...")
        restart_gateway()
        send_alert(f"Killed {len(stuck_processes)} stuck process(es) and restarted gateway", "warning")
    else:
        log("All systems nominal")

if __name__ == "__main__":
    main()
