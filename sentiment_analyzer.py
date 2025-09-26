"""
Sentiment Analysis Service for Financial News
Uses multiple sentiment analysis methods for comprehensive analysis
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available. Install with: pip install textblob")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    logging.warning("VADER not available. Install with: pip install vaderSentiment")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Install with: pip install transformers torch")

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Comprehensive sentiment analysis using multiple methods
    """
    
    def __init__(self):
        self.vader_analyzer = None
        self.transformers_pipeline = None
        
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.transformers_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception as e:
                self.transformers_pipeline = None
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        text = re.sub(r'<[^>]+>', '', text)
        
        text = re.sub(r'\s+', ' ', text)
        
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text.strip()
    
    def analyze_with_textblob(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        if not TEXTBLOB_AVAILABLE or not text:
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'label': 'neutral'
            }
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': label
            }
        except Exception as e:
            return {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'label': 'neutral'
            }
    
    def analyze_with_vader(self, text: str) -> Dict:
        """Analyze sentiment using VADER"""
        if not VADER_AVAILABLE or not text:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0,
                'label': 'neutral'
            }
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            compound = scores['compound']
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'compound': compound,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'label': label
            }
        except Exception as e:
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0,
                'label': 'neutral'
            }
    
    def analyze_with_transformers(self, text: str) -> Dict:
        """Analyze sentiment using Transformers"""
        if not TRANSFORMERS_AVAILABLE or not self.transformers_pipeline or not text:
            return {
                'label': 'neutral',
                'score': 0.0
            }
        
        try:
            if len(text) > 512:
                text = text[:512]
            
            results = self.transformers_pipeline(text)
            
            best_result = max(results[0], key=lambda x: x['score'])
            
            return {
                'label': best_result['label'].lower(),
                'score': best_result['score']
            }
        except Exception as e:
            return {
                'label': 'neutral',
                'score': 0.0
            }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis using multiple methods
        
        Args:
            text: Text to analyze (title + summary)
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if not text:
            return self._get_default_sentiment()
        
        cleaned_text = self.clean_text(text)
        
        if not cleaned_text:
            return self._get_default_sentiment()
        
        textblob_result = self.analyze_with_textblob(cleaned_text)
        vader_result = self.analyze_with_vader(cleaned_text)
        transformers_result = self.analyze_with_transformers(cleaned_text)
        
        overall_sentiment = self._combine_sentiment_results(
            textblob_result, vader_result, transformers_result
        )
        
        return {
            'sentiment_score': overall_sentiment['score'],
            'sentiment_label': overall_sentiment['label'],
            'sentiment_confidence': overall_sentiment['confidence'],
            'textblob_polarity': textblob_result['polarity'],
            'textblob_subjectivity': textblob_result['subjectivity'],
            'vader_compound': vader_result['compound'],
            'vader_positive': vader_result['positive'],
            'vader_negative': vader_result['negative'],
            'vader_neutral': vader_result['neutral'],
            'transformers_label': transformers_result['label'],
            'transformers_score': transformers_result['score']
        }
    
    def _combine_sentiment_results(self, textblob: Dict, vader: Dict, transformers: Dict) -> Dict:
        """Combine results from multiple sentiment analysis methods"""
        
        labels = [textblob['label'], vader['label'], transformers['label']]
        
        label_counts = {
            'positive': labels.count('positive'),
            'negative': labels.count('negative'),
            'neutral': labels.count('neutral')
        }
        
        majority_label = max(label_counts, key=label_counts.get)
        
        scores = []
        weights = []
        
        if textblob['polarity'] != 0:
            scores.append(textblob['polarity'])
            weights.append(0.3)
        
        if vader['compound'] != 0:
            scores.append(vader['compound'])
            weights.append(0.4)
        
        if transformers['score'] != 0:
            if transformers['label'] == 'positive':
                transformers_score = transformers['score']
            elif transformers['label'] == 'negative':
                transformers_score = -transformers['score']
            else:
                transformers_score = 0
            scores.append(transformers_score)
            weights.append(0.3)
        
        if scores and weights:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            weighted_score = 0.0
        
        total_methods = len([s for s in scores if s != 0])
        if total_methods > 0:
            confidence = label_counts[majority_label] / total_methods
        else:
            confidence = 0.0
        
        return {
            'score': weighted_score,
            'label': majority_label,
            'confidence': confidence
        }
    
    def _get_default_sentiment(self) -> Dict:
        """Return default sentiment when analysis fails"""
        return {
            'sentiment_score': 0.0,
            'sentiment_label': 'neutral',
            'sentiment_confidence': 0.0,
            'textblob_polarity': 0.0,
            'textblob_subjectivity': 0.0,
            'vader_compound': 0.0,
            'vader_positive': 0.0,
            'vader_negative': 0.0,
            'vader_neutral': 0.0,
            'transformers_label': 'neutral',
            'transformers_score': 0.0
        }
    
    def analyze_article(self, title: str, summary: str = "") -> Dict:
        """
        Analyze sentiment of a news article
        
        Args:
            title: Article title
            summary: Article summary (optional)
        
        Returns:
            Dictionary with sentiment analysis results
        """
        full_text = f"{title}"
        if summary:
            full_text += f" {summary}"
        
        return self.analyze_sentiment(full_text)
    
    def get_stock_sentiment_summary(self, articles: List[Dict]) -> Dict:
        """
        Calculate overall sentiment summary for a stock based on multiple articles
        
        Args:
            articles: List of articles with sentiment data
        
        Returns:
            Dictionary with stock sentiment summary
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        sentiment_scores = []
        sentiment_labels = []
        confidences = []
        
        for article in articles:
            if 'sentiment_score' in article and article['sentiment_score'] is not None:
                sentiment_scores.append(article['sentiment_score'])
            if 'sentiment_label' in article and article['sentiment_label']:
                sentiment_labels.append(article['sentiment_label'])
            if 'sentiment_confidence' in article and article['sentiment_confidence'] is not None:
                confidences.append(article['sentiment_confidence'])
        
        if sentiment_scores:
            overall_score = statistics.mean(sentiment_scores)
        else:
            overall_score = 0.0
        
        if sentiment_labels:
            label_counts = {
                'positive': sentiment_labels.count('positive'),
                'negative': sentiment_labels.count('negative'),
                'neutral': sentiment_labels.count('neutral')
            }
            overall_label = max(label_counts, key=label_counts.get)
        else:
            label_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            overall_label = 'neutral'
        
        if confidences:
            overall_confidence = statistics.mean(confidences)
        else:
            overall_confidence = 0.0
        
        return {
            'overall_sentiment': overall_label,
            'sentiment_score': overall_score,
            'confidence': overall_confidence,
            'positive_count': label_counts['positive'],
            'negative_count': label_counts['negative'],
            'neutral_count': label_counts['neutral'],
            'total_articles': len(articles)
        }

sentiment_analyzer = SentimentAnalyzer()