#!/usr/bin/env python3
"""
X/Twitter OAuth 2.0 PKCE Setup for @cortanaops account
"""
import os
import sys
import json
import hashlib
import base64
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
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

TOKEN_FILE = Path("/root/.config/x-oauth/cortana-tokens.json")
CLIENT_ID = os.environ.get("CORTANA_X_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CORTANA_X_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8990/callback"  # Different port for cortana
SCOPES = ["tweet.read", "users.read", "follows.read", "offline.access"]

AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

def generate_pkce():
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge

def save_tokens(tokens):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    tokens["saved_at"] = datetime.now().isoformat()
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"Tokens saved to {TOKEN_FILE}")

def load_tokens():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return None

def refresh_access_token(refresh_token):
    print("Refreshing access token...")
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30
    )
    if resp.status_code == 200:
        tokens = resp.json()
        save_tokens(tokens)
        print("Access token refreshed successfully")
        return tokens
    else:
        print(f"Refresh failed: {resp.status_code} - {resp.text}")
        return None

def test_token(access_token):
    print("Testing access token...")
    resp = requests.get(
        "https://api.twitter.com/2/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )
    if resp.status_code == 200:
        user = resp.json().get("data", {})
        print(f"Token valid! Logged in as @{user.get('username')} ({user.get('name')})")
        return True
    elif resp.status_code == 401:
        print("Token expired or invalid")
        return False
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
        return False

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            params = parse_qs(parsed.query)
            if "code" in params:
                self.server.auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this window.</p>")
            else:
                error = params.get("error", ["Unknown error"])[0]
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h1>Error: {error}</h1>".encode())
                self.server.auth_code = None
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def setup_oauth():
    print("Starting OAuth 2.0 PKCE setup for @cortanaops...")
    print(f"Client ID: {CLIENT_ID[:20]}...")
    
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(16)

    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"

    print(f"\nOpening browser for authorization...")
    print(f"If browser does not open, visit:\n{auth_url}\n")

    server = HTTPServer(("localhost", 8990), OAuthCallbackHandler)
    server.auth_code = None

    webbrowser.open(auth_url)

    print("Waiting for authorization...")
    while server.auth_code is None:
        server.handle_request()

    auth_code = server.auth_code
    print(f"Got authorization code: {auth_code[:20]}...")

    print("Exchanging code for tokens...")
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
            "client_id": CLIENT_ID,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30
    )

    if resp.status_code == 200:
        tokens = resp.json()
        save_tokens(tokens)
        print("\nOAuth setup complete!")
        print(f"Access token: {tokens.get('access_token', ''[:30]}...")
        print(f"Refresh token: {tokens.get('refresh_token', ''[:30]}...")
        print(f"Expires in: {tokens.get('expires_in')} seconds")
        return tokens
    else:
        print(f"\nToken exchange failed: {resp.status_code}")
        print(resp.text)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cortana-x-oauth-setup.py --setup|--refresh|--test")
        return

    cmd = sys.argv[1]

    if cmd == "--setup":
        setup_oauth()
    elif cmd == "--refresh":
        tokens = load_tokens()
        if tokens and "refresh_token" in tokens:
            refresh_access_token(tokens["refresh_token"])
        else:
            print("No refresh token found. Run --setup first.")
    elif cmd == "--test":
        tokens = load_tokens()
        if tokens and "access_token" in tokens:
            if not test_token(tokens["access_token"]):
                if "refresh_token" in tokens:
                    new_tokens = refresh_access_token(tokens["refresh_token"])
                    if new_tokens:
                        test_token(new_tokens["access_token"])
        else:
            print("No tokens found. Run --setup first.")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
