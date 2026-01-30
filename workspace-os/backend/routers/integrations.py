"""
Real Integrations Router v2 - Multi-account Twitter, YouTube, Notion, Gmail
Pulls ALL available data from connected services
"""
import os
import json
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import base64
import hashlib
import hmac
import time
import urllib.parse

router = APIRouter()

# Load environment
def load_env():
    env = {}
    env_files = ['/root/.clawdbot/.env', '/root/.clawdbot/.env.notion', '/root/.clawdbot/.env.google', '/root/.clawdbot/.env.slack']
    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value
    return env

ENV = load_env()

# ============ TWITTER OAUTH HELPERS ============

def get_twitter_oauth_header(method: str, url: str, params: dict = None):
    """Generate OAuth 1.0a header for Twitter API"""
    oauth_consumer_key = ENV.get('X_API_KEY') or ENV.get('TWITTER_API_KEY')
    oauth_consumer_secret = ENV.get('X_API_SECRET') or ENV.get('TWITTER_API_SECRET')
    oauth_token = ENV.get('X_ACCESS_TOKEN') or ENV.get('TWITTER_ACCESS_TOKEN')
    oauth_token_secret = ENV.get('X_ACCESS_TOKEN_SECRET') or ENV.get('TWITTER_ACCESS_TOKEN_SECRET')

    if not all([oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_token_secret]):
        return None

    oauth_nonce = base64.b64encode(os.urandom(32)).decode('utf-8').replace('+', '').replace('/', '').replace('=', '')[:32]
    oauth_timestamp = str(int(time.time()))

    oauth_params = {
        'oauth_consumer_key': oauth_consumer_key,
        'oauth_nonce': oauth_nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': oauth_timestamp,
        'oauth_token': oauth_token,
        'oauth_version': '1.0'
    }

    all_params = {**oauth_params}
    if params:
        all_params.update(params)

    sorted_params = sorted(all_params.items())
    param_string = '&'.join([f"{urllib.parse.quote(str(k), safe='')}" + "=" + f"{urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])

    base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"

    signing_key = f"{urllib.parse.quote(oauth_consumer_secret, safe='')}&{urllib.parse.quote(oauth_token_secret, safe='')}"
    signature = base64.b64encode(hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()).decode()

    oauth_params['oauth_signature'] = signature

    header = 'OAuth ' + ', '.join([f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(oauth_params.items())])
    return header

def get_bearer_token():
    """Get bearer token for app-only auth"""
    return ENV.get('X_BEARER_TOKEN')

# ============ TWITTER - CORTANA'S ACCOUNT (@0xBenJammin) ============

@router.get('/twitter/cortana')
async def get_cortana_twitter():
    """Get Cortana's Twitter account (@0xBenJammin) - full data"""
    url = 'https://api.twitter.com/2/users/me'
    params = {
        'user.fields': 'public_metrics,description,profile_image_url,created_at,location,url,verified,pinned_tweet_id'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)
    if not auth_header:
        return {'error': 'Twitter not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            data = resp.json()
            data['account_type'] = 'cortana'
            return data
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/cortana/tweets')
async def get_cortana_tweets(limit: int = 50):
    """Get Cortana's tweets with full metrics"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    if not user_id:
        return {'error': 'Could not get user ID'}

    url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    params = {
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,text,conversation_id,in_reply_to_user_id,referenced_tweets,entities',
        'expansions': 'attachments.media_keys,referenced_tweets.id',
        'media.fields': 'url,preview_image_url,type'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            data = resp.json()
            tweets = data.get('data', [])
            # Calculate engagement score and sort
            for tweet in tweets:
                metrics = tweet.get('public_metrics', {})
                tweet['engagement_score'] = (
                    metrics.get('like_count', 0) * 3 +
                    metrics.get('retweet_count', 0) * 5 +
                    metrics.get('reply_count', 0) * 2 +
                    metrics.get('quote_count', 0) * 4 +
                    metrics.get('impression_count', 0) * 0.01
                )
            tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
            return {'tweets': tweets, 'user': me.get('data'), 'includes': data.get('includes', {})}
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/cortana/mentions')
async def get_cortana_mentions(limit: int = 50):
    """Get mentions of Cortana's account"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/mentions'
    params = {
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,text,author_id,conversation_id',
        'expansions': 'author_id',
        'user.fields': 'name,username,profile_image_url,public_metrics'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/cortana/likes')
async def get_cortana_likes(limit: int = 50):
    """Get tweets Cortana has liked"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/liked_tweets'
    params = {
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,text,author_id',
        'expansions': 'author_id',
        'user.fields': 'name,username,profile_image_url'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/cortana/following')
async def get_cortana_following(limit: int = 100):
    """Get accounts Cortana follows"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/following'
    params = {
        'max_results': min(limit, 1000),
        'user.fields': 'public_metrics,description,profile_image_url'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/cortana/followers')
async def get_cortana_followers(limit: int = 100):
    """Get Cortana's followers"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/followers'
    params = {
        'max_results': min(limit, 1000),
        'user.fields': 'public_metrics,description,profile_image_url'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

# ============ TWITTER - BEN'S ACCOUNT (@xBenJamminx) - PUBLIC DATA ============

@router.get('/twitter/ben')
async def get_ben_twitter():
    """Get Ben's Twitter account (@xBenJamminx) - public data via username lookup"""
    bearer = get_bearer_token()
    if not bearer:
        # Fall back to OAuth
        url = 'https://api.twitter.com/2/users/by/username/xBenJamminx'
        params = {
            'user.fields': 'public_metrics,description,profile_image_url,created_at,location,url,verified,pinned_tweet_id'
        }
        auth_header = get_twitter_oauth_header('GET', url, params)
        if not auth_header:
            return {'error': 'Twitter not configured'}

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers={'Authorization': auth_header})
            if resp.status_code == 200:
                data = resp.json()
                data['account_type'] = 'ben'
                return data
            return {'error': resp.text, 'status': resp.status_code}
    else:
        url = 'https://api.twitter.com/2/users/by/username/xBenJamminx'
        params = {
            'user.fields': 'public_metrics,description,profile_image_url,created_at,location,url,verified,pinned_tweet_id'
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers={'Authorization': f'Bearer {bearer}'})
            if resp.status_code == 200:
                data = resp.json()
                data['account_type'] = 'ben'
                return data
            return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/ben/tweets')
async def get_ben_tweets(limit: int = 50):
    """Get Ben's recent tweets"""
    ben = await get_ben_twitter()
    if 'error' in ben:
        return ben

    user_id = ben.get('data', {}).get('id')
    if not user_id:
        return {'error': 'Could not get user ID'}

    url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    params = {
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,text,conversation_id,entities',
        'expansions': 'attachments.media_keys',
        'media.fields': 'url,preview_image_url,type'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            data = resp.json()
            tweets = data.get('data', [])
            for tweet in tweets:
                metrics = tweet.get('public_metrics', {})
                tweet['engagement_score'] = (
                    metrics.get('like_count', 0) * 3 +
                    metrics.get('retweet_count', 0) * 5 +
                    metrics.get('reply_count', 0) * 2 +
                    metrics.get('impression_count', 0) * 0.01
                )
            tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
            return {'tweets': tweets, 'user': ben.get('data'), 'includes': data.get('includes', {})}
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/twitter/ben/mentions')
async def get_ben_mentions(limit: int = 50):
    """Get mentions of Ben's account"""
    ben = await get_ben_twitter()
    if 'error' in ben:
        return ben

    user_id = ben.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/mentions'
    params = {
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,text,author_id',
        'expansions': 'author_id',
        'user.fields': 'name,username,profile_image_url'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

# ============ TWITTER - COMBINED DASHBOARD ============

@router.get('/twitter/all')
async def get_all_twitter_accounts():
    """Get both Twitter accounts with all data"""
    cortana = await get_cortana_twitter()
    ben = await get_ben_twitter()

    return {
        'cortana': cortana.get('data') if 'data' in cortana else cortana,
        'ben': ben.get('data') if 'data' in ben else ben,
        'timestamp': datetime.utcnow().isoformat()
    }

# ============ TWITTER ACTIONS ============

class TweetPost(BaseModel):
    text: str
    reply_to: Optional[str] = None
    quote_tweet_id: Optional[str] = None

@router.post('/twitter/tweet')
async def post_tweet(tweet: TweetPost):
    """Post a new tweet from Cortana's account"""
    url = 'https://api.twitter.com/2/tweets'

    payload = {'text': tweet.text}
    if tweet.reply_to:
        payload['reply'] = {'in_reply_to_tweet_id': tweet.reply_to}
    if tweet.quote_tweet_id:
        payload['quote_tweet_id'] = tweet.quote_tweet_id

    auth_header = get_twitter_oauth_header('POST', url)
    if not auth_header:
        return {'error': 'Twitter not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers={
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        })
        return resp.json()

@router.post('/twitter/like/{tweet_id}')
async def like_tweet(tweet_id: str):
    """Like a tweet"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/likes'

    auth_header = get_twitter_oauth_header('POST', url)

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={'tweet_id': tweet_id}, headers={
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        })
        return resp.json()

@router.post('/twitter/retweet/{tweet_id}')
async def retweet(tweet_id: str):
    """Retweet a tweet"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    user_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{user_id}/retweets'

    auth_header = get_twitter_oauth_header('POST', url)

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={'tweet_id': tweet_id}, headers={
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        })
        return resp.json()

@router.post('/twitter/follow/{user_id}')
async def follow_user(user_id: str):
    """Follow a user"""
    me = await get_cortana_twitter()
    if 'error' in me:
        return me

    my_id = me.get('data', {}).get('id')
    url = f'https://api.twitter.com/2/users/{my_id}/following'

    auth_header = get_twitter_oauth_header('POST', url)

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={'target_user_id': user_id}, headers={
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        })
        return resp.json()

# ============ TWITTER SEARCH ============

@router.get('/twitter/search')
async def search_twitter(query: str, limit: int = 20):
    """Search recent tweets"""
    url = 'https://api.twitter.com/2/tweets/search/recent'
    params = {
        'query': query,
        'max_results': min(limit, 100),
        'tweet.fields': 'public_metrics,created_at,author_id',
        'expansions': 'author_id',
        'user.fields': 'name,username,profile_image_url,public_metrics'
    }

    auth_header = get_twitter_oauth_header('GET', url, params)

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers={'Authorization': auth_header})
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

# ============ YOUTUBE ============

@router.get('/youtube/channel/{channel_handle}')
async def get_youtube_channel(channel_handle: str = 'benjamminbuilds'):
    """Get YouTube channel by handle"""
    api_key = ENV.get('YOUTUBE_API_KEY') or ENV.get('GOOGLE_API_KEY')
    if not api_key:
        return {'error': 'YouTube API key not configured'}

    async with httpx.AsyncClient() as client:
        # Search for channel by handle
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        search_params = {
            'part': 'snippet',
            'q': channel_handle,
            'type': 'channel',
            'key': api_key
        }
        search_resp = await client.get(search_url, params=search_params)

        if search_resp.status_code == 200:
            search_data = search_resp.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']

                # Get full channel details
                channel_url = 'https://www.googleapis.com/youtube/v3/channels'
                channel_params = {
                    'part': 'statistics,snippet,contentDetails,brandingSettings',
                    'id': channel_id,
                    'key': api_key
                }
                channel_resp = await client.get(channel_url, params=channel_params)
                if channel_resp.status_code == 200:
                    return channel_resp.json()

        return {'error': 'Channel not found'}

@router.get('/youtube/videos')
async def get_youtube_videos(limit: int = 20):
    """Get recent YouTube videos with full analytics"""
    api_key = ENV.get('YOUTUBE_API_KEY') or ENV.get('GOOGLE_API_KEY')
    if not api_key:
        return {'error': 'YouTube API key not configured'}

    # First find the channel
    channel_data = await get_youtube_channel('benjamminbuilds')
    if 'error' in channel_data:
        return channel_data

    if not channel_data.get('items'):
        return {'error': 'Channel not found'}

    channel = channel_data['items'][0]
    uploads_playlist = channel['contentDetails']['relatedPlaylists']['uploads']

    async with httpx.AsyncClient() as client:
        # Get videos from uploads playlist
        playlist_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        playlist_params = {
            'part': 'snippet,contentDetails',
            'playlistId': uploads_playlist,
            'maxResults': limit,
            'key': api_key
        }
        playlist_resp = await client.get(playlist_url, params=playlist_params)

        if playlist_resp.status_code != 200:
            return {'error': 'Could not get videos'}

        videos = playlist_resp.json().get('items', [])
        video_ids = [v['contentDetails']['videoId'] for v in videos]

        if not video_ids:
            return {'videos': [], 'channel': channel}

        # Get video statistics
        stats_url = 'https://www.googleapis.com/youtube/v3/videos'
        stats_params = {
            'part': 'statistics,snippet,contentDetails',
            'id': ','.join(video_ids),
            'key': api_key
        }
        stats_resp = await client.get(stats_url, params=stats_params)

        if stats_resp.status_code == 200:
            video_data = stats_resp.json().get('items', [])
            # Sort by views
            video_data.sort(key=lambda x: int(x.get('statistics', {}).get('viewCount', 0)), reverse=True)
            return {'videos': video_data, 'channel': channel}

        return {'error': stats_resp.text}

@router.get('/youtube/comments/{video_id}')
async def get_youtube_comments(video_id: str, limit: int = 50):
    """Get comments on a YouTube video"""
    api_key = ENV.get('YOUTUBE_API_KEY') or ENV.get('GOOGLE_API_KEY')
    if not api_key:
        return {'error': 'YouTube API key not configured'}

    async with httpx.AsyncClient() as client:
        url = 'https://www.googleapis.com/youtube/v3/commentThreads'
        params = {
            'part': 'snippet,replies',
            'videoId': video_id,
            'maxResults': limit,
            'order': 'relevance',
            'key': api_key
        }
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

# ============ NOTION ============

@router.get('/notion/databases')
async def list_notion_databases():
    """List all Notion databases"""
    api_key = ENV.get('NOTION_API_KEY')
    if not api_key:
        return {'error': 'Notion not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://api.notion.com/v1/search',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            },
            json={'filter': {'property': 'object', 'value': 'database'}}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/notion/pages')
async def list_notion_pages(limit: int = 50):
    """List recent Notion pages"""
    api_key = ENV.get('NOTION_API_KEY')
    if not api_key:
        return {'error': 'Notion not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://api.notion.com/v1/search',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            },
            json={
                'filter': {'property': 'object', 'value': 'page'},
                'page_size': limit,
                'sort': {'direction': 'descending', 'timestamp': 'last_edited_time'}
            }
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/notion/database/{database_id}')
async def query_notion_database(database_id: str, limit: int = 100):
    """Query a specific Notion database"""
    api_key = ENV.get('NOTION_API_KEY')
    if not api_key:
        return {'error': 'Notion not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f'https://api.notion.com/v1/databases/{database_id}/query',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            },
            json={'page_size': limit}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

# ============ SLACK ============

@router.get('/slack/channels')
async def list_slack_channels():
    """List Slack channels"""
    token = ENV.get('SLACK_TOKEN') or ENV.get('SLACK_BOT_TOKEN')
    if not token:
        return {'error': 'Slack not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://slack.com/api/conversations.list',
            headers={'Authorization': f'Bearer {token}'},
            params={'types': 'public_channel,private_channel,im,mpim', 'limit': 100}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/slack/messages/{channel_id}')
async def get_slack_messages(channel_id: str, limit: int = 50):
    """Get messages from a Slack channel"""
    token = ENV.get('SLACK_TOKEN') or ENV.get('SLACK_BOT_TOKEN')
    if not token:
        return {'error': 'Slack not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://slack.com/api/conversations.history',
            headers={'Authorization': f'Bearer {token}'},
            params={'channel': channel_id, 'limit': limit}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/slack/users')
async def list_slack_users():
    """List Slack workspace users"""
    token = ENV.get('SLACK_TOKEN') or ENV.get('SLACK_BOT_TOKEN')
    if not token:
        return {'error': 'Slack not configured'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://slack.com/api/users.list',
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

# ============ AGGREGATED DASHBOARD ============

@router.get('/dashboard')
async def get_full_integrations_dashboard():
    """Get comprehensive dashboard data from ALL integrations"""
    dashboard = {
        'twitter': {
            'cortana': None,
            'ben': None
        },
        'youtube': None,
        'notion': None,
        'slack': None,
        'timestamp': datetime.utcnow().isoformat()
    }

    # Twitter - Both accounts
    try:
        cortana = await get_cortana_twitter()
        if 'data' in cortana:
            dashboard['twitter']['cortana'] = cortana['data']
    except Exception as e:
        dashboard['twitter']['cortana'] = {'error': str(e)}

    try:
        ben = await get_ben_twitter()
        if 'data' in ben:
            dashboard['twitter']['ben'] = ben['data']
    except Exception as e:
        dashboard['twitter']['ben'] = {'error': str(e)}

    # YouTube
    try:
        yt = await get_youtube_channel('benjamminbuilds')
        if 'items' in yt and len(yt['items']) > 0:
            channel = yt['items'][0]
            stats = channel.get('statistics', {})
            dashboard['youtube'] = {
                'title': channel.get('snippet', {}).get('title'),
                'subscribers': int(stats.get('subscriberCount', 0)),
                'views': int(stats.get('viewCount', 0)),
                'videos': int(stats.get('videoCount', 0)),
                'thumbnail': channel.get('snippet', {}).get('thumbnails', {}).get('default', {}).get('url')
            }
    except Exception as e:
        dashboard['youtube'] = {'error': str(e)}

    # Notion
    if ENV.get('NOTION_API_KEY'):
        try:
            notion = await list_notion_databases()
            if 'results' in notion:
                dashboard['notion'] = {
                    'databases': len(notion['results']),
                    'status': 'connected'
                }
        except:
            dashboard['notion'] = {'status': 'error'}

    # Slack
    if ENV.get('SLACK_TOKEN') or ENV.get('SLACK_BOT_TOKEN'):
        try:
            slack = await list_slack_channels()
            if slack.get('ok'):
                dashboard['slack'] = {
                    'channels': len(slack.get('channels', [])),
                    'status': 'connected'
                }
        except:
            dashboard['slack'] = {'status': 'error'}

    return dashboard

# Legacy endpoint for backwards compatibility
@router.get('/twitter/me')
async def get_twitter_me():
    """Legacy endpoint - returns Cortana's account"""
    return await get_cortana_twitter()

@router.get('/twitter/tweets')
async def get_my_tweets(limit: int = 10):
    """Legacy endpoint - returns Cortana's tweets"""
    return await get_cortana_tweets(limit)

@router.get('/twitter/mentions')
async def get_twitter_mentions(limit: int = 20):
    """Legacy endpoint - returns Cortana's mentions"""
    return await get_cortana_mentions(limit)
