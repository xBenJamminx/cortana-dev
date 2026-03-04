#!/usr/bin/env python3
"""
Review Monitor MVP - Cortana Autonomous Business #1

Monitors Google/Yelp reviews for businesses, detects new/negative reviews,
drafts AI responses, and delivers alerts via email + Telegram.

Multi-client ready: each client gets their own config + review DB.

Usage:
    python3 review_monitor.py --setup "Business Name" "City, State" --client acme-plumbing
    python3 review_monitor.py --check --client acme-plumbing
    python3 review_monitor.py --check-all                    # Check all clients
    python3 review_monitor.py --digest --client acme-plumbing
    python3 review_monitor.py --digest-all                   # Digest for all clients
    python3 review_monitor.py --list-clients                 # List configured clients
    python3 review_monitor.py --add-client acme-plumbing --email owner@acme.com --name "Acme Plumbing"
"""

import argparse
import json
import os
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.openclaw/.env"))

import requests

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
CLIENTS_DIR = DATA_DIR / "clients"
DATA_DIR.mkdir(exist_ok=True)
CLIENTS_DIR.mkdir(exist_ok=True)

MASTER_CONFIG = DATA_DIR / "master_config.json"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def get_client_dir(client_slug):
    d = CLIENTS_DIR / client_slug
    d.mkdir(exist_ok=True)
    return d


def slugify(name):
    return name.lower().replace(" ", "-").replace("'", "").replace("&", "and")


def load_master_config():
    if MASTER_CONFIG.exists():
        with open(MASTER_CONFIG) as f:
            return json.load(f)
    return {"clients": {}}


def save_master_config(mc):
    with open(MASTER_CONFIG, "w") as f:
        json.dump(mc, f, indent=2)


def load_reviews_db(client_slug):
    db_file = get_client_dir(client_slug) / "reviews.json"
    if db_file.exists():
        with open(db_file) as f:
            return json.load(f)
    return {"reviews": [], "seen_ids": []}


def save_reviews_db(db, client_slug):
    db_file = get_client_dir(client_slug) / "reviews.json"
    with open(db_file, "w") as f:
        json.dump(db, f, indent=2)


def load_config(client_slug):
    cfg_file = get_client_dir(client_slug) / "config.json"
    if cfg_file.exists():
        with open(cfg_file) as f:
            return json.load(f)
    return {}


def save_config(config, client_slug):
    cfg_file = get_client_dir(client_slug) / "config.json"
    with open(cfg_file, "w") as f:
        json.dump(config, f, indent=2)


# --- Google Maps Reviews via open-source scraper ---
# Uses: github.com/georgekhananaev/google-reviews-scraper-pro
# Zero cost, self-hosted, no API keys needed.

import sqlite3
import yaml

SCRAPER_DIR = PROJECT_DIR / "scraper"
SCRAPER_DB = SCRAPER_DIR / "reviews.db"


def search_google_place(business_name, location):
    """Return a dict with business info. For the open-source scraper,
    the user provides a Google Maps URL directly via --setup."""
    # We still accept name + location for display purposes,
    # but the actual scraping uses the Google Maps URL stored in config.
    return {
        "name": business_name,
        "formatted_address": location,
        "rating": 0,
        "user_ratings_total": 0,
    }


def run_scraper_for_client(client_slug):
    """Generate a config.yaml for the scraper and run it for one client."""
    config = load_config(client_slug)
    maps_url = config.get("business", {}).get("maps_url", "")
    if not maps_url:
        print(f"  No Google Maps URL configured for {client_slug}. Skipping Google scrape.")
        return []

    # Build minimal scraper config
    scraper_config = {
        "headless": True,
        "sort_by": "newest",
        "scrape_mode": "update",
        "stop_threshold": 3,
        "max_reviews": 0,
        "max_scroll_attempts": 30,
        "scroll_idle_limit": 10,
        "db_path": str(SCRAPER_DB),
        "convert_dates": True,
        "download_images": False,
        "use_mongodb": False,
        "use_s3": False,
        "backup_to_json": False,
        "businesses": [
            {
                "url": maps_url,
                "custom_params": {
                    "company": config.get("business", {}).get("name", client_slug),
                    "client": client_slug,
                },
            }
        ],
    }

    # Write temp config
    tmp_config = SCRAPER_DIR / f"config_{client_slug}.yaml"
    with open(tmp_config, "w") as f:
        yaml.dump(scraper_config, f)

    # Run the scraper
    print(f"  Running open-source scraper for {client_slug}...")
    try:
        result = subprocess.run(
            [sys.executable, str(SCRAPER_DIR / "start.py"), "--config", str(tmp_config)],
            capture_output=True, text=True, timeout=300, cwd=str(SCRAPER_DIR),
        )
        if result.returncode != 0:
            print(f"  Scraper error: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        print(f"  Scraper timed out for {client_slug}")
    except Exception as e:
        print(f"  Scraper exception: {e}")
    finally:
        tmp_config.unlink(missing_ok=True)


def fetch_google_reviews(client_slug=None, **kwargs):
    """Read reviews from the scraper's SQLite database."""
    reviews = []

    if not SCRAPER_DB.exists():
        print("  No scraper database found. Run scraper first.")
        return reviews

    try:
        conn = sqlite3.connect(str(SCRAPER_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all reviews, optionally filtered by client via custom_params
        cursor.execute("""
            SELECT * FROM reviews
            ORDER BY review_date DESC
            LIMIT 200
        """)
        rows = cursor.fetchall()

        for row in rows:
            row_dict = dict(row)
            review_id = hashlib.md5(
                f"google_{row_dict.get('review_id', '')}_{row_dict.get('reviewer_name', '')}".encode()
            ).hexdigest()

            reviews.append({
                "id": review_id,
                "source": "google",
                "author": row_dict.get("reviewer_name", "Unknown"),
                "rating": row_dict.get("rating", 0),
                "text": row_dict.get("review_text", ""),
                "date": str(row_dict.get("review_date", ""))[:10],
                "iso_date": str(row_dict.get("review_date", "")),
                "response": row_dict.get("owner_response", "") or "",
                "fetched_at": datetime.now().isoformat(),
            })

        conn.close()
    except Exception as e:
        print(f"  Error reading scraper DB: {e}")

    return reviews


def fetch_trustpilot_reviews(domain):
    """Fetch reviews from Trustpilot's public API."""
    reviews = []

    # Find business unit ID
    url = f"https://www.trustpilot.com/api/consumersitejwt/business-units/find"
    params = {"name": domain}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            # Try alternative endpoint
            url = f"https://www.trustpilot.com/api/consumersitejwt/business-units/search"
            params = {"query": domain, "country": "US", "pageSize": 1}
            r = requests.get(url, params=params, headers=headers, timeout=10)

        data = r.json()
        business_id = None

        if isinstance(data, dict):
            business_id = data.get("id") or data.get("businessUnitId")
            if not business_id and data.get("businessUnits"):
                business_id = data["businessUnits"][0].get("id")

        if not business_id:
            print(f"Could not find Trustpilot business for: {domain}")
            return []

        # Fetch reviews
        url = f"https://www.trustpilot.com/api/consumersitejwt/business-units/{business_id}/reviews"
        params = {"perPage": 20, "page": 1}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()

        for rev in data.get("reviews", data.get("pageProps", {}).get("reviews", [])):
            review_id = hashlib.md5(
                f"tp_{rev.get('id', '')}_{rev.get('consumer', {}).get('displayName', '')}".encode()
            ).hexdigest()

            reviews.append({
                "id": review_id,
                "source": "trustpilot",
                "author": rev.get("consumer", {}).get("displayName", "Unknown"),
                "rating": rev.get("stars", rev.get("rating", 0)),
                "text": rev.get("text", rev.get("title", "")),
                "date": rev.get("createdAt", rev.get("dates", {}).get("publishedDate", ""))[:10],
                "iso_date": rev.get("createdAt", rev.get("dates", {}).get("publishedDate", "")),
                "response": "",
                "fetched_at": datetime.now().isoformat(),
            })

    except Exception as e:
        print(f"Trustpilot fetch error: {e}")

    return reviews


def fetch_yelp_reviews(business_name, location):
    """Fetch reviews from Yelp using Fusion API or SerpApi."""
    reviews = []
    yelp_key = os.environ.get("YELP_API_KEY", "")

    if yelp_key:
        # Search for business
        headers = {"Authorization": f"Bearer {yelp_key}"}
        url = "https://api.yelp.com/v3/businesses/search"
        params = {"term": business_name, "location": location, "limit": 1}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=10)
            businesses = r.json().get("businesses", [])
            if not businesses:
                return []

            biz_id = businesses[0]["id"]

            # Fetch reviews (Yelp API only returns 3, but it's a start)
            r = requests.get(
                f"https://api.yelp.com/v3/businesses/{biz_id}/reviews",
                headers=headers, params={"sort_by": "newest"}, timeout=10
            )
            for rev in r.json().get("reviews", []):
                review_id = hashlib.md5(f"yelp_{rev.get('id', '')}".encode()).hexdigest()
                reviews.append({
                    "id": review_id,
                    "source": "yelp",
                    "author": rev.get("user", {}).get("name", "Unknown"),
                    "rating": rev.get("rating", 0),
                    "text": rev.get("text", ""),
                    "date": rev.get("time_created", "")[:10],
                    "iso_date": rev.get("time_created", ""),
                    "response": "",
                    "fetched_at": datetime.now().isoformat(),
                })
        except Exception as e:
            print(f"Yelp API error: {e}")

    # SerpApi fallback for Yelp
    serpapi_key = os.environ.get("SERPAPI_KEY", "")
    if not reviews and serpapi_key:
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "yelp_reviews",
                "place_id": "",  # Would need to search first
                "api_key": serpapi_key,
            }
            # Search for place first
            search_params = {
                "engine": "yelp",
                "find_desc": business_name,
                "find_loc": location,
                "api_key": serpapi_key,
            }
            r = requests.get(url, params=search_params, timeout=10)
            results = r.json().get("organic_results", [])
            if results:
                place_id = results[0].get("place_ids", [""])[0]
                if place_id:
                    params["place_id"] = place_id
                    r = requests.get(url, params=params, timeout=10)
                    for rev in r.json().get("reviews", []):
                        review_id = hashlib.md5(
                            f"yelp_{rev.get('user', {}).get('name', '')}_{rev.get('date', '')}".encode()
                        ).hexdigest()
                        reviews.append({
                            "id": review_id,
                            "source": "yelp",
                            "author": rev.get("user", {}).get("name", "Unknown"),
                            "rating": rev.get("rating", 0),
                            "text": rev.get("comment", {}).get("text", ""),
                            "date": rev.get("date", ""),
                            "iso_date": rev.get("date", ""),
                            "response": "",
                            "fetched_at": datetime.now().isoformat(),
                        })
        except Exception as e:
            print(f"Yelp SerpApi error: {e}")

    return reviews


# --- Sentiment Analysis + Response Drafting ---

def classify_sentiment(review_text, rating):
    """Quick sentiment classification based on rating + keywords."""
    if rating <= 2:
        return "negative"
    elif rating == 3:
        # Check text for negative signals
        negative_words = ["disappointed", "terrible", "awful", "worst", "horrible",
                         "never", "waste", "broken", "scam", "fraud", "rude",
                         "unprofessional", "avoid", "disgusting", "unacceptable"]
        text_lower = review_text.lower()
        if any(w in text_lower for w in negative_words):
            return "negative"
        return "neutral"
    else:
        return "positive"


def draft_response(review, business_name):
    """Use Gemini to draft a professional response to a review."""
    if not GEMINI_API_KEY:
        return _draft_response_template(review, business_name)

    prompt = f"""You are a reputation management specialist. Draft a professional, empathetic response to this review for {business_name}.

Review ({review['rating']} stars) by {review['author']}:
"{review['text']}"

Rules:
- Be genuine and specific to what the reviewer said
- If negative: acknowledge the issue, apologize, offer to make it right, provide contact for follow-up
- If positive: thank them sincerely, mention something specific they said
- Keep it under 100 words
- Don't be generic or template-sounding
- Don't offer discounts or freebies (that attracts fake reviews)
- Sign off as the business, not as an AI

Draft the response:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
    }

    try:
        r = requests.post(url, json=payload, headers=headers, params=params, timeout=30)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _draft_response_template(review, business_name)


def _draft_response_template(review, business_name):
    """Fallback template-based response when API is unavailable."""
    if review["rating"] <= 2:
        return (f"Thank you for your feedback, {review['author']}. We're sorry to hear about your experience. "
                f"This isn't the standard we hold ourselves to at {business_name}. "
                f"We'd love the opportunity to make this right. Please reach out to us directly so we can address your concerns.")
    elif review["rating"] == 3:
        return (f"Thank you for your review, {review['author']}. We appreciate your honest feedback. "
                f"We're always looking to improve and would love to hear more about how we can earn that 5-star experience for you.")
    else:
        return (f"Thank you so much for the kind words, {review['author']}! "
                f"We're thrilled to hear you had a great experience with {business_name}. "
                f"We look forward to serving you again!")


# --- Alerting ---

def send_telegram_alert(message, topic_id=31):
    """Send alert via Telegram."""
    try:
        subprocess.run(
            ["/usr/bin/python3", "/root/.openclaw/workspace/lib/telegram.py",
             "--topic", str(topic_id), message],
            capture_output=True, timeout=30
        )
    except Exception as e:
        print(f"Telegram alert error: {e}")


def send_email_digest(subject, body, to_email=None):
    """Send digest via AgentMail."""
    api_key = os.environ.get("AGENTMAIL_API_KEY", "")
    if not api_key:
        print("No AGENTMAIL_API_KEY set, skipping email.")
        return

    # Get inbox ID
    try:
        r = requests.get(
            "https://api.agentmail.to/v0/inboxes",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        inboxes = r.json().get("inboxes", [])
        if not inboxes:
            print("No AgentMail inboxes found.")
            return

        inbox_id = inboxes[0]["id"]

        # Send email
        r = requests.post(
            f"https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "to": [{"email": to_email or "benjoselson@gmail.com"}],
                "subject": subject,
                "body": body,
            },
            timeout=10
        )
        print(f"Email sent: {r.status_code}")
    except Exception as e:
        print(f"Email error: {e}")


# --- Main Commands ---

def cmd_add_client(client_slug, client_name, client_email):
    """Register a new client."""
    mc = load_master_config()
    mc["clients"][client_slug] = {
        "name": client_name,
        "email": client_email,
        "slug": client_slug,
        "created_at": datetime.now().isoformat(),
        "active": True,
    }
    save_master_config(mc)
    get_client_dir(client_slug)  # Create directory
    print(f"Client registered: {client_name} ({client_slug}) -> {client_email}")


def cmd_list_clients():
    """List all configured clients."""
    mc = load_master_config()
    clients = mc.get("clients", {})
    if not clients:
        print("No clients configured. Use --add-client to add one.")
        return

    print(f"\n{'='*60}")
    print(f"REGISTERED CLIENTS ({len(clients)})")
    print(f"{'='*60}")
    for slug, info in clients.items():
        status = "ACTIVE" if info.get("active") else "PAUSED"
        cfg = load_config(slug)
        biz_name = cfg.get("business", {}).get("name", "Not set up")
        print(f"  [{status}] {slug}: {info['name']} ({info['email']})")
        print(f"         Business: {biz_name}")
    print()


def cmd_setup(business_name, location, client_slug, maps_url=None):
    """Set up monitoring for a business."""
    if not client_slug:
        client_slug = slugify(business_name)

    # Auto-register client if not exists
    mc = load_master_config()
    if client_slug not in mc.get("clients", {}):
        cmd_add_client(client_slug, business_name, "")

    config = load_config(client_slug)
    config["business"] = {
        "name": business_name,
        "address": location,
        "location": location,
        "maps_url": maps_url or "",
        "rating": 0,
        "total_reviews": 0,
    }
    config["setup_at"] = datetime.now().isoformat()
    save_config(config, client_slug)

    print(f"\nMonitoring set up for: {business_name}")
    print(f"Client: {client_slug}")
    print(f"Location: {location}")
    if maps_url:
        print(f"Google Maps URL: {maps_url}")
    else:
        print(f"NOTE: Add Google Maps URL with --maps-url for review scraping")
    print(f"Run: --check --client {client_slug}")


def cmd_check(client_slug):
    """Check for new reviews and process them."""
    config = load_config(client_slug)
    if not config.get("business"):
        print(f"No business configured for {client_slug}. Run --setup first.")
        return

    mc = load_master_config()
    client_info = mc.get("clients", {}).get(client_slug, {})
    biz = config["business"]
    db = load_reviews_db(client_slug)
    seen_ids = set(db.get("seen_ids", []))

    print(f"Checking reviews for: {biz['name']} (client: {client_slug})...")

    # Fetch from Google
    reviews = fetch_google_reviews(
        place_id=biz.get("place_id"),
        data_id=biz.get("data_id")
    )
    print(f"  Google: {len(reviews)} reviews fetched")

    # Fetch from Yelp
    yelp_reviews = fetch_yelp_reviews(biz["name"], biz.get("location", ""))
    reviews.extend(yelp_reviews)
    print(f"  Yelp: {len(yelp_reviews)} reviews fetched")

    # Fetch from Trustpilot if domain configured
    if config.get("trustpilot_domain"):
        tp_reviews = fetch_trustpilot_reviews(config["trustpilot_domain"])
        reviews.extend(tp_reviews)
        print(f"  Trustpilot: {len(tp_reviews)} reviews fetched")

    # Find new reviews
    new_reviews = [r for r in reviews if r["id"] not in seen_ids]
    negative_reviews = [r for r in new_reviews if classify_sentiment(r["text"], r["rating"]) == "negative"]

    print(f"\n  New reviews: {len(new_reviews)}")
    print(f"  Negative reviews: {len(negative_reviews)}")

    # Process ALL new reviews -- draft responses for negatives + neutrals
    for rev in new_reviews:
        sentiment = classify_sentiment(rev["text"], rev["rating"])
        if sentiment in ("negative", "neutral"):
            response = draft_response(rev, biz["name"])
            rev["drafted_response"] = response
            print(f"\n  --- {sentiment.upper()} REVIEW ({rev['rating']}*) ---")
            print(f"  Author: {rev['author']}")
            print(f"  Text: {rev['text'][:200]}")
            print(f"  Drafted response: {response[:150]}...")

    # Send alerts for negative reviews
    if negative_reviews:
        alert_msg = f"🚨 {len(negative_reviews)} new negative review(s) for {biz['name']}!\n\n"
        for rev in negative_reviews[:3]:
            alert_msg += f"{'⭐' * rev['rating']} by {rev['author']}\n"
            alert_msg += f'"{rev["text"][:150]}"\n\n'
            alert_msg += f"Drafted response:\n{rev.get('drafted_response', 'N/A')[:200]}\n\n---\n\n"
        send_telegram_alert(alert_msg)

    # Send digest email to client
    client_email = client_info.get("email", "")
    if new_reviews and client_email:
        subject = f"Review Alert: {biz['name']} - {len(new_reviews)} new reviews"
        body = _build_client_email(biz["name"], new_reviews, negative_reviews)
        send_email_digest(subject, body, to_email=client_email)

    # Update DB
    for rev in new_reviews:
        rev["sentiment"] = classify_sentiment(rev["text"], rev["rating"])
        db["reviews"].append(rev)
        db["seen_ids"].append(rev["id"])

    db["last_check"] = datetime.now().isoformat()
    save_reviews_db(db, client_slug)

    print(f"\nDone. {len(new_reviews)} new reviews processed. DB has {len(db['reviews'])} total.")
    return new_reviews, negative_reviews


def cmd_check_all():
    """Check reviews for all active clients."""
    mc = load_master_config()
    for slug, info in mc.get("clients", {}).items():
        if info.get("active", True):
            print(f"\n{'='*50}")
            cmd_check(slug)
    print(f"\nAll clients checked.")


def _build_client_email(business_name, new_reviews, negative_reviews):
    """Build a professional HTML email for the client."""
    neg_count = len(negative_reviews)
    pos_count = len([r for r in new_reviews if classify_sentiment(r["text"], r["rating"]) == "positive"])

    body = f"""REVIEW MONITOR ALERT - {datetime.now().strftime('%B %d, %Y')}
{'='*60}
Business: {business_name}
New Reviews Found: {len(new_reviews)}
Positive: {pos_count} | Negative: {neg_count}

"""
    if negative_reviews:
        body += "⚠️ NEGATIVE REVIEWS REQUIRING ATTENTION\n"
        body += "-" * 40 + "\n\n"
        for rev in negative_reviews:
            body += f"{'⭐' * rev['rating']} by {rev['author']} ({rev.get('source', 'google')}) - {rev['date']}\n"
            body += f'"{rev["text"]}"\n\n'
            if rev.get("drafted_response"):
                body += f"SUGGESTED RESPONSE (copy-paste ready):\n{rev['drafted_response']}\n\n"
            body += "-" * 20 + "\n\n"

    body += "\n---\nPowered by Review Monitor | Your AI reputation manager"
    return body


def cmd_digest(client_slug):
    """Generate and send a daily digest."""
    config = load_config(client_slug)
    if not config.get("business"):
        print(f"No business configured for {client_slug}. Run --setup first.")
        return

    mc = load_master_config()
    client_info = mc.get("clients", {}).get(client_slug, {})
    biz = config["business"]
    db = load_reviews_db(client_slug)

    # Get reviews from last 24 hours
    cutoff = (datetime.now() - timedelta(days=1)).isoformat()
    recent = [r for r in db["reviews"] if r.get("fetched_at", "") > cutoff]

    if not recent:
        print("No new reviews in the last 24 hours.")
        return

    # Build digest
    negative = [r for r in recent if r.get("sentiment") == "negative"]
    positive = [r for r in recent if r.get("sentiment") == "positive"]
    neutral = [r for r in recent if r.get("sentiment") == "neutral"]

    avg_rating = sum(r["rating"] for r in recent) / len(recent) if recent else 0

    subject = f"Daily Review Digest: {biz['name']} - {len(recent)} new reviews"

    body = f"""DAILY REVIEW DIGEST - {datetime.now().strftime('%B %d, %Y')}
{'='*60}
Business: {biz['name']}
New Reviews: {len(recent)}
Average Rating: {avg_rating:.1f}/5
Breakdown: {len(positive)} positive | {len(neutral)} neutral | {len(negative)} negative

"""

    if negative:
        body += "🚨 NEGATIVE REVIEWS (requires attention)\n"
        body += "-" * 40 + "\n\n"
        for rev in negative:
            body += f"{'⭐' * rev['rating']} by {rev['author']} ({rev['date']})\n"
            body += f'"{rev["text"]}"\n\n'
            if rev.get("drafted_response"):
                body += f"SUGGESTED RESPONSE:\n{rev['drafted_response']}\n\n"
            body += "-" * 20 + "\n\n"

    if positive:
        body += f"\n✅ POSITIVE REVIEWS ({len(positive)})\n"
        body += "-" * 40 + "\n\n"
        for rev in positive[:5]:  # Show top 5
            body += f"{'⭐' * rev['rating']} by {rev['author']}: \"{rev['text'][:100]}...\"\n\n"

    body += f"\n\nGenerated by Cortana Review Monitor"

    # Send via email to client
    client_email = client_info.get("email", "")
    send_email_digest(subject, body, to_email=client_email or None)

    # Also send summary to Telegram (internal)
    tg_msg = f"📊 Daily Digest: {biz['name']} ({client_slug})\n\n"
    tg_msg += f"New reviews: {len(recent)}\n"
    tg_msg += f"Avg rating: {avg_rating:.1f}/5\n"
    tg_msg += f"Breakdown: {len(positive)}✅ {len(neutral)}➖ {len(negative)}🚨\n"
    if negative:
        tg_msg += f"\n{len(negative)} negative review(s) need attention."

    send_telegram_alert(tg_msg)
    print(f"Digest sent: {len(recent)} reviews, {len(negative)} negative")


def cmd_digest_all():
    """Send digests for all active clients."""
    mc = load_master_config()
    for slug, info in mc.get("clients", {}).items():
        if info.get("active", True):
            print(f"\n{'='*50}")
            cmd_digest(slug)
    print(f"\nAll digests sent.")


def cmd_report(client_slug):
    """Print a quick status report."""
    config = load_config(client_slug)
    db = load_reviews_db(client_slug)

    if not config.get("business"):
        print(f"No business configured for {client_slug}.")
        return

    biz = config["business"]
    reviews = db.get("reviews", [])

    print(f"\n{'='*50}")
    print(f"REVIEW MONITOR STATUS")
    print(f"{'='*50}")
    print(f"Business: {biz['name']}")
    print(f"Address: {biz['address']}")
    print(f"Total tracked: {len(reviews)} reviews")
    print(f"Last check: {db.get('last_check', 'Never')}")

    if reviews:
        ratings = [r["rating"] for r in reviews]
        sentiments = [r.get("sentiment", "unknown") for r in reviews]
        print(f"Avg rating: {sum(ratings)/len(ratings):.1f}")
        print(f"Negative: {sentiments.count('negative')}")
        print(f"Neutral: {sentiments.count('neutral')}")
        print(f"Positive: {sentiments.count('positive')}")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review Monitor - AI-Powered Reputation Management")
    parser.add_argument("--client", type=str, help="Client slug identifier")
    parser.add_argument("--setup", nargs=2, metavar=("NAME", "LOCATION"),
                       help="Set up monitoring for a business")
    parser.add_argument("--check", action="store_true",
                       help="Check for new reviews")
    parser.add_argument("--check-all", action="store_true",
                       help="Check reviews for all clients")
    parser.add_argument("--digest", action="store_true",
                       help="Send daily digest")
    parser.add_argument("--digest-all", action="store_true",
                       help="Send digests for all clients")
    parser.add_argument("--report", action="store_true",
                       help="Print status report")
    parser.add_argument("--list-clients", action="store_true",
                       help="List all configured clients")
    parser.add_argument("--add-client", type=str, metavar="SLUG",
                       help="Register a new client")
    parser.add_argument("--email", type=str, help="Client email (with --add-client)")
    parser.add_argument("--name", type=str, help="Client display name (with --add-client)")
    parser.add_argument("--trustpilot", type=str,
                       help="Add Trustpilot domain to monitor")

    args = parser.parse_args()

    if args.list_clients:
        cmd_list_clients()
    elif args.add_client:
        cmd_add_client(args.add_client, args.name or args.add_client, args.email or "")
    elif args.setup:
        cmd_setup(args.setup[0], args.setup[1], args.client)
    elif args.check_all:
        cmd_check_all()
    elif args.check:
        if not args.client:
            print("ERROR: --client required. Use --check-all for all clients.")
            sys.exit(1)
        cmd_check(args.client)
    elif args.digest_all:
        cmd_digest_all()
    elif args.digest:
        if not args.client:
            print("ERROR: --client required. Use --digest-all for all clients.")
            sys.exit(1)
        cmd_digest(args.client)
    elif args.report:
        if not args.client:
            print("ERROR: --client required.")
            sys.exit(1)
        cmd_report(args.client)
    elif args.trustpilot:
        if not args.client:
            print("ERROR: --client required.")
            sys.exit(1)
        config = load_config(args.client)
        config["trustpilot_domain"] = args.trustpilot
        save_config(config, args.client)
        print(f"Added Trustpilot domain: {args.trustpilot}")
    else:
        parser.print_help()
