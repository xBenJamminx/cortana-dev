"""
Bird CLI wrapper — shared utilities for all Twitter/X tools.

WARNING: Bird CLI calls are DISABLED while @xBenJamminx account is suspended.
DO NOT make any Bird CLI calls that could hurt the appeal process.
All scripts importing from this module should have their Bird CLI calls
neutralized at the script level. See each script's main() function.

Provides a clean Python interface to Bird CLI commands with auth handling,
JSON parsing, tweet normalization, Telegram delivery, and logging.

Usage:
    from lib.bird import bird_search, bird_user_tweets, bird_home, send_telegram, log
"""

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Auth ─────────────────────────────────────────────────────────────────

BIRD_ENV_FILE = Path.home() / ".bird-env"
OPENCLAW_ENV_FILE = Path("/root/.openclaw/.env")

_env_cache = {}
_bird_auth_cache = {}


def load_env() -> dict:
    """Load key=value pairs from /root/.openclaw/.env (cached)."""
    if _env_cache:
        return _env_cache
    try:
        with open(OPENCLAW_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    # Handle 'export KEY=VAL' format
                    if line.startswith("export "):
                        line = line[7:]
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    _env_cache[key] = val
    except FileNotFoundError:
        pass
    return _env_cache


def load_bird_env(account: str = "ben") -> tuple:
    """Load Bird CLI auth tokens from ~/.bird-env.

    Args:
        account: "ben" for @xBenJamminx, "cortana" for @CortanaOps

    Returns:
        (auth_token, ct0) tuple
    """
    cache_key = account
    if cache_key in _bird_auth_cache:
        return _bird_auth_cache[cache_key]

    auth_token = ""
    ct0 = ""

    try:
        text = BIRD_ENV_FILE.read_text()
        prefix = "CORTANA_BIRD_" if account == "cortana" else "BIRD_"

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            if key == f"{prefix}AUTH_TOKEN":
                auth_token = val
            elif key == f"{prefix}CT0":
                ct0 = val
    except FileNotFoundError:
        pass

    _bird_auth_cache[cache_key] = (auth_token, ct0)
    return auth_token, ct0


# ── Bird CLI Commands ────────────────────────────────────────────────────

def bird_cmd(command: str, args: list = None, account: str = "ben",
             timeout: int = 30, json_output: bool = True) -> list | dict | str:
    """Run a Bird CLI command and return parsed output.

    Args:
        command: Bird subcommand (search, read, home, etc.)
        args: Additional CLI arguments
        account: "ben" or "cortana"
        timeout: Subprocess timeout in seconds
        json_output: If True, add --json flag and parse output

    Returns:
        Parsed JSON (list of dicts for multi-line, dict for single) or raw string

    Raises:
        BirdError: On command failure or timeout
    """
    auth_token, ct0 = load_bird_env(account)

    cmd = ["bird", command]
    if args:
        cmd.extend(args)
    if json_output:
        cmd.append("--json")
    if auth_token:
        cmd.extend(["--auth-token", auth_token])
    if ct0:
        cmd.extend(["--ct0", ct0])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        raise BirdError(f"Bird command timed out after {timeout}s: {' '.join(cmd[:4])}")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "429" in stderr or "Rate limit" in stderr.lower():
            raise BirdRateLimited(f"Rate limited: {stderr[:200]}")
        raise BirdError(f"Bird command failed (exit {result.returncode}): {stderr[:200]}")

    if not json_output:
        return result.stdout.strip()

    # Parse JSON — Bird outputs one JSON object per line for multi-result commands
    output = result.stdout.strip()
    if not output:
        return []

    objects = []
    for line in output.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            objects.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    # If only one object, check if it's already a list (some commands return arrays)
    if len(objects) == 1 and isinstance(objects[0], list):
        return objects[0]

    return objects


def bird_search(query: str, n: int = 20, account: str = "ben") -> list:
    """Search tweets. Returns list of raw tweet dicts."""
    return bird_cmd("search", [query, "-n", str(n)], account=account)


def bird_user_tweets(username: str, n: int = 10, account: str = "ben") -> list:
    """Get a user's recent tweets."""
    return bird_cmd("user-tweets", [username, "-n", str(n)], account=account)


def bird_home(n: int = 50, account: str = "ben") -> list:
    """Get home timeline."""
    return bird_cmd("home", ["-n", str(n)], account=account)


def bird_mentions(account: str = "ben") -> list:
    """Get mentions of the authenticated user."""
    return bird_cmd("mentions", account=account)


def bird_read(tweet_id: str, account: str = "ben") -> list:
    """Read a single tweet by ID or URL."""
    return bird_cmd("read", [tweet_id], account=account)


def bird_thread(tweet_id: str, account: str = "ben") -> list:
    """Get full conversation thread for a tweet."""
    return bird_cmd("thread", [tweet_id], account=account)


def bird_about(username: str, account: str = "ben") -> list:
    """Get user profile information."""
    return bird_cmd("about", [username], account=account)


def bird_followers(username: str, n: int = 50, account: str = "ben") -> list:
    """Get a user's followers."""
    return bird_cmd("followers", ["--user", username, "-n", str(n)], account=account)


def bird_following(username: str, n: int = 50, account: str = "ben") -> list:
    """Get accounts a user follows."""
    return bird_cmd("following", ["--user", username, "-n", str(n)], account=account)


def bird_bookmarks(n: int = 50, account: str = "ben") -> list:
    """Get bookmarked tweets."""
    return bird_cmd("bookmarks", ["-n", str(n)], account=account)


def bird_post(text: str, account: str = "ben") -> str:
    """Post a tweet. Returns raw output (not JSON)."""
    return bird_cmd("tweet", [text], account=account, json_output=False)


def bird_reply(tweet_id: str, text: str, account: str = "ben") -> str:
    """Reply to a tweet. Returns raw output."""
    return bird_cmd("reply", [tweet_id, text], account=account, json_output=False)


# ── Tweet Normalization ──────────────────────────────────────────────────

def normalize_tweet(raw: dict) -> dict:
    """Normalize Bird CLI tweet output into a standard dict.

    Bird CLI output varies by command — this normalizes field names
    so all downstream code can use consistent keys.
    """
    # Text
    text = raw.get("text", raw.get("full_text", ""))

    # ID
    tweet_id = str(raw.get("id_str", raw.get("id", "")))

    # Engagement metrics — Bird uses different field names depending on version
    likes = raw.get("favorite_count", raw.get("likes", raw.get("like_count", 0))) or 0
    retweets = raw.get("retweet_count", raw.get("retweets", 0)) or 0
    replies = raw.get("reply_count", raw.get("replies", 0)) or 0
    bookmarks = raw.get("bookmark_count", raw.get("bookmarks", 0)) or 0
    impressions = raw.get("impression_count", raw.get("impressions", raw.get("views", 0))) or 0

    # Author info — may be nested under 'user' or flat
    user = raw.get("user", {})
    username = user.get("screen_name", user.get("username", raw.get("username", raw.get("screen_name", "?"))))
    name = user.get("name", raw.get("name", "?"))
    followers = user.get("followers_count", user.get("followers", raw.get("followers_count", 0))) or 0

    # Timestamps
    created_at = raw.get("created_at", "")
    age_hours = _compute_age_hours(created_at)

    # Velocity
    velocity = likes / age_hours if age_hours > 0 else 0

    return {
        "id": tweet_id,
        "text": text,
        "username": username,
        "name": name,
        "followers": followers,
        "created_at": created_at,
        "age_hours": round(age_hours, 1),
        "likes": likes,
        "retweets": retweets,
        "replies": replies,
        "bookmarks": bookmarks,
        "impressions": impressions,
        "velocity": round(velocity, 2),
        "url": f"https://x.com/{username}/status/{tweet_id}",
    }


def _compute_age_hours(created_at: str) -> float:
    """Compute age in hours from a timestamp string."""
    if not created_at:
        return 1.0  # default

    now = datetime.now(timezone.utc)

    # Try ISO format first
    for fmt_func in [_parse_iso, _parse_twitter_format]:
        dt = fmt_func(created_at)
        if dt:
            return max((now - dt).total_seconds() / 3600, 0.1)

    return 1.0


def _parse_iso(s: str):
    """Parse ISO 8601 timestamps."""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _parse_twitter_format(s: str):
    """Parse Twitter's 'Wed Oct 10 20:19:24 +0000 2018' format."""
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except (ValueError, AttributeError):
        return None


# ── Telegram ─────────────────────────────────────────────────────────────

def send_telegram(text: str, parse_mode: str = "Markdown") -> bool:
    """Send a message to Telegram. Handles 4096 char splitting.

    Returns True if all chunks sent successfully.
    """
    env = load_env()
    bot_token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not found in .env")
        return False

    # Split into 4096-char chunks if needed
    chunks = []
    while text:
        if len(text) <= 4000:
            chunks.append(text)
            break
        # Find a good split point (newline near the limit)
        split_at = text.rfind("\n", 0, 4000)
        if split_at < 2000:
            split_at = 4000
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    success = True
    for i, chunk in enumerate(chunks):
        payload = json.dumps({
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }).encode()

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    print(f"⚠️  Telegram error: {result}")
                    success = False
        except Exception as e:
            print(f"⚠️  Failed to send to Telegram: {e}")
            success = False

        # Small delay between chunks
        if i < len(chunks) - 1:
            time.sleep(0.5)

    if success:
        print("✅ Sent to Telegram!")
    return success


# ── Logging ──────────────────────────────────────────────────────────────

def log(msg: str, log_file: str = None):
    """Standard timestamped logging to console and optionally a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(line + "\n")


# ── Retry Helper ─────────────────────────────────────────────────────────

def retry_on_rate_limit(fn, max_retries: int = 3, base_delay: int = 30):
    """Retry a function that might raise BirdRateLimited."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except BirdRateLimited as e:
            if attempt == max_retries:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"  ⏳ Rate limited, waiting {delay}s (attempt {attempt + 1}/{max_retries})...")
            time.sleep(delay)


# ── Exceptions ───────────────────────────────────────────────────────────

class BirdError(Exception):
    """Base exception for Bird CLI errors."""
    pass


class BirdRateLimited(BirdError):
    """Raised when Bird CLI hits a Twitter rate limit."""
    pass
