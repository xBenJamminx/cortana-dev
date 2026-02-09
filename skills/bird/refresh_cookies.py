"""Refresh Bird CLI Twitter cookies using Playwright persistent browser context"""
import asyncio
import json
import os
import sys

async def refresh_cookies():
    from playwright.async_api import async_playwright
    
    state_dir = "/root/.twitter-session"
    os.makedirs(state_dir, exist_ok=True)
    
    async with async_playwright() as p:
        # Persistent context keeps cookies between runs
        browser = await p.chromium.launch_persistent_context(
            state_dir,
            headless=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Navigate to Twitter to refresh session
        await page.goto("https://x.com/home", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        
        # Check if we are logged in
        url = page.url
        if "/login" in url or "/i/flow/login" in url:
            print("NOT_LOGGED_IN")
            print(f"Current URL: {url}")
            print("Need to log in first. Run with --login flag.")
            await browser.close()
            return False
        
        # Extract cookies
        cookies = await browser.cookies("https://x.com")
        auth_token = None
        ct0 = None
        
        for cookie in cookies:
            if cookie["name"] == "auth_token":
                auth_token = cookie["value"]
            elif cookie["name"] == "ct0":
                ct0 = cookie["value"]
        
        if auth_token and ct0:
            # Save to env file for easy sourcing
            env_path = "/root/.bird-env"
            with open(env_path, "w") as f:
                f.write(f"export AUTH_TOKEN={auth_token}\n")
                f.write(f"export CT0={ct0}\n")
            
            print(f"REFRESHED")
            print(f"AUTH_TOKEN={auth_token[:20]}...")
            print(f"CT0={ct0[:20]}...")
            print(f"Saved to {env_path}")
        else:
            print("NO_COOKIES")
            print(f"auth_token: {bool(auth_token)}, ct0: {bool(ct0)}")
        
        await browser.close()
        return bool(auth_token and ct0)

if __name__ == "__main__":
    result = asyncio.run(refresh_cookies())
    sys.exit(0 if result else 1)
