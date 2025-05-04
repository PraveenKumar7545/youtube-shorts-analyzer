import re

def is_shorts_url(url):
    """
    Check if a URL is a valid YouTube Shorts URL
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Check for standard YouTube Shorts URL format
    shorts_pattern = r'https?://(www\.)?youtube\.com/shorts/[a-zA-Z0-9_-]{11}(\?.*)?$'
    if re.match(shorts_pattern, url):
        return True
    
    # Check for YouTube URL that might be a Short
    youtube_pattern = r'https?://(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}(&.*)?$'
    if re.match(youtube_pattern, url):
        return True
    
    # Check for youtu.be short URL
    short_link_pattern = r'https?://(www\.)?youtu\.be/[a-zA-Z0-9_-]{11}(\?.*)?$'
    if re.match(short_link_pattern, url):
        return True
    
    return False

def extract_video_id(url):
    """
    Extract YouTube video ID from URL
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID
    """
    # Check for standard YouTube Shorts URL format
    shorts_match = re.match(r'https?://(www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})(\?.*)?$', url)
    if shorts_match:
        return shorts_match.group(2)
    
    # Check for standard YouTube URL
    watch_match = re.match(r'https?://(www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(&.*)?$', url)
    if watch_match:
        return watch_match.group(2)
    
    # Check for youtu.be short URL
    short_link_match = re.match(r'https?://(www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(\?.*)?$', url)
    if short_link_match:
        return short_link_match.group(2)
    
    return None

def format_number(num):
    """
    Format number for display (e.g., 1,234,567 -> 1.2M)
    
    Args:
        num (int): Number to format
        
    Returns:
        str: Formatted number
    """
    if num is None:
        return "0"
        
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    elif num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)
