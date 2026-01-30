import urllib.parse

CLIENT_ID = "1065692947130-821rth5vjk1nb1onhbulu5o8pjihgvkt.apps.googleusercontent.com"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": " ".join(SCOPES),
    "response_type": "code",
    "access_type": "offline"
}

url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
print(url)
