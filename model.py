import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Since we don't have a pre-trained model, we'll create a rule-based scoring system
# In a real-world scenario, this would be replaced with a trained ML model

def predict_engagement(features):
    """
    Predict engagement potential for a YouTube Shorts video
    
    Args:
        features (dict): Video features
        
    Returns:
        dict: Prediction results including score and explanation
    """
    # Base score
    score = 0.5
    
    # Factors that influence the score
    factors = []
    
    # Title-related features
    if features['title_length'] >= 30 and features['title_length'] <= 50:
        score += 0.05
        factors.append("Optimal title length (30-50 characters)")
    elif features['title_length'] < 20:
        score -= 0.05
        
    if features['has_emoji_in_title']:
        score += 0.03
        factors.append("Title contains emoji which can increase engagement")
        
    if features['has_question_in_title']:
        score += 0.03
        factors.append("Title contains a question which can drive curiosity")
        
    if features['has_number_in_title']:
        score += 0.02
        factors.append("Title contains numbers which can increase click-through rate")
    
    # Tag-related features
    if features['tag_count'] >= 8:
        score += 0.05
        factors.append("Good number of tags (8+) for discoverability")
    elif features['tag_count'] <= 3:
        score -= 0.05
    
    # Duration feature
    if 15 <= features['duration_seconds'] <= 45:
        score += 0.1
        factors.append("Optimal video length (15-45 seconds) for viewer retention")
    elif features['duration_seconds'] > 55:
        score -= 0.05
    
    # Engagement metrics
    if features['like_view_ratio'] > 0.1:  # >10% like/view ratio
        score += 0.15
        factors.append("Excellent like-to-view ratio (>10%)")
    elif features['like_view_ratio'] > 0.05:  # >5% like/view ratio
        score += 0.08
        factors.append("Good like-to-view ratio (>5%)")
    
    if features['comment_view_ratio'] > 0.01:  # >1% comment/view ratio
        score += 0.1
        factors.append("High comment engagement")
    
    # Views per day (early traction is a good indicator)
    if features['views_per_day'] > 10000:
        score += 0.15
        factors.append("Strong daily view velocity")
    elif features['views_per_day'] > 1000:
        score += 0.05
        factors.append("Good daily view velocity")
    
    # Cap the score between 0 and 1
    score = max(0.1, min(score, 0.99))
    
    # Generate explanation based on score
    if score > 0.7:
        explanation = "This video shows high viral potential! It has strong engagement metrics and follows best practices."
    elif score > 0.5:
        explanation = "This video has moderate viral potential with decent engagement. Some aspects could be improved."
    else:
        explanation = "This video has lower viral potential. Consider improving key factors to boost engagement."
    
    # Select top 3 factors that contributed most positively
    key_factors = sorted(factors, key=lambda x: len(x), reverse=True)[:3] if factors else ["No standout factors detected"]
    
    return {
        'score': score,
        'explanation': explanation,
        'key_factors': key_factors
    }

# This is a placeholder for a future ML model
class EngagementModel:
    """
    A more sophisticated model that would be trained on historical data
    This is not implemented yet but shows the structure for future expansion
    """
    def __init__(self):
        self.scaler = MinMaxScaler()
        # In a real implementation, we would load pre-trained model weights here
    
    def predict(self, features):
        """
        Make prediction using the trained model
        
        Args:
            features (dict): Video features
            
        Returns:
            float: Engagement score between 0 and 1
        """
        # Convert features to array
        feature_array = np.array([
            features['title_length'],
            features['title_word_count'],
            features['has_question_in_title'],
            features['has_exclamation_in_title'],
            features['has_number_in_title'],
            features['has_emoji_in_title'],
            features['tag_count'],
            features['avg_tag_length'],
            features['duration_seconds'],
            features['like_view_ratio'],
            features['comment_view_ratio'],
            features['views_per_day'],
            features['days_since_published']
        ]).reshape(1, -1)
        
        # Scale features
        scaled_features = self.scaler.transform(feature_array)
        
        # In a real implementation, we would use the trained model to make predictions
        # For now, return a random score between 0.2 and 0.8
        return np.random.uniform(0.2, 0.8)
