#!/usr/bin/env python3
"""
Twitter Cookie Refresh v2 - Automates browser login to capture auth_token and ct0 for Bird CLI
Fixed: Better handling of Twitter's verification flow
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright --break-system-packages && playwright install chromium")
    from playwright.async_api import async_playwright

# Load env
env_file = Path("/root/.openclaw/.env")
if env_file.exists():
    for line in env_file.read_text().split("\n"):
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v.strip()

COOKIE_FILE = Path("/root/.config/bird/cookies.json")
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD", "")
TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL", "")

def save_cookies(auth_token, ct0):
    """Save cookies for Bird CLI"""
    COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "auth_token": auth_token,
        "ct0": ct0,
        "updated_at": datetime.now().isoformat()
    }
    with open(COOKIE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    # Also update bashrc for Bird CLI
    bashrc = Path.home() / ".bashrc"
    content = bashrc.read_text() if bashrc.exists() else ""

    # Update or add AUTH_TOKEN
    if "AUTH_TOKEN=" in content:
        lines = content.split("\n")
        lines = [l if not l.startswith("export AUTH_TOKEN=") else f'export AUTH_TOKEN="{auth_token}"' for l in lines]
        content = "\n".join(lines)
    else:
        content += f'\nexport AUTH_TOKEN="{auth_token}"\n'

    # Update or add CT0
    if "CT0=" in content:
        lines = content.split("\n")
        lines = [l if not l.startswith("export CT0=") else f'export CT0="{ct0}"' for l in lines]
        content = "\n".join(lines)
    else:
        content += f'export CT0="{ct0}"\n'

    bashrc.write_text(content)
    print(f"Cookies saved to {COOKIE_FILE} and ~/.bashrc")

async def login_and_get_cookies():
    """Automate Twitter login and extract cookies"""

    if not TWITTER_USERNAME or not TWITTER_PASSWORD:
        print("ERROR: Set TWITTER_USERNAME and TWITTER_PASSWORD in /root/.openclaw/.env")
        return None, None

    print(f"Logging in as @{TWITTER_USERNAME}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        try:
            # Go to Twitter login
            print("Loading Twitter login page...")
            await page.goto("https://twitter.com/i/flow/login", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            # Take screenshot of initial state
            await page.screenshot(path="/tmp/twitter-step1.png")
            print("Screenshot saved: /tmp/twitter-step1.png")

            # Enter username
            print("Looking for username input...")
            try:
                username_input = page.locator('input[autocomplete="username"]')
                await username_input.wait_for(state="visible", timeout=15000)
                print("Entering username...")
                await username_input.fill(TWITTER_USERNAME)
                await asyncio.sleep(1)

                # Click Next button
                next_btn = page.locator('button:has-text("Next"), div[role="button"]:has-text("Next")')
                await next_btn.click()
                await asyncio.sleep(3)
            except Exception as e:
                print(f"Username step error: {e}")
                await page.screenshot(path="/tmp/twitter-error-username.png")
                await browser.close()
                return None, None

            await page.screenshot(path="/tmp/twitter-step2.png")
            print("Screenshot saved: /tmp/twitter-step2.png")

            # Check for unusual login activity / verification
            print("Checking for verification prompts...")
            try:
                # Look for "Enter your phone number or email address" or similar
                verify_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
                if await verify_input.is_visible(timeout=5000):
                    print("Verification required! Entering email...")
                    if TWITTER_EMAIL:
                        await verify_input.fill(TWITTER_EMAIL)
                        await asyncio.sleep(1)
                        next_btn = page.locator('button:has-text("Next"), div[role="button"]:has-text("Next")')
                        await next_btn.click()
                        await asyncio.sleep(3)
                    else:
                        print("ERROR: TWITTER_EMAIL not set but verification required")
                        await browser.close()
                        return None, None
            except:
                print("No verification prompt found, continuing...")

            await page.screenshot(path="/tmp/twitter-step3.png")
            print("Screenshot saved: /tmp/twitter-step3.png")

            # Enter password
            print("Looking for password input...")
            try:
                password_input = page.locator('input[name="password"], input[type="password"]')
                await password_input.wait_for(state="visible", timeout=15000)
                print("Entering password...")
                await password_input.fill(TWITTER_PASSWORD)
                await asyncio.sleep(1)

                # Click Log in button
                login_btn = page.locator('button:has-text("Log in"), div[role="button"]:has-text("Log in")')
                await login_btn.click()
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Password step error: {e}")
                await page.screenshot(path="/tmp/twitter-error-password.png")
                print("Screenshot saved: /tmp/twitter-error-password.png")
                await browser.close()
                return None, None

            await page.screenshot(path="/tmp/twitter-step4.png")
            print("Screenshot saved: /tmp/twitter-step4.png")

            # Check for 2FA
            print("Checking for 2FA...")
            try:
                twofa_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
                if await twofa_input.is_visible(timeout=5000):
                    print("\n*** 2FA REQUIRED! ***")
                    print("Enter your 2FA code: ", end="", flush=True)
                    code = input()
                    await twofa_input.fill(code)
                    await asyncio.sleep(1)
                    next_btn = page.locator('button:has-text("Next"), div[role="button"]:has-text("Next")')
                    await next_btn.click()
                    await asyncio.sleep(5)
            except:
                print("No 2FA prompt found")

            # Wait for redirect to home or check current URL
            print("Waiting for successful login...")
            try:
                await page.wait_for_url("**/home**", timeout=30000)
                print("Login successful! Redirected to home.")
            except:
                current_url = page.url
                print(f"Current URL: {current_url}")
                if "home" in current_url or "twitter.com" in current_url:
                    print("Appears to be logged in")
                else:
                    await page.screenshot(path="/tmp/twitter-login-final.png")
                    print("May not be fully logged in. Check /tmp/twitter-login-final.png")

            # Extract cookies
            print("Extracting cookies...")
            cookies = await context.cookies()
            auth_token = None
            ct0 = None

            for cookie in cookies:
                if cookie["name"] == "auth_token":
                    auth_token = cookie["value"]
                    print(f"Found auth_token: {auth_token[:20]}...")
                elif cookie["name"] == "ct0":
                    ct0 = cookie["value"]
                    print(f"Found ct0: {ct0[:20]}...")

            await browser.close()

            if auth_token and ct0:
                return auth_token, ct0
            else:
                print("ERROR: Could not find required cookies")
                print(f"All cookies: {[c['name'] for c in cookies]}")
                return None, None

        except Exception as e:
            print(f"ERROR: {e}")
            await page.screenshot(path="/tmp/twitter-login-error.png")
            print("Screenshot saved to /tmp/twitter-login-error.png")
            await browser.close()
            return None, None

def test_cookies():
    """Test if current cookies work"""
    if not COOKIE_FILE.exists():
        print("No cookies found")
        return False

    data = json.loads(COOKIE_FILE.read_text())
    auth_token = data.get("auth_token")
    ct0 = data.get("ct0")

    if not auth_token or not ct0:
        print("Invalid cookie file")
        return False

    # Test with Bird CLI
    import subprocess
    result = subprocess.run(
        ["bird", "me", "--auth-token", auth_token, "--ct0", ct0],
        capture_output=True, text=True, timeout=15
    )

    if result.returncode == 0:
        print(f"Cookies valid! {result.stdout.strip()}")
        return True
    else:
        print(f"Cookies invalid: {result.stderr}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 twitter-cookie-refresh.py --refresh|--test")
        print("\nRequired in /root/.openclaw/.env:")
        print("  TWITTER_USERNAME=your_username")
        print("  TWITTER_PASSWORD=your_password")
        print("  TWITTER_EMAIL=your_email  # for verification")
        return

    cmd = sys.argv[1]

    if cmd == "--refresh":
        auth_token, ct0 = await login_and_get_cookies()
        if auth_token and ct0:
            save_cookies(auth_token, ct0)
            print("\nCookies refreshed successfully!")
        else:
            print("\nFailed to refresh cookies")

    elif cmd == "--test":
        test_cookies()

    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    asyncio.run(main())
