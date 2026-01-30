#!/usr/bin/env python3
"""
Unified Social Media Report Generator
Pulls data from X/Twitter, YouTube, and TikTok (when available)
Generates weekly performance brief
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Config
REPORT_DIR = Path("/root/clawd/reports")
REPORT_DIR.mkdir(exist_ok=True)

def run_bird_command(cmd, auth_token=None, ct0=None):
    """Run bird CLI with auth"""
    env = os.environ.copy()
    if auth_token:
        env['AUTH_TOKEN'] = auth_token
        env['CT0'] = ct0
    
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, env=env, timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_x_analytics():
    """Fetch X/Twitter data via bird CLI"""
    auth_token = "REDACTED_TWITTER_AUTH_TOKEN"
    ct0 = "REDACTED_TWITTER_CT0"
    
    # Get recent tweets (last 7 days worth)
    stdout, stderr, rc = run_bird_command(
        "bird user-tweets @xBenJamminx -n 50 --json",
        auth_token, ct0
    )
    
    if rc != 0:
        print(f"  X API error: {stderr}")
        return {"error": f"Failed to fetch X data: {stderr}", "posts": []}
    
    try:
        data = json.loads(stdout) if stdout.strip() else {}
        # Handle both formats: direct list or {"tweets": [...]}
        if isinstance(data, list):
            tweets = data
        elif isinstance(data, dict) and 'tweets' in data:
            tweets = data['tweets']
        else:
            tweets = []
    except Exception as e:
        print(f"  X JSON parse error: {e}")
        tweets = []
    
    print(f"  Fetched {len(tweets)} tweets from X")
    
    # Process tweets from last 7 days
    cutoff = datetime.now() - timedelta(days=7)
    recent_posts = []
    
    for tweet in tweets:
        try:
            created = tweet.get('createdAt', '')
            if not created:
                continue
            
            # Parse Twitter timestamp
            tweet_time = datetime.strptime(created, '%a %b %d %H:%M:%S +0000 %Y')
            
            if tweet_time >= cutoff:
                recent_posts.append({
                    'date': tweet_time.strftime('%Y-%m-%d'),
                    'text': tweet.get('text', '')[:100] + '...' if len(tweet.get('text', '')) > 100 else tweet.get('text', ''),
                    'url': f"https://x.com/xBenJamminx/status/{tweet.get('id', '')}",
                    'likes': tweet.get('likeCount', 0),
                    'replies': tweet.get('replyCount', 0),
                    'retweets': tweet.get('retweetCount', 0),
                    'impressions': tweet.get('viewCount', 0) or 0
                })
        except Exception as e:
            continue
    
    print(f"  Found {len(recent_posts)} posts from last 7 days")
    
    # Calculate totals
    total_likes = sum(p['likes'] for p in recent_posts)
    total_replies = sum(p['replies'] for p in recent_posts)
    total_retweets = sum(p['retweets'] for p in recent_posts)
    total_impressions = sum(p['impressions'] for p in recent_posts)
    
    # Find best post
    best_post = max(recent_posts, key=lambda x: x['likes']) if recent_posts else None
    
    return {
        'platform': 'X (@xBenJamminx)',
        'period': 'Last 7 days',
        'total_posts': len(recent_posts),
        'total_likes': total_likes,
        'total_replies': total_replies,
        'total_retweets': total_retweets,
        'total_impressions': total_impressions,
        'avg_likes': round(total_likes / len(recent_posts), 1) if recent_posts else 0,
        'avg_impressions': round(total_impressions / len(recent_posts), 0) if recent_posts else 0,
        'best_post': best_post,
        'posts': recent_posts[:5]  # Top 5 for detail
    }

def get_youtube_analytics():
    """Fetch YouTube analytics via Google API"""
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        # Load credentials
        creds_path = Path("/root/.config/youtube/credentials.json")
        if not creds_path.exists():
            return {"error": "YouTube credentials not found", "videos": []}
        
        with open(creds_path) as f:
            creds_data = json.load(f)
        
        creds = Credentials(
            token=creds_data['access_token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret']
        )
        
        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Get channel info
        channels_response = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return {"error": "No YouTube channel found", "videos": []}
        
        channel = channels_response['items'][0]
        channel_stats = channel.get('statistics', {})
        
        # Get recent videos
        videos_response = youtube.search().list(
            part='snippet',
            channelId=channel['id'],
            order='date',
            type='video',
            maxResults=10
        ).execute()
        
        videos = []
        for item in videos_response.get('items', []):
            video_id = item['id']['videoId']
            
            # Get video stats
            video_stats = youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
            
            if video_stats.get('items'):
                stats = video_stats['items'][0]['statistics']
                snippet = video_stats['items'][0]['snippet']
                published = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                
                videos.append({
                    'title': snippet['title'],
                    'published': published.strftime('%Y-%m-%d'),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'url': f"https://youtube.com/watch?v={video_id}"
                })
        
        # Calculate totals from last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        recent_videos = [v for v in videos if datetime.strptime(v['published'], '%Y-%m-%d') >= cutoff]
        
        total_views = sum(v['views'] for v in videos)  # All recent videos views
        total_likes = sum(v['likes'] for v in videos)
        total_comments = sum(v['comments'] for v in videos)
        
        best_video = max(videos, key=lambda x: x['views']) if videos else None
        
        return {
            'platform': 'YouTube (Ben Jammin Builds)',
            'period': 'Recent uploads',
            'subscriber_count': int(channel_stats.get('subscriberCount', 0)),
            'total_views': int(channel_stats.get('viewCount', 0)),
            'video_count': int(channel_stats.get('videoCount', 0)),
            'recent_videos': len(recent_videos),
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_views': round(sum(v['views'] for v in videos) / len(videos), 0) if videos else 0,
            'best_video': best_video,
            'videos': videos[:5]
        }
        
    except Exception as e:
        return {"error": f"YouTube API error: {str(e)}", "videos": []}

def get_tiktok_analytics():
    """
    TikTok analytics - requires TikTok Creator/Business account API
    For now, returns template for manual entry or scraped data
    """
    # TikTok doesn't have a personal API - would need:
    # 1. TikTok Creator Portal API access
    # 2. Third-party service like Exolyt, Pentos, or Popsters
    # 3. Manual CSV export from TikTok analytics
    
    return {
        'platform': 'TikTok',
        'period': 'Last 7 days',
        'note': 'TikTok API requires Creator/Business account. Connect via Composio or export manually.',
        'manual_entry': True,
        'template': {
            'total_posts': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_shares': 0,
            'total_comments': 0,
            'follower_growth': 0,
            'avg_watch_time': '0s',
            'best_video': None
        }
    }

def generate_report():
    """Generate unified social media report"""
    
    print("📊 Generating Social Media Report...\n")
    
    # Fetch all platforms
    print("Fetching X/Twitter data...")
    x_data = get_x_analytics()
    
    print("Fetching YouTube data...")
    yt_data = get_youtube_analytics()
    
    print("Fetching TikTok data...")
    tt_data = get_tiktok_analytics()
    
    # Generate report markdown
    report_date = datetime.now().strftime('%Y-%m-%d')
    report_path = REPORT_DIR / f"social_report_{report_date}.md"
    
    report = f"""# 📊 Social Media Performance Report
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p ET')}  
**Period:** Last 7 days

---

## 🐦 X / Twitter (@xBenJamminx)

**Account Stats:**
- Posts: {x_data.get('total_posts', 0)}
- Total Likes: {x_data.get('total_likes', 0)}
- Total Replies: {x_data.get('total_replies', 0)}
- Total Retweets: {x_data.get('total_retweets', 0)}
- Total Impressions: {x_data.get('total_impressions', 0):,}
- Avg Likes/Post: {x_data.get('avg_likes', 0)}
- Avg Impressions: {x_data.get('avg_impressions', 0):,.0f}

**🏆 Best Performing Post:**
"""
    
    if x_data.get('best_post'):
        bp = x_data['best_post']
        report += f"""
> {bp['text']}
> 
> **{bp['likes']}** likes | **{bp['replies']}** replies | **{bp['retweets']}** retweets | **{bp['impressions']:,}** impressions
> 
> [View Post]({bp['url']})

**Recent Posts:**
"""
        for post in x_data.get('posts', []):
            report += f"""
- **{post['date']}**: {post['text'][:80]}...
  - {post['likes']} likes, {post['replies']} replies, {post['impressions']:,} impressions
"""
    else:
        report += "\n_No posts found in the last 7 days_\n"
    
    report += f"""

---

## 📺 YouTube (Ben Jammin Builds)

**Channel Stats:**
- Subscribers: {yt_data.get('subscriber_count', 0):,}
- Total Views: {yt_data.get('total_views', 0):,}
- Total Videos: {yt_data.get('video_count', 0)}
- Recent Uploads (7d): {yt_data.get('recent_videos', 0)}

**Recent Performance:**
- Total Likes: {yt_data.get('total_likes', 0)}
- Total Comments: {yt_data.get('total_comments', 0)}
- Avg Views/Video: {yt_data.get('avg_views', 0):,.0f}

"""
    
    if yt_data.get('best_video'):
        bv = yt_data['best_video']
        report += f"""**🏆 Best Recent Video:**
> **{bv['title']}**
> 
> {bv['views']:,} views | {bv['likes']:,} likes | {bv['comments']:,} comments
> 
> [Watch]({bv['url']})

**Recent Videos:**
"""
        for video in yt_data.get('videos', []):
            report += f"""
- **{video['published']}**: {video['title'][:60]}...
  - {video['views']:,} views, {video['likes']:,} likes
"""
    else:
        report += "\n_No recent videos found_\n"
    
    if yt_data.get('error'):
        report += f"\n⚠️ **Note:** {yt_data['error']}\n"
    
    report += f"""

---

## 🎵 TikTok

**Status:** {tt_data.get('note', 'Not connected')}

{'' if not tt_data.get('manual_entry') else '''
To add TikTok data:
1. Export analytics from TikTok Creator Tools (7-day CSV)
2. Save to `/root/clawd/reports/tiktok_data.csv`
3. Re-run this report

**Or** connect via Composio once you have Creator account API access.
'''}"""
    
    report += f"""

---

## 📈 Cross-Platform Insights

### Content Themes That Worked:
[Analyze and fill in based on best performing posts]

### Audience Growth:
- X: [Track follower growth manually or via API]
- YouTube: {yt_data.get('subscriber_count', 0):,} subscribers
- TikTok: [Add when connected]

### Recommendations for Next Week:
1. [Based on top-performing content themes]
2. [Optimal posting times analysis]
3. [Content gaps/opportunities]

### Priority Actions:
- [ ] 
- [ ] 
- [ ] 

---

*Report generated by Cortana* 💜
"""
    
    # Save report
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")
    
    # Print summary to console
    print("\n" + "="*50)
    print("QUICK SUMMARY")
    print("="*50)
    print(f"\n🐦 X: {x_data.get('total_posts', 0)} posts, {x_data.get('total_likes', 0)} likes, {x_data.get('total_impressions', 0):,} impressions")
    print(f"📺 YouTube: {yt_data.get('recent_videos', 0)} recent videos, {yt_data.get('subscriber_count', 0):,} subs")
    print(f"🎵 TikTok: {tt_data.get('note', 'Not connected')}")
    
    return report_path

if __name__ == "__main__":
    generate_report()
