import os
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime, timedelta
import random
import re
from dotenv import load_dotenv
load_dotenv()
# Setup API client
def get_youtube_api():
    """Initialize the YouTube API client."""
    api_key = os.getenv("YOUTUBE_API_KEY", "")
    if not api_key:
        raise ValueError("YouTube API key not found. Please set the YOUTUBE_API_KEY environment variable.")
    
    api_service_name = "youtube"
    api_version = "v3"
    
    return googleapiclient.discovery.build(
        api_service_name, 
        api_version, 
        developerKey=api_key
    )

def get_video_data(video_id):
    """
    Fetch metadata for a specific YouTube video
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        dict: Video metadata
    """
    try:
        youtube = get_youtube_api()
        
        # Get video details
        video_response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
        
        if not video_response['items']:
            return None
        
        video_info = video_response['items'][0]
        
        # Extract relevant data
        video_data = {
            'video_id': video_id,
            'title': video_info['snippet']['title'],
            'description': video_info['snippet']['description'],
            'published_at': video_info['snippet']['publishedAt'],
            'channel_id': video_info['snippet']['channelId'],
            'channel_title': video_info['snippet']['channelTitle'],
            'tags': video_info['snippet'].get('tags', []),
            'category_id': video_info['snippet']['categoryId'],
            'thumbnail_url': video_info['snippet']['thumbnails']['high']['url'] if 'high' in video_info['snippet']['thumbnails'] else video_info['snippet']['thumbnails']['default']['url'],
            'duration': video_info['contentDetails']['duration'],
            'view_count': int(video_info['statistics'].get('viewCount', 0)),
            'like_count': int(video_info['statistics'].get('likeCount', 0)),
            'comment_count': int(video_info['statistics'].get('commentCount', 0)),
            'is_shorts': is_shorts(video_info)
        }
        
        return video_data
        
    except googleapiclient.errors.HttpError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching video data: {e}")
        return None

def get_trending_shorts(max_results=20):
    """
    Fetch metadata for trending YouTube Shorts
    
    Args:
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of video metadata
    """
    try:
        youtube = get_youtube_api()
        
        # Search for trending shorts
        # Note: YouTube API doesn't have a direct "shorts" filter, so we'll use workarounds
        search_response = youtube.search().list(
            part="id",
            maxResults=max_results * 2,  # Fetch more to filter down to actual shorts
            type="video",
            videoDuration="short",  # Short videos (<4 minutes)
            order="viewCount",
            publishedAfter=(datetime.now() - timedelta(days=14)).isoformat() + "Z",  # Last 2 weeks
            relevanceLanguage="en"
        ).execute()
        
        if not search_response.get('items', []):
            return []
            
        # Get video IDs
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        # Get details for these videos
        videos_response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(video_ids)
        ).execute()
        
        # Filter to actual shorts
        shorts_data = []
        for video in videos_response.get('items', []):
            if is_shorts(video) and len(shorts_data) < max_results:
                shorts_data.append({
                    'video_id': video['id'],
                    'title': video['snippet']['title'],
                    'channel_title': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': int(video['statistics'].get('viewCount', 0)),
                    'like_count': int(video['statistics'].get('likeCount', 0)),
                    'comment_count': int(video['statistics'].get('commentCount', 0)),
                    'tags': video['snippet'].get('tags', []),
                })
        
        return shorts_data
        
    except googleapiclient.errors.HttpError as e:
        print(f"HTTP Error when fetching trending shorts: {e}")
        return []
    except Exception as e:
        print(f"Error fetching trending shorts: {e}")
        return []

def is_shorts(video_info):
    """
    Determine if a video is a YouTube Short
    
    Args:
        video_info (dict): Video information from YouTube API
        
    Returns:
        bool: True if the video is a Short, False otherwise
    """
    # Check if duration is less than 60 seconds
    duration = video_info['contentDetails']['duration']
    duration_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if duration_match:
        hours = int(duration_match.group(1) or 0)
        minutes = int(duration_match.group(2) or 0)
        seconds = int(duration_match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        # YouTube Shorts are typically vertical (aspect ratio > 1) and less than 60 seconds
        if total_seconds <= 60:
            return True
    
    # Sometimes, video description or title mentions #Shorts
    if '#shorts' in video_info['snippet'].get('description', '').lower() or '#shorts' in video_info['snippet']['title'].lower():
        return True
        
    return False
