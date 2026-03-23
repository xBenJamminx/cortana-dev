"""
RetellVideo Twitter/X API client via Tweepy.

Uses OAuth 1.0a with the RETELL_* credentials from /root/.openclaw/.env.
Supports posting tweets, threads, and media uploads.

Usage:
    from core.integrations.retell_twitter import post_tweet, post_thread

    # Single tweet
    post_tweet("Hello from @RetellVideo!")

    # Thread
    post_thread(["Tweet 1", "Tweet 2", "Tweet 3"])

CLI:
    python3 -m core.integrations.retell_twitter "Your tweet text here"
    python3 -m core.integrations.retell_twitter --thread "Tweet 1" "Tweet 2" "Tweet 3"
    python3 -m core.integrations.retell_twitter --media /path/to/video.mp4 "Tweet with media"
"""

import os
import sys
import tweepy
from pathlib import Path


def _load_env():
    """Load env vars from /root/.openclaw/.env into os.environ if not already set."""
    env_file = Path("/root/.openclaw/.env")
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key not in os.environ:
            os.environ[key] = val


def get_client() -> tweepy.Client:
    """Get an authenticated Tweepy v2 Client for @RetellVideo."""
    _load_env()
    return tweepy.Client(
        bearer_token=os.environ["RETELL_BEARER_TOKEN"],
        consumer_key=os.environ["RETELL_CONSUMER_KEY"],
        consumer_secret=os.environ["RETELL_CONSUMER_SECRET"],
        access_token=os.environ["RETELL_ACCESS_TOKEN"],
        access_token_secret=os.environ["RETELL_ACCESS_SECRET"],
        wait_on_rate_limit=True,
    )


def get_api() -> tweepy.API:
    """Get an authenticated Tweepy v1.1 API (needed for media uploads)."""
    _load_env()
    auth = tweepy.OAuth1UserHandler(
        os.environ["RETELL_CONSUMER_KEY"],
        os.environ["RETELL_CONSUMER_SECRET"],
        os.environ["RETELL_ACCESS_TOKEN"],
        os.environ["RETELL_ACCESS_SECRET"],
    )
    return tweepy.API(auth, wait_on_rate_limit=True)


def post_tweet(text: str, media_path: str = None, reply_to: str = None) -> dict:
    """Post a tweet as @RetellVideo.

    Args:
        text: Tweet text (max 280 chars for free tier, 4000 for premium)
        media_path: Optional path to image/video to attach
        reply_to: Optional tweet ID to reply to

    Returns:
        dict with 'id' and 'text' of the posted tweet
    """
    client = get_client()

    media_ids = None
    if media_path:
        api = get_api()
        media = api.media_upload(filename=media_path)
        media_ids = [media.media_id]

    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    if reply_to:
        kwargs["in_reply_to_tweet_id"] = reply_to

    response = client.create_tweet(**kwargs)
    tweet_id = response.data["id"]
    print(f"✅ Posted: https://x.com/RetellVideo/status/{tweet_id}")
    return {"id": tweet_id, "text": text}


def post_thread(tweets: list[str], media_path: str = None) -> list[dict]:
    """Post a thread as @RetellVideo.

    Args:
        tweets: List of tweet texts (first tweet posted, rest as replies)
        media_path: Optional media to attach to the FIRST tweet only

    Returns:
        List of dicts with 'id' and 'text' for each tweet
    """
    results = []
    reply_to = None

    for i, text in enumerate(tweets):
        mp = media_path if i == 0 else None
        result = post_tweet(text, media_path=mp, reply_to=reply_to)
        results.append(result)
        reply_to = result["id"]

    print(f"✅ Thread posted: {len(results)} tweets")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Post to @RetellVideo")
    parser.add_argument("text", nargs="+", help="Tweet text(s). Multiple = thread with --thread flag")
    parser.add_argument("--thread", action="store_true", help="Post as a thread")
    parser.add_argument("--media", type=str, help="Path to media file to attach")
    parser.add_argument("--dry-run", action="store_true", help="Print without posting")

    args = parser.parse_args()

    if args.dry_run:
        if args.thread:
            for i, t in enumerate(args.text):
                print(f"[Tweet {i+1}] {t}")
        else:
            print(f"[Tweet] {' '.join(args.text)}")
        sys.exit(0)

    if args.thread and len(args.text) > 1:
        post_thread(args.text, media_path=args.media)
    else:
        post_tweet(" ".join(args.text), media_path=args.media)
