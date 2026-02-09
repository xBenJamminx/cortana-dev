#!/usr/bin/env python3
"""
Twitter Cookie Manager - Validates cookies and alerts when refresh needed

Usage:
  python3 twitter-cookie-manager.py --check      # Check if cookies are valid
  python3 twitter-cookie-manager.py --refresh    # Open browser for manual login
  python3 twitter-cookie-manager.py --cron       # For cron: check + alert if expired

Cron setup (check daily at 6am):
  0 6 * * * /usr/bin/python3 /root/clawd/scripts/twitter-cookie-manager.py --cron
"""
import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
import requests

# Load env
env_file = Path("/root/.openclaw/.env")
if env_file.exists():
    for line in env_file.read_text().split("\n"):
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

COOKIE_FILE = Path("/root/.config/bird/cookies.json")
LOG_FILE = Path("/root/clawd/logs/cookie-manager.log")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def send_telegram_alert(message):
    """Send alert via Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram not configured, skipping alert")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        log(f"Telegram error: {e}")
        return False

def load_cookies():
    """Load cookies from file"""
    if COOKIE_FILE.exists():
        return json.loads(COOKIE_FILE.read_text())
    return {}

def save_cookies(cookies):
    """Save cookies to file"""
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f, indent=2)

def test_cookie(account_name, auth_token, ct0):
    """Test if a cookie is still valid using Bird CLI"""
    try:
        result = subprocess.run(
            ["bird", "search", "from:OpenAI", "--json", "-n", "1", "--auth-token", auth_token, "--ct0", ct0],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0 and result.stdout.strip():
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def check_all_cookies():
    """Check all stored cookies"""
    cookies = load_cookies()
    results = {}

    for account, creds in cookies.items():
        auth_token = creds.get("auth_token", "")
        ct0 = creds.get("ct0", "")

        if not auth_token or not ct0:
            results[account] = {"valid": False, "error": "Missing credentials"}
            continue

        valid, info = test_cookie(account, auth_token, ct0)
        results[account] = {"valid": valid, "info": info}

        status = "✓ VALID" if valid else "✗ EXPIRED"
        log(f"{account}: {status}")

    return results

async def refresh_cookies_interactive(account_name):
    """Open browser for manual login, then capture cookies"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log("Playwright not installed")
        return None, None

    user_data_dir = Path(f"/root/.config/playwright/{account_name}")
    user_data_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOpening browser for @{account_name}...")
    print("1. Log in to Twitter manually")
    print("2. Once logged in, press Enter here to capture cookies")
    print("3. Or type 'cancel' to abort\n")

    async with async_playwright() as p:
        # Launch with persistent context (saves session)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,  # Show the browser
            args=["--start-maximized"]
        )

        page = await browser.new_page()
        await page.goto("https://twitter.com/login")

        # Wait for user input
        user_input = input("Press Enter when logged in (or 'cancel'): ").strip().lower()

        if user_input == "cancel":
            await browser.close()
            return None, None

        # Navigate to home to ensure we're logged in
        await page.goto("https://twitter.com/home")
        await asyncio.sleep(2)

        # Extract cookies
        cookies = await browser.cookies()
        auth_token = None
        ct0 = None

        for cookie in cookies:
            if cookie["name"] == "auth_token":
                auth_token = cookie["value"]
            elif cookie["name"] == "ct0":
                ct0 = cookie["value"]

        await browser.close()

        if auth_token and ct0:
            return auth_token, ct0
        else:
            log("Could not find required cookies")
            return None, None

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "--check":
        log("Checking all cookies...")
        results = check_all_cookies()

        all_valid = all(r["valid"] for r in results.values())
        if all_valid:
            print("\n✓ All cookies are valid!")
        else:
            expired = [k for k, v in results.items() if not v["valid"]]
            print(f"\n✗ Expired cookies: {', '.join(expired)}")
            print("Run with --refresh to update")

    elif cmd == "--cron":
        log("Cron check: validating cookies...")
        results = check_all_cookies()

        expired = [k for k, v in results.items() if not v["valid"]]

        if expired:
            message = (
                "⚠️ *Twitter Cookie Alert*\n\n"
                f"Expired accounts: {', '.join(expired)}\n\n"
                "Please refresh cookies:\n"
                "`ssh openclaw`\n"
                "`python3 /root/clawd/scripts/twitter-cookie-manager.py --refresh`"
            )
            send_telegram_alert(message)
            log(f"Alert sent for expired cookies: {expired}")
        else:
            log("All cookies valid, no alert needed")

    elif cmd == "--refresh":
        account = sys.argv[2] if len(sys.argv) > 2 else None

        if not account:
            cookies = load_cookies()
            print("Available accounts:")
            for i, acc in enumerate(cookies.keys(), 1):
                print(f"  {i}. {acc}")
            print(f"  {len(cookies)+1}. Add new account")

            choice = input("\nSelect account number: ").strip()
            try:
                idx = int(choice) - 1
                if idx < len(cookies):
                    account = list(cookies.keys())[idx]
                else:
                    account = input("Enter new account username: ").strip()
            except:
                print("Invalid choice")
                return

        log(f"Refreshing cookies for @{account}...")
        auth_token, ct0 = asyncio.run(refresh_cookies_interactive(account))

        if auth_token and ct0:
            cookies = load_cookies()
            cookies[account] = {
                "auth_token": auth_token,
                "ct0": ct0,
                "updated_at": datetime.now().isoformat()
            }
            save_cookies(cookies)
            log(f"Cookies updated for @{account}")
            print(f"\n✓ Cookies saved for @{account}!")
        else:
            print("\n✗ Failed to capture cookies")

    elif cmd == "--status":
        cookies = load_cookies()
        print("\nStored accounts:")
        for account, creds in cookies.items():
            updated = creds.get("updated_at", "unknown")
            print(f"  • {account} (updated: {updated})")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
