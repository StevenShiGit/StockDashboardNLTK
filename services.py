from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from models import Stock, NewsArticle
from scraper import FinvizScraper
from sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.scraper = FinvizScraper()
    
    def get_all_stocks(self, limit: int = 100, offset: int = 0) -> List[Stock]:
        """Get all stocks with pagination"""
        return self.db.query(Stock).offset(offset).limit(limit).all()
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Get specific stock by symbol"""
        return self.db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    
    def search_stocks(self, query: str, limit: int = 20) -> List[Stock]:
        """Search stocks by symbol or name"""
        search_term = f"%{query.upper()}%"
        return self.db.query(Stock).filter(
            or_(
                Stock.symbol.like(search_term),
                Stock.name.like(f"%{query}%")
            )
        ).limit(limit).all()
    
    def get_stocks_by_sector(self, sector: str, limit: int = 50) -> List[Stock]:
        """Get stocks by sector"""
        return self.db.query(Stock).filter(
            Stock.sector == sector
        ).limit(limit).all()
    
    def get_stocks_by_industry(self, industry: str, limit: int = 50) -> List[Stock]:
        """Get stocks by industry"""
        return self.db.query(Stock).filter(
            Stock.industry == industry
        ).limit(limit).all()
    
    def create_or_update_stock(self, stock_data: Dict[str, Any]) -> Stock:
        """Create or update stock data"""
        symbol = stock_data.get('symbol', '').upper()
        
        existing_stock = self.get_stock(symbol)
        
        if existing_stock:
            for key, value in stock_data.items():
                if hasattr(existing_stock, key) and value is not None:
                    setattr(existing_stock, key, value)
            existing_stock.updated_at = datetime.now()
            self.db.commit()
            return existing_stock
        else:
            new_stock = Stock(**stock_data)
            self.db.add(new_stock)
            self.db.commit()
            self.db.refresh(new_stock)
            return new_stock
    
    def scrape_and_save_stock(self, symbol: str) -> Optional[Stock]:
        """Scrape stock data and save to database"""
        try:
            stock_data = self.scraper.get_stock_data(symbol)
            
            if stock_data:
                return self.create_or_update_stock(stock_data)
            else:
                return None
                
        except Exception as e:

                
            pass
            return None
    
    def bulk_scrape_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """Bulk scrape multiple stocks"""
        results = {
            'successful': [],
            'failed': [],
            'total': len(symbols)
        }
        
        for symbol in symbols:
            try:
                stock = self.scrape_and_save_stock(symbol)
                if stock:
                    results['successful'].append(symbol)
                else:
                    results['failed'].append(symbol)
            except Exception as e:
                results['failed'].append(symbol)
        
        return results
    
    def get_stock_statistics(self) -> Dict[str, Any]:
        """Get stock database statistics"""
        total_stocks = self.db.query(Stock).count()
        
        sector_stats = self.db.query(
            Stock.sector,
            func.count(Stock.id).label('count')
        ).group_by(Stock.sector).all()
        
        industry_stats = self.db.query(
            Stock.industry,
            func.count(Stock.id).label('count')
        ).group_by(Stock.industry).limit(10).all()
        
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_updates = self.db.query(Stock).filter(
            Stock.updated_at >= recent_cutoff
        ).count()
        
        return {
            'total_stocks': total_stocks,
            'recent_updates_24h': recent_updates,
            'sectors': {sector: count for sector, count in sector_stats},
            'top_industries': {industry: count for industry, count in industry_stats}
        }

class NewsService:
    def __init__(self, db: Session):
        self.db = db
        self.scraper = FinvizScraper()
    
    def get_news(self, symbol: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[NewsArticle]:
        """Get news articles with optional symbol filter"""
        query = self.db.query(NewsArticle)
        
        if symbol:
            query = query.filter(NewsArticle.stock_symbol == symbol.upper())
        
        return query.order_by(desc(NewsArticle.published_date)).offset(offset).limit(limit).all()
    
    def get_recent_news(self, hours: int = 24, limit: int = 50) -> List[NewsArticle]:
        """Get recent news within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return self.db.query(NewsArticle).filter(
            NewsArticle.published_date >= cutoff_time
        ).order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def get_news_by_symbol(self, symbol: str, limit: int = 20) -> List[NewsArticle]:
        """Get news for specific symbol"""
        return self.db.query(NewsArticle).filter(
            NewsArticle.stock_symbol == symbol.upper()
        ).order_by(desc(NewsArticle.published_date)).limit(limit).all()
    
    def create_or_update_news(self, news_data: Dict[str, Any]) -> NewsArticle:
        """Create or update news article"""
        existing_article = self.db.query(NewsArticle).filter(
            NewsArticle.link == news_data.get('link')
        ).first()
        
        if existing_article:
            for key, value in news_data.items():
                if hasattr(existing_article, key) and value is not None:
                    setattr(existing_article, key, value)
            self.db.commit()
            return existing_article
        else:
            new_article = NewsArticle(**news_data)
            self.db.add(new_article)
            self.db.commit()
            self.db.refresh(new_article)
            return new_article
    
    def analyze_article_sentiment(self, article: NewsArticle) -> NewsArticle:
        """Analyze sentiment for a single article"""
        try:
            sentiment_data = sentiment_analyzer.analyze_article(
                title=article.title,
                summary=article.summary or ""
            )
            
            article.sentiment_score = sentiment_data['sentiment_score']
            article.sentiment_label = sentiment_data['sentiment_label']
            article.sentiment_confidence = sentiment_data['sentiment_confidence']
            article.textblob_polarity = sentiment_data['textblob_polarity']
            article.textblob_subjectivity = sentiment_data['textblob_subjectivity']
            article.vader_compound = sentiment_data['vader_compound']
            article.vader_positive = sentiment_data['vader_positive']
            article.vader_negative = sentiment_data['vader_negative']
            article.vader_neutral = sentiment_data['vader_neutral']
            article.sentiment_analyzed_at = datetime.now()
            
            self.db.commit()
            
        except Exception as e:
            pass
        
        return article
    
    def analyze_news_sentiment(self, symbol: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Analyze sentiment for news articles"""
        try:
            query = self.db.query(NewsArticle).filter(
                NewsArticle.sentiment_score.is_(None)
            )
            
            if symbol:
                query = query.filter(NewsArticle.stock_symbol == symbol.upper())
            
            articles = query.limit(limit).all()
            
            analyzed_count = 0
            for article in articles:
                self.analyze_article_sentiment(article)
                analyzed_count += 1
            
            return {
                'analyzed_count': analyzed_count,
                'symbol': symbol or 'all',
                'status': 'completed'
            }
            
        except Exception as e:

            
            pass
            return {
                'analyzed_count': 0,
                'symbol': symbol or 'all',
                'status': 'error',
                'error': str(e)
            }
    
    def get_stock_sentiment_summary(self, symbol: str, days_back: int = 7) -> Dict[str, Any]:
        """Get sentiment summary for a specific stock"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            articles = self.db.query(NewsArticle).filter(
                NewsArticle.stock_symbol == symbol.upper(),
                NewsArticle.published_date >= cutoff_date,
                NewsArticle.sentiment_score.isnot(None)
            ).all()
            
            if not articles:
                return {
                    'symbol': symbol.upper(),
                    'overall_sentiment': 'neutral',
                    'sentiment_score': 0.0,
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0,
                    'days_analyzed': days_back
                }
            
            articles_data = []
            for article in articles:
                articles_data.append({
                    'sentiment_score': article.sentiment_score,
                    'sentiment_label': article.sentiment_label,
                    'sentiment_confidence': article.sentiment_confidence
                })
            
            summary = sentiment_analyzer.get_stock_sentiment_summary(articles_data)
            summary['symbol'] = symbol.upper()
            summary['days_analyzed'] = days_back
            
            return summary
            
        except Exception as e:

            
            pass
            return {
                'symbol': symbol.upper(),
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0,
                'days_analyzed': days_back,
                'error': str(e)
            }
    
    def scrape_and_save_news(self, symbol: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Scrape news and save to database"""
        try:
            if symbol:
                articles = self.scraper.get_news_for_stock(symbol, max_pages=5)
            else:
                popular_symbols = self.scraper.get_popular_stocks()
                articles = []
                for sym in popular_symbols[:10]:
                    articles.extend(self.scraper.get_news_for_stock(sym, max_pages=2))
            
            saved_count = 0
            for article_data in articles:
                try:
                    self.create_or_update_news(article_data)
                    saved_count += 1
                except Exception as e:
                    continue
            
            return {
                'scraped': len(articles),
                'saved': saved_count,
                'symbol': symbol or 'multiple'
            }
            
        except Exception as e:

            
            pass
            return {'scraped': 0, 'saved': 0, 'error': str(e)}
    
    def get_news_statistics(self) -> Dict[str, Any]:
        """Get news database statistics"""
        total_articles = self.db.query(NewsArticle).count()
        
        symbol_stats = self.db.query(
            NewsArticle.stock_symbol,
            func.count(NewsArticle.id).label('count')
        ).group_by(NewsArticle.stock_symbol).all()
        
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_articles = self.db.query(NewsArticle).filter(
            NewsArticle.scraped_at >= recent_cutoff
        ).count()
        
        return {
            'total_articles': total_articles,
            'recent_articles_24h': recent_articles,
            'articles_by_symbol': {symbol: count for symbol, count in symbol_stats}
        }