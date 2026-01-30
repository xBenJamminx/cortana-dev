#!/usr/bin/env python3
"""
Google Services Integration Module
Gmail, Calendar, YouTube API wrapper
"""
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json

class GoogleServices:
    def __init__(self):
        self.gmail_api_key = os.environ.get('GMAIL_API_KEY', '')
        self.calendar_api_key = os.environ.get('CALENDAR_API_KEY', '')
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY', '')
        
    def _make_request(self, url: str, method: str = 'GET', data: dict = None) -> dict:
        """Make authenticated request to Google API"""
        import requests
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    # Gmail Methods
    def gmail_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search Gmail messages"""
        # Note: Requires OAuth2, not just API key
        # For now, return placeholder
        return [{'note': 'Gmail requires OAuth2 setup - use browser automation or provide credentials'}]
    
    # Calendar Methods  
    def calendar_list_events(self, calendar_id: str = 'primary', days: int = 7) -> List[Dict]:
        """List calendar events for next N days"""
        # Note: Requires OAuth2
        return [{'note': 'Calendar requires OAuth2 setup'}]
    
    # YouTube Methods
    def youtube_get_channel_stats(self, channel_id: str = None) -> Dict:
        """Get YouTube channel statistics"""
        if not self.youtube_api_key:
            return {'error': 'YouTube API key not configured'}
        
        # If no channel_id provided, try to get authenticated user's channel
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&mine=true&key={self.youtube_api_key}"
        
        return self._make_request(url)
    
    def youtube_list_videos(self, channel_id: str = None, max_results: int = 10) -> List[Dict]:
        """List recent videos from channel"""
        if not self.youtube_api_key:
            return [{'error': 'YouTube API key not configured'}]
        
        # Get upload playlist for channel
        if channel_id:
            url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={self.youtube_api_key}"
            channel_data = self._make_request(url)
            
            if 'items' in channel_data and len(channel_data['items']) > 0:
                uploads_playlist = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Get videos from uploads playlist
                videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist}&maxResults={max_results}&key={self.youtube_api_key}"
                return self._make_request(videos_url).get('items', [])
        
        return []
    
    def youtube_get_video_stats(self, video_id: str) -> Dict:
        """Get statistics for specific video"""
        if not self.youtube_api_key:
            return {'error': 'YouTube API key not configured'}
        
        url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={self.youtube_api_key}"
        result = self._make_request(url)
        
        if 'items' in result and len(result['items']) > 0:
            return result['items'][0]
        return {'error': 'Video not found'}
    
    def youtube_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube videos"""
        if not self.youtube_api_key:
            return [{'error': 'YouTube API key not configured'}]
        
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&maxResults={max_results}&type=video&key={self.youtube_api_key}"
        return self._make_request(url).get('items', [])

# Convenience functions for direct use
def get_youtube_stats(channel_id: str = None) -> Dict:
    """Quick function to get YouTube channel stats"""
    gs = GoogleServices()
    return gs.youtube_get_channel_stats(channel_id)

def get_recent_videos(channel_id: str = None, max_results: int = 10) -> List[Dict]:
    """Quick function to list recent videos"""
    gs = GoogleServices()
    return gs.youtube_list_videos(channel_id, max_results)

def search_youtube(query: str, max_results: int = 10) -> List[Dict]:
    """Quick function to search YouTube"""
    gs = GoogleServices()
    return gs.youtube_search(query, max_results)

if __name__ == "__main__":
    # Test YouTube if API key is set
    if os.environ.get('YOUTUBE_API_KEY'):
        print("Testing YouTube API...")
        gs = GoogleServices()
        
        # Search for something
        results = gs.youtube_search("AI tutorials", 3)
        print(f"Found {len(results)} videos")
        for item in results:
            if 'snippet' in item:
                print(f"- {item['snippet']['title']}")
    else:
        print("YOUTUBE_API_KEY not set. Set it to test YouTube integration.")
