# tasks/nlp.py
from celery import shared_task
import nltk
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
import string
from datetime import datetime
import re

# Download required NLTK data (would need to be done once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class HazardNLPAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.hazard_keywords = {
            'tsunami', 'storm', 'flood', 'wave', 'erosion', 'cyclone', 
            'typhoon', 'hurricane', 'tidal', 'surge', 'coastal', 'marine',
            'warning', 'alert', 'emergency', 'disaster', 'hazard', 'danger',
            'evacuate', 'shelter', 'rescue', 'damage', 'destroy', 'impact'
        }
        self.severity_keywords = {
            'severe', 'extreme', 'critical', 'dangerous', 'catastrophic',
            'devastating', 'massive', 'huge', 'enormous', 'intense'
        }

    def analyze_text(self, text):
        """Comprehensive NLP analysis of hazard-related text"""
        if not text or not isinstance(text, str):
            return {}
        
        text = text.lower()
        
        # Sentiment analysis
        sentiment = self.sia.polarity_scores(text)
        
        # TextBlob analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Tokenization and POS tagging
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        
        # Hazard keyword analysis
        hazard_matches = [word for word in tokens if word in self.hazard_keywords]
        severity_matches = [word for word in tokens if word in self.severity_keywords]
        
        # Location extraction (simple pattern matching)
        locations = self.extract_locations(text)
        
        # Urgency detection
        urgency_score = self.calculate_urgency_score(text, hazard_matches, severity_matches)
        
        return {
            "sentiment": sentiment,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "hazard_keywords": list(set(hazard_matches)),
            "severity_keywords": list(set(severity_matches)),
            "locations": locations,
            "urgency_score": urgency_score,
            "word_count": len(tokens),
            "unique_hazard_words": len(set(hazard_matches)),
            "analysis_time": datetime.utcnow().isoformat()
        }

    def extract_locations(self, text):
        """Extract potential location mentions"""
        # Simple pattern matching for locations
        patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Capitalized words (potential place names)
            r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        locations = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            locations.update(matches)
        
        return list(locations)

    def calculate_urgency_score(self, text, hazard_matches, severity_matches):
        """Calculate urgency score based on content analysis"""
        base_score = len(hazard_matches) * 2
        severity_bonus = len(severity_matches) * 3
        
        # Check for emergency indicators
        emergency_indicators = ['emergency', 'urgent', 'immediate', 'now', 'help', 'sos']
        emergency_count = sum(1 for word in emergency_indicators if word in text)
        emergency_bonus = emergency_count * 5
        
        # Check for time sensitivity
        time_indicators = ['now', 'today', 'immediately', 'soon', 'coming']
        time_count = sum(1 for word in time_indicators if word in text)
        time_bonus = time_count * 2
        
        total_score = base_score + severity_bonus + emergency_bonus + time_bonus
        
        # Cap at 100
        return min(total_score, 100)

@shared_task
def analyze_hazard_text(text_data):
    """Analyze hazard-related text using NLP"""
    analyzer = HazardNLPAnalyzer()
    
    if isinstance(text_data, str):
        # Single text analysis
        return analyzer.analyze_text(text_data)
    elif isinstance(text_data, list):
        # Batch analysis
        results = []
        for text in text_data:
            if isinstance(text, str):
                results.append(analyzer.analyze_text(text))
        return results
    else:
        return {"error": "Invalid input format"}

@shared_task
def process_social_media_batch(social_media_data):
    """Process a batch of social media posts with NLP"""
    analyzer = HazardNLPAnalyzer()
    processed_data = []
    
    for post in social_media_data:
        text = post.get('text') or post.get('content') or ''
        analysis = analyzer.analyze_text(text)
        
        processed_post = {
            **post,
            "nlp_analysis": analysis,
            "processed": True,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        processed_data.append(processed_post)
    
    return processed_data

@shared_task
def detect_hazard_trends(text_corpus):
    """Detect trending hazard topics from a corpus of text"""
    analyzer = HazardNLPAnalyzer()
    
    if not text_corpus:
        return {}
    
    # Combine all text for analysis
    combined_text = " ".join([str(text) for text in text_corpus if text])
    
    # Frequency analysis
    tokens = word_tokenize(combined_text.lower())
    filtered_tokens = [word for word in tokens if word not in analyzer.stop_words and word not in string.punctuation]
    
    from collections import Counter
    word_freq = Counter(filtered_tokens)
    
    # Get top hazard-related words
    top_hazard_words = {word: count for word, count in word_freq.items() 
                       if word in analyzer.hazard_keywords and count > 1}
    
    # Overall sentiment
    overall_sentiment = analyzer.sia.polarity_scores(combined_text)
    
    return {
        "total_posts": len(text_corpus),
        "top_hazard_words": dict(sorted(top_hazard_words.items(), key=lambda x: x[1], reverse=True)[:10]),
        "overall_sentiment": overall_sentiment,
        "average_urgency": sum(analyzer.calculate_urgency_score(str(text), [], []) for text in text_corpus) / len(text_corpus),
        "analysis_time": datetime.utcnow().isoformat()
    }
