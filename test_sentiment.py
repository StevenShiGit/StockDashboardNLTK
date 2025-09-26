"""
Test script for sentiment analysis functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_analyzer import sentiment_analyzer
from database import SessionLocal, create_tables, test_connection
from services import NewsService

def test_sentiment_analyzer():
    """Test the sentiment analyzer with sample texts"""
    
    test_cases = [
        {
            "title": "Apple Reports Record Quarterly Revenue",
            "summary": "Apple Inc. reported its highest quarterly revenue ever, driven by strong iPhone sales and services growth.",
            "expected": "positive"
        },
        {
            "title": "Stock Market Crashes Amid Economic Uncertainty",
            "summary": "Major stock indices plummeted today as investors worry about inflation and economic instability.",
            "expected": "negative"
        },
        {
            "title": "Company Announces Quarterly Earnings",
            "summary": "The company released its quarterly financial results showing mixed performance across different segments.",
            "expected": "neutral"
        },
        {
            "title": "Tesla Stock Surges on Strong Delivery Numbers",
            "summary": "Tesla shares jumped 15% after reporting record vehicle deliveries, exceeding analyst expectations.",
            "expected": "positive"
        },
        {
            "title": "Tech Giant Faces Regulatory Investigation",
            "summary": "The company is under investigation for potential antitrust violations, causing investor concern.",
            "expected": "negative"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        
        result = sentiment_analyzer.analyze_article(case['title'], case['summary'])
        
        
        if result['sentiment_label'] == case['expected']:
        else:

def test_database_sentiment():
    """Test sentiment analysis with database operations"""
    
    if not test_connection():
        return False
    
    
    create_tables()
    
    db = SessionLocal()
    try:
        news_service = NewsService(db)
        
        articles = news_service.get_news(limit=5)
        
        if articles:
            
            for i, article in enumerate(articles[:3]):
                
                analyzed_article = news_service.analyze_article_sentiment(article)
                
        
        summary = news_service.get_stock_sentiment_summary("AAPL", days_back=7)
        
        
    finally:
        db.close()
    
    return True

def test_api_endpoints():
    """Test sentiment analysis API endpoints"""
    
    try:
        import requests
        import time
        
        time.sleep(2)
        
        base_url = "http://localhost:8000"
        
        response = requests.post(f"{base_url}/api/sentiment/analyze?symbol=AAPL&limit=5")
        if response.status_code == 200:
        else:
        
        response = requests.get(f"{base_url}/api/sentiment/stock/AAPL?days_back=7")
        if response.status_code == 200:
            data = response.json()
        else:
        
        response = requests.get(f"{base_url}/api/sentiment/articles?limit=5")
        if response.status_code == 200:
            data = response.json()
        else:
        
        response = requests.get(f"{base_url}/api/sentiment/stats")
        if response.status_code == 200:
            data = response.json()
        else:
        
    except Exception as e:

def main():
    """Main test function"""
    
    test_sentiment_analyzer()
    
    if test_database_sentiment():
    else:
        return 1
    
    
    try:
        test_api_endpoints()
    except Exception as e:
    
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)