import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

from youtube_api import get_video_data, get_trending_shorts
from data_processor import process_video_data, extract_features
from model import predict_engagement
from utils import is_shorts_url, extract_video_id, format_number

# Page configuration
st.set_page_config(
    page_title="YouTube Shorts Trend Analyzer",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("📱 YouTube Shorts Trend Analyzer")
st.markdown("""
This application analyzes YouTube Shorts metadata to identify trends and predict viewer engagement potential.
Enter a YouTube Shorts URL below to get started.
""")

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Main input for YouTube URL
url_input = st.text_input(
    "Enter YouTube Shorts URL:",
    placeholder="https://www.youtube.com/shorts/..."
)

# Analysis trigger
analyze_button = st.button("Analyze Video", type="primary")

# Function to display error messages
def show_error(message):
    st.error(message)

# Function to display video info
def display_video_info(video_data):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display thumbnail
        if 'thumbnail_url' in video_data:
            st.image(video_data['thumbnail_url'], use_column_width=True)
    
    with col2:
        # Display basic video info
        st.subheader(video_data['title'])
        st.write(f"**Channel:** {video_data['channel_title']}")
        
        # Create metrics row
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Views", format_number(video_data['view_count']))
        with metric_col2:
            st.metric("Likes", format_number(video_data['like_count']))
        with metric_col3:
            st.metric("Comments", format_number(video_data['comment_count']))
        with metric_col4:
            published_date = datetime.strptime(video_data['published_at'], "%Y-%m-%dT%H:%M:%SZ")
            days_ago = (datetime.now() - published_date).days
            st.metric("Published", f"{days_ago} days ago")
        
        # Display tags if available
        if video_data['tags']:
            st.write("**Tags:**")
            tags_html = ' '.join([f'<span style="background-color: #f0f2f6; padding: 2px 8px; margin: 0 4px 4px 0; border-radius: 12px; display: inline-block; font-size: 0.8em;">{tag}</span>' for tag in video_data['tags']])
            st.markdown(f'<div style="display: flex; flex-wrap: wrap;">{tags_html}</div>', unsafe_allow_html=True)

# Function to display engagement metrics
def display_engagement_metrics(video_data, prediction_result):
    st.subheader("Engagement Analysis")
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        views_per_day = int(video_data['view_count'] / max(1, (datetime.now() - datetime.strptime(video_data['published_at'], "%Y-%m-%dT%H:%M:%SZ")).days))
        st.metric("Views/Day", format_number(views_per_day))
        
    with col2:
        like_view_ratio = round((video_data['like_count'] / max(1, video_data['view_count'])) * 100, 2)
        st.metric("Like/View Ratio", f"{like_view_ratio}%")
        
    with col3:
        comment_view_ratio = round((video_data['comment_count'] / max(1, video_data['view_count'])) * 1000, 2)
        st.metric("Comments/1K Views", comment_view_ratio)
    
    # Display engagement potential gauge
    st.subheader("Engagement Potential")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prediction_result['score'] * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Viral Potential Score"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': "rgba(50, 168, 82, 0.8)"},
            'steps': [
                {'range': [0, 30], 'color': "rgba(255, 99, 132, 0.3)"},
                {'range': [30, 70], 'color': "rgba(255, 205, 86, 0.3)"},
                {'range': [70, 100], 'color': "rgba(75, 192, 192, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': prediction_result['score'] * 100
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Display prediction explanation
    st.markdown(f"**Prediction:** {prediction_result['explanation']}")
    
    # Display key factors
    st.markdown("**Key Factors Influencing Score:**")
    for factor in prediction_result['key_factors']:
        st.markdown(f"- {factor}")

# Function to display comparison with trending videos
def display_trending_comparison(video_data, trending_data):
    st.subheader("Comparison with Trending Shorts")
    
    if not trending_data:
        st.info("Could not retrieve trending data for comparison at this time.")
        return
    
    # Create a dataframe for trending videos
    df_trending = pd.DataFrame(trending_data)
    
    # Calculate average metrics
    avg_views = df_trending['view_count'].mean()
    avg_likes = df_trending['like_count'].mean()
    avg_comments = df_trending['comment_count'].mean()
    avg_like_ratio = (df_trending['like_count'] / df_trending['view_count'].clip(lower=1)).mean() * 100
    
    # Compare with current video
    current_like_ratio = (video_data['like_count'] / max(1, video_data['view_count'])) * 100
    
    # Create comparison chart
    metrics = ['Views', 'Likes', 'Comments', 'Like/View %']
    current_values = [
        video_data['view_count'] / max(1, avg_views) * 100,
        video_data['like_count'] / max(1, avg_likes) * 100,
        video_data['comment_count'] / max(1, avg_comments) * 100,
        current_like_ratio / max(0.01, avg_like_ratio) * 100
    ]
    
    fig = go.Figure()
    
    # Add bar for current video (as percentage of trending average)
    fig.add_trace(go.Bar(
        x=metrics,
        y=current_values,
        name='Your Video vs Trending Average (%)',
        marker_color='rgba(75, 192, 192, 0.8)',
        text=[f"{val:.1f}%" for val in current_values],
        textposition='auto',
    ))
    
    # Add line at 100% for reference
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=100,
        x1=3.5,
        y1=100,
        line=dict(
            color="red",
            width=2,
            dash="dash",
        )
    )
    
    fig.update_layout(
        title="Your Video Compared to Trending Average (100% = Equal to Average)",
        xaxis_title="Metrics",
        yaxis_title="Percentage of Trending Average",
        height=400,
        yaxis=dict(
            range=[0, max(max(current_values) * 1.1, 110)]
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanatory text
    if sum(val > 100 for val in current_values) >= 2:
        st.success("Your video is performing above average in multiple metrics compared to trending videos!")
    elif sum(val > 100 for val in current_values) == 1:
        st.info("Your video is performing above average in one metric, with room for improvement in others.")
    else:
        st.warning("Your video is currently performing below trending averages. See recommendations below.")

# Function to display recommendations
def display_recommendations(video_data, prediction_result):
    st.subheader("Recommendations to Improve Engagement")
    
    recommendations = []
    
    # Title length recommendation
    title_length = len(video_data['title'])
    if title_length < 30:
        recommendations.append("Consider using a slightly longer title (30-50 characters) that includes trending keywords to improve searchability.")
    elif title_length > 60:
        recommendations.append("Your title is quite long. Consider a more concise title (30-50 characters) that still conveys the key message.")
    
    # Tags recommendation
    if len(video_data['tags']) < 5:
        recommendations.append("Add more relevant tags (aim for 8-10) to improve discoverability.")
    
    # Like/view ratio recommendation
    like_view_ratio = (video_data['like_count'] / max(1, video_data['view_count'])) * 100
    if like_view_ratio < 5:
        recommendations.append("Your like-to-view ratio is lower than optimal. Try creating more engaging hooks and calls to action.")
    
    # Comment engagement recommendation
    comment_view_ratio = (video_data['comment_count'] / max(1, video_data['view_count'])) * 1000
    if comment_view_ratio < 2:
        recommendations.append("Encourage more comments by asking questions or creating content that sparks discussion.")
    
    # Add custom recommendations based on prediction
    if prediction_result['score'] < 0.3:
        recommendations.append("Consider trends analysis: Study currently viral Shorts for inspiration on content and style.")
        recommendations.append("Improve hook: The first 3 seconds are crucial for retention - make them more compelling.")
    elif prediction_result['score'] < 0.7:
        recommendations.append("Consistency is key: Regular posting can help build momentum and improve algorithmic favor.")
    
    # Display recommendations
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.success("Your video is well optimized! Continue with your current strategy.")

# Main logic flow
if analyze_button and url_input:
    if not is_shorts_url(url_input):
        show_error("Invalid URL. Please enter a valid YouTube Shorts URL.")
    else:
        with st.spinner("Analyzing video..."):
            try:
                # Extract video ID
                video_id = extract_video_id(url_input)
                
                # Fetch video data
                video_data = get_video_data(video_id)
                
                if not video_data:
                    show_error("Could not retrieve video data. Please check the URL and try again.")
                else:
                    # Process video data
                    processed_data = process_video_data(video_data)
                    
                    # Extract features for prediction
                    features = extract_features(processed_data)
                    
                    # Get prediction
                    prediction_result = predict_engagement(features)
                    
                    # Get trending videos for comparison
                    trending_videos = get_trending_shorts()
                    
                    # Add to history if not already there
                    if video_id not in [item['video_id'] for item in st.session_state.history]:
                        st.session_state.history.insert(0, {
                            'video_id': video_id,
                            'title': video_data['title'],
                            'thumbnail': video_data.get('thumbnail_url', ''),
                            'score': prediction_result['score']
                        })
                        # Keep only the last 5 videos
                        if len(st.session_state.history) > 5:
                            st.session_state.history = st.session_state.history[:5]
                    
                    # Display results in tabs
                    tabs = st.tabs(["Video Analysis", "Trend Comparison", "Recommendations"])
                    
                    with tabs[0]:
                        display_video_info(processed_data)
                        st.markdown("---")
                        display_engagement_metrics(processed_data, prediction_result)
                    
                    with tabs[1]:
                        display_trending_comparison(processed_data, trending_videos)
                    
                    with tabs[2]:
                        display_recommendations(processed_data, prediction_result)
                    
            except Exception as e:
                show_error(f"An error occurred during analysis: {str(e)}")

# Display history
if st.session_state.history:
    st.markdown("---")
    st.subheader("Recently Analyzed Videos")
    
    history_cols = st.columns(min(5, len(st.session_state.history)))
    
    for i, item in enumerate(st.session_state.history):
        if i < len(history_cols):
            with history_cols[i]:
                if item.get('thumbnail'):
                    st.image(item['thumbnail'], use_column_width=True)
                st.write(f"**{item['title'][:50]}**{'...' if len(item['title']) > 50 else ''}")
                st.write(f"Score: {item['score']*100:.1f}%")

# Footer with disclaimer
st.markdown("---")
st.caption("Disclaimer: This tool provides estimates based on available data and should be used as a guide only. Actual performance may vary.")
