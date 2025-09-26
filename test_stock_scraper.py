"""
Test script for the enhanced stock scraper
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import FinvizScraper
from database import SessionLocal, create_tables, test_connection
from services import StockService, NewsService

def test_stock_scraping():
    """Test stock data scraping"""
    
    scraper = FinvizScraper()
    
    stock_data = scraper.get_stock_data("AAPL")
    
    if stock_data:
    else:
        return False
    
    return True

def test_database_operations():
    """Test database operations"""
    
    if not test_connection():
        return False
    
    
    create_tables()
    
    db = SessionLocal()
    try:
        stock_service = StockService(db)
        
        stock = stock_service.scrape_and_save_stock("AAPL")
        
        if stock:
        else:
            return False
        
        retrieved_stock = stock_service.get_stock("AAPL")
        if retrieved_stock:
        else:
            return False
        
        news_service = NewsService(db)
        
        result = news_service.scrape_and_save_news("AAPL", limit=5)
        
    finally:
        db.close()
    
    return True

def test_api_endpoints():
    """Test API endpoints"""
    
    try:
        import requests
        import time
        
        time.sleep(2)
        
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
        else:
            return False
        
        response = requests.get("http://localhost:8000/api/stocks?limit=5")
        if response.status_code == 200:
            data = response.json()
        else:
            return False
        
        response = requests.get("http://localhost:8000/api/stocks/AAPL")
        if response.status_code == 200:
            data = response.json()
        else:
            return False
        
        response = requests.get("http://localhost:8000/api/news?limit=5")
        if response.status_code == 200:
            data = response.json()
        else:
            return False
        
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            data = response.json()
        else:
            return False
        
    except Exception as e:
        return False
    
    return True

def main():
    """Main test function"""
    
    if not test_stock_scraping():
        return 1
    
    if not test_database_operations():
        return 1
    
    
    try:
        if test_api_endpoints():
        else:
    except Exception as e:
    
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)