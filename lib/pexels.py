"""Pexels API client for fetching free stock images and videos."""

import json
import os
import urllib.request
import urllib.parse

API_BASE = "https://api.pexels.com"


def _get_key():
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        from dotenv import load_dotenv
        load_dotenv("/root/.openclaw/.env")
        key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        with open("/root/.openclaw/.env") as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    break
    return key


def _request(endpoint, params=None):
    key = _get_key()
    if not key:
        raise RuntimeError("PEXELS_API_KEY not found")
    url = f"{API_BASE}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": key,
        "User-Agent": "Mozilla/5.0 CortanaBot/1.0",
    })
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())


def search_photos(query, per_page=10, orientation="portrait", size="medium"):
    """Search for stock photos. Returns list of photo dicts with download URLs."""
    params = {"query": query, "per_page": per_page, "orientation": orientation, "size": size}
    data = _request("/v1/search", params)
    return [
        {
            "id": p["id"],
            "url_original": p["src"]["original"],
            "url_large2x": p["src"]["large2x"],
            "url_large": p["src"]["large"],
            "url_medium": p["src"]["medium"],
            "url_portrait": p["src"]["portrait"],
            "width": p["width"],
            "height": p["height"],
            "alt": p.get("alt", ""),
            "photographer": p.get("photographer", ""),
        }
        for p in data.get("photos", [])
    ]


def search_videos(query, per_page=10, orientation="portrait", size="medium"):
    """Search for stock videos. Returns list of video dicts with download URLs."""
    params = {"query": query, "per_page": per_page, "orientation": orientation, "size": size}
    data = _request("/videos/search", params)
    results = []
    for v in data.get("videos", []):
        # Get the best video file (prefer HD, portrait)
        files = v.get("video_files", [])
        best = None
        for f in files:
            if f.get("quality") == "hd":
                best = f
                break
        if not best and files:
            best = files[0]
        results.append({
            "id": v["id"],
            "url": best["link"] if best else None,
            "width": best.get("width") if best else None,
            "height": best.get("height") if best else None,
            "duration": v.get("duration"),
            "image": v.get("image"),  # thumbnail
        })
    return results


def download_file(url, output_path):
    """Download a file from URL to local path."""
    req = urllib.request.Request(url, headers={
        "Authorization": _get_key(),
        "User-Agent": "Mozilla/5.0 CortanaBot/1.0",
    })
    resp = urllib.request.urlopen(req, timeout=120)
    with open(output_path, "wb") as f:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            f.write(chunk)
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pexels.py <search query> [video|photo]")
        sys.exit(1)
    query = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "photo"
    if mode == "video":
        results = search_videos(query, per_page=3)
    else:
        results = search_photos(query, per_page=3)
    print(json.dumps(results, indent=2))
