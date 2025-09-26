"""
Standalone script to scrape news for specific stocks
Usage: python scripts/scrape_stocks.py AAPL TSLA MSFT
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import FinvizScraper
from database import SessionLocal, create_tables
from models import NewsArticle
from config import Config

def scrape_and_store(symbols, max_pages=5):
    """Scrape news for given symbols and store in database"""
    scraper = FinvizScraper()
    db = SessionLocal()
    
    try:
        create_tables()
        
        total_stored = 0
        
        for symbol in symbols:
            
            try:
                articles = scraper.get_news_for_stock(symbol, max_pages)
                
                stored_count = 0
                for article_data in articles:
                    try:
                        existing = db.query(NewsArticle).filter(
                            NewsArticle.link == article_data['link']
                        ).first()
                        
                        if not existing:
                            db_article = NewsArticle(
                                title=article_data['title'],
                                link=article_data['link'],
                                summary=article_data.get('summary', ''),
                                source=article_data.get('source', ''),
                                stock_symbol=article_data['stock_symbol'],
                                published_date=article_data.get('published_date')
                            )
                            
                            db.add(db_article)
                            stored_count += 1
                        else:
                    
                    except Exception as e:
                        continue
                
                db.commit()
                total_stored += stored_count
                
            except Exception as e:
                continue
        
        return total_stored
        
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Scrape news for stock symbols')
    parser.add_argument('symbols', nargs='+', help='Stock symbols to scrape (e.g., AAPL TSLA MSFT)')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages to scrape per stock')
    parser.add_argument('--init-db', action='store_true', help='Initialize database before scraping')
    
    args = parser.parse_args()
    
    
    try:
        Config.validate_config()
        
        if args.init_db:
            from database import test_connection, create_tables
            if not test_connection():
                return 1
            create_tables()
        
        total_stored = scrape_and_store(args.symbols, args.max_pages)
        
        
        return 0
        
    except Exception as e:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)