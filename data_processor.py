import re
from datetime import datetime
import pandas as pd
import numpy as np

def process_video_data(video_data):
    """
    Process raw video data from YouTube API
    
    Args:
        video_data (dict): Raw video data
        
    Returns:
        dict: Processed video data with additional metrics
    """
    processed_data = video_data.copy()
    
    # Clean title (remove emoji, extra spaces, etc.)
    processed_data['clean_title'] = clean_text(video_data['title'])
    
    # Extract title features
    processed_data['title_length'] = len(video_data['title'])
    processed_data['title_word_count'] = len(video_data['title'].split())
    processed_data['has_question_in_title'] = '?' in video_data['title']
    processed_data['has_exclamation_in_title'] = '!' in video_data['title']
    processed_data['has_number_in_title'] = any(char.isdigit() for char in video_data['title'])
    processed_data['has_emoji_in_title'] = contains_emoji(video_data['title'])
    
    # Extract tag features
    processed_data['tag_count'] = len(video_data['tags']) if video_data['tags'] else 0
    processed_data['total_tag_length'] = sum(len(tag) for tag in video_data['tags']) if video_data['tags'] else 0
    processed_data['avg_tag_length'] = processed_data['total_tag_length'] / max(1, processed_data['tag_count'])
    
    # Calculate engagement metrics
    processed_data['like_view_ratio'] = processed_data['like_count'] / max(1, processed_data['view_count'])
    processed_data['comment_view_ratio'] = processed_data['comment_count'] / max(1, processed_data['view_count'])
    
    # Calculate time-based metrics
    published_date = datetime.strptime(video_data['published_at'], "%Y-%m-%dT%H:%M:%SZ")
    days_live = max(1, (datetime.now() - published_date).days)
    processed_data['days_since_published'] = days_live
    processed_data['views_per_day'] = processed_data['view_count'] / days_live
    processed_data['likes_per_day'] = processed_data['like_count'] / days_live
    processed_data['comments_per_day'] = processed_data['comment_count'] / days_live
    
    # Parse duration
    duration_match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', video_data['duration'])
    if duration_match:
        hours = int(duration_match.group(1) or 0)
        minutes = int(duration_match.group(2) or 0)
        seconds = int(duration_match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        processed_data['duration_seconds'] = total_seconds
    else:
        processed_data['duration_seconds'] = 0
    
    return processed_data

def extract_features(processed_data):
    """
    Extract features for ML model
    
    Args:
        processed_data (dict): Processed video data
        
    Returns:
        dict: Features for prediction
    """
    features = {
        'title_length': processed_data['title_length'],
        'title_word_count': processed_data['title_word_count'],
        'has_question_in_title': int(processed_data['has_question_in_title']),
        'has_exclamation_in_title': int(processed_data['has_exclamation_in_title']),
        'has_number_in_title': int(processed_data['has_number_in_title']),
        'has_emoji_in_title': int(processed_data['has_emoji_in_title']),
        'tag_count': processed_data['tag_count'],
        'avg_tag_length': processed_data['avg_tag_length'],
        'duration_seconds': processed_data['duration_seconds'],
        'like_view_ratio': processed_data['like_view_ratio'],
        'comment_view_ratio': processed_data['comment_view_ratio'],
        'views_per_day': min(processed_data['views_per_day'], 1000000),  # Cap at 1M to avoid extreme values
        'days_since_published': min(processed_data['days_since_published'], 30),  # Cap at 30 days
    }
    
    return features

def clean_text(text):
    """
    Clean text by removing emojis, extra spaces, etc.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove emojis
    text = remove_emoji(text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def remove_emoji(text):
    """
    Remove emojis from text
    
    Args:
        text (str): Text with emojis
        
    Returns:
        str: Text without emojis
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def contains_emoji(text):
    """
    Check if text contains emojis
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text contains emojis, False otherwise
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    return bool(emoji_pattern.search(text))
