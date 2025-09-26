from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database import get_db, create_tables, test_connection
from models import NewsArticle, Stock
from scraper import FinvizScraper
from services import StockService, NewsService
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Stock Dashboard API",
    description="API for scraping and serving stock data and news from Finviz",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = FinvizScraper()

class NewsArticleResponse(BaseModel):
    id: int
    title: str
    link: str
    summary: Optional[str]
    source: Optional[str]
    stock_symbol: str
    published_date: Optional[datetime]
    scraped_at: datetime
    is_processed: bool

    class Config:
        from_attributes = True

class ScrapeRequest(BaseModel):
    symbols: List[str]
    max_pages_per_stock: Optional[int] = 5

class ScrapeResponse(BaseModel):
    message: str
    total_articles: int
    articles_by_symbol: dict

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    
    if not test_connection():
        raise Exception("Database connection failed")
    
    create_tables()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Finviz News Scraper API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_news(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
):
    """
    Scrape news articles for given stock symbols and store them in the database
    """
    try:
        
        total_articles = 0
        articles_by_symbol = {}
        
        for symbol in request.symbols:
            try:
                articles = scraper.get_news_for_stock(symbol, request.max_pages_per_stock)
                
                stored_count = 0
                for article_data in articles:
                    try:
                        existing_article = db.query(NewsArticle).filter(
                            NewsArticle.link == article_data['link']
                        ).first()
                        
                        if not existing_article:
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
                            continue
                    
                    except Exception as e:
                        continue
                
                db.commit()
                
                articles_by_symbol[symbol] = {
                    "scraped": len(articles),
                    "stored": stored_count
                }
                total_articles += stored_count
                
                
            except Exception as e:
                articles_by_symbol[symbol] = {
                    "scraped": 0,
                    "stored": 0,
                    "error": str(e)
                }
        
        return ScrapeResponse(
            message=f"Scraping completed. Total new articles stored: {total_articles}",
            total_articles=total_articles,
            articles_by_symbol=articles_by_symbol
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news", response_model=List[NewsArticleResponse])
async def get_news(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    days_back: Optional[int] = Query(None, ge=1, description="Only return articles from the last N days"),
    db: Session = Depends(get_db)
):
    """
    Retrieve news articles from the database with optional filtering
    """
    try:
        query = db.query(NewsArticle)
        
        if symbol:
            query = query.filter(NewsArticle.stock_symbol == symbol.upper())
        
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query = query.filter(NewsArticle.published_date >= cutoff_date)
        
        query = query.order_by(NewsArticle.published_date.desc())
        
        articles = query.offset(offset).limit(limit).all()
        
        return articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{article_id}", response_model=NewsArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific news article by ID
    """
    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article

@app.get("/symbols")
async def get_symbols(db: Session = Depends(get_db)):
    """
    Get list of all stock symbols that have news articles
    """
    try:
        symbols = db.query(NewsArticle.stock_symbol).distinct().all()
        return [symbol[0] for symbol in symbols]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about stored news articles
    """
    try:
        total_articles = db.query(NewsArticle).count()
        
        symbol_counts = db.query(
            NewsArticle.stock_symbol,
            func.count(NewsArticle.id).label('count')
        ).group_by(NewsArticle.stock_symbol).all()
        
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_articles = db.query(NewsArticle).filter(
            NewsArticle.scraped_at >= recent_cutoff
        ).count()
        
        return {
            "total_articles": total_articles,
            "recent_articles_24h": recent_articles,
            "articles_by_symbol": {symbol: count for symbol, count in symbol_counts},
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/news/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific news article
    """
    article = db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    
    return {"message": f"Article {article_id} deleted successfully"}

@app.get("/api/stocks")
async def get_stocks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get all stocks with pagination"""
    service = StockService(db)
    stocks = service.get_all_stocks(limit=limit, offset=offset)
    return {
        "stocks": [
            {
                "symbol": stock.symbol,
                "name": stock.name,
                "price": stock.price,
                "change": stock.change,
                "change_percent": stock.change_percent,
                "volume": stock.volume,
                "market_cap": stock.market_cap,
                "sector": stock.sector,
                "industry": stock.industry,
                "updated_at": stock.updated_at.isoformat() if stock.updated_at else None
            }
            for stock in stocks
        ],
        "total": len(stocks)
    }

@app.get("/api/stocks/search")
async def search_stocks(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Search stocks by symbol or name and automatically rescrape data"""
    service = StockService(db)
    stocks = service.search_stocks(q, limit=limit)
    
    for stock in stocks:
        background_tasks.add_task(service.scrape_and_save_stock, stock.symbol)
    
    news_service = NewsService(db)
    for stock in stocks:
        background_tasks.add_task(news_service.scrape_and_save_news, stock.symbol, 10)
    
    return {
        "stocks": [
            {
                "symbol": stock.symbol,
                "name": stock.name,
                "price": stock.price,
                "change": stock.change,
                "change_percent": stock.change_percent,
                "sector": stock.sector,
                "industry": stock.industry
            }
            for stock in stocks
        ],
        "message": f"Found {len(stocks)} stocks. Rescraping stock data and news in background for fresh results."
    }

@app.get("/api/stocks/{symbol}")
async def get_stock(
    symbol: str, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Get specific stock by symbol and automatically rescrape data"""
    service = StockService(db)
    stock = service.get_stock(symbol.upper())
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    background_tasks.add_task(service.scrape_and_save_stock, symbol.upper())
    
    news_service = NewsService(db)
    background_tasks.add_task(news_service.scrape_and_save_news, symbol.upper(), 10)
    
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "price": stock.price,
        "change": stock.change,
        "change_percent": stock.change_percent,
        "volume": stock.volume,
        "avg_volume": stock.avg_volume,
        "market_cap": stock.market_cap,
        "pe_ratio": stock.pe_ratio,
        "eps": stock.eps,
        "dividend": stock.dividend,
        "dividend_yield": stock.dividend_yield,
        "sector": stock.sector,
        "industry": stock.industry,
        "country": stock.country,
        "exchange": stock.exchange,
        "ipo_date": stock.ipo_date.isoformat() if stock.ipo_date else None,
        "currency": stock.currency,
        "high_52w": stock.high_52w,
        "low_52w": stock.low_52w,
        "rsi": stock.rsi,
        "sma_20": stock.sma_20,
        "sma_50": stock.sma_50,
        "sma_200": stock.sma_200,
        "created_at": stock.created_at.isoformat() if stock.created_at else None,
        "updated_at": stock.updated_at.isoformat() if stock.updated_at else None,
        "message": f"Stock data retrieved. Rescraping {symbol.upper()} stock data and news in background for fresh results."
    }

@app.post("/api/stocks/{symbol}/scrape")
async def scrape_stock(
    symbol: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scrape and update stock data"""
    service = StockService(db)
    
    background_tasks.add_task(service.scrape_and_save_stock, symbol.upper())
    
    return {"message": f"Scraping initiated for {symbol.upper()}"}

@app.get("/api/news")
async def get_news_api(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get financial news"""
    service = NewsService(db)
    news = service.get_news(symbol, limit=limit, offset=offset)
    
    return {
        "news": [
            {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "published_at": article.published_date.isoformat() if article.published_date else None,
                "url": article.link,
                "sentiment": getattr(article, 'sentiment', None),
                "symbol": article.stock_symbol,
                "category": getattr(article, 'category', None)
            }
            for article in news
        ],
        "total": len(news)
    }

@app.get("/api/news/recent")
async def get_recent_news_api(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get recent news within specified hours"""
    service = NewsService(db)
    news = service.get_recent_news(hours=hours, limit=limit)
    
    return {
        "news": [
            {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "published_at": article.published_date.isoformat() if article.published_date else None,
                "url": article.link,
                "sentiment": getattr(article, 'sentiment', None),
                "symbol": article.stock_symbol,
                "category": getattr(article, 'category', None)
            }
            for article in news
        ]
    }

@app.post("/api/news/scrape")
async def scrape_news_api(
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Scrape and update news"""
    service = NewsService(db)
    
    background_tasks.add_task(service.scrape_and_save_news, symbol, limit)
    
    return {"message": f"News scraping initiated for {symbol or 'all stocks'}"}

@app.get("/api/stats")
async def get_statistics_api(db: Session = Depends(get_db)):
    """Get database statistics"""
    stock_service = StockService(db)
    news_service = NewsService(db)
    
    stock_stats = stock_service.get_stock_statistics()
    news_stats = news_service.get_news_statistics()
    
    return {
        "stocks": stock_stats,
        "news": news_stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/stocks/bulk-scrape")
async def bulk_scrape_stocks(
    symbols: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Bulk scrape multiple stocks"""
    if len(symbols) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 symbols allowed per request")
    
    service = StockService(db)
    
    background_tasks.add_task(service.bulk_scrape_stocks, symbols)
    
    return {"message": f"Bulk scraping initiated for {len(symbols)} symbols"}

@app.post("/api/stocks/popular-scrape")
async def scrape_popular_stocks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scrape popular stocks"""
    popular_symbols = scraper.get_popular_stocks()
    
    service = StockService(db)
    
    background_tasks.add_task(service.bulk_scrape_stocks, popular_symbols)
    
    return {"message": f"Scraping initiated for {len(popular_symbols)} popular stocks"}

@app.post("/api/sentiment/analyze")
async def analyze_sentiment(
    symbol: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Analyze sentiment for news articles"""
    service = NewsService(db)
    
    background_tasks.add_task(service.analyze_news_sentiment, symbol, limit)
    
    return {"message": f"Sentiment analysis initiated for {symbol or 'all articles'}"}

@app.get("/api/sentiment/stock/{symbol}")
async def get_stock_sentiment(
    symbol: str,
    days_back: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get sentiment summary for a specific stock"""
    service = NewsService(db)
    summary = service.get_stock_sentiment_summary(symbol, days_back)
    
    return summary

@app.get("/api/sentiment/articles")
async def get_articles_with_sentiment(
    symbol: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get articles with sentiment analysis"""
    query = db.query(NewsArticle).filter(
        NewsArticle.sentiment_score.isnot(None)
    )
    
    if symbol:
        query = query.filter(NewsArticle.stock_symbol == symbol.upper())
    
    if sentiment:
        query = query.filter(NewsArticle.sentiment_label == sentiment)
    
    articles = query.order_by(desc(NewsArticle.published_date)).offset(offset).limit(limit).all()
    
    return {
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "published_at": article.published_date.isoformat() if article.published_date else None,
                "url": article.link,
                "symbol": article.stock_symbol,
                "sentiment_score": article.sentiment_score,
                "sentiment_label": article.sentiment_label,
                "sentiment_confidence": article.sentiment_confidence,
                "textblob_polarity": article.textblob_polarity,
                "textblob_subjectivity": article.textblob_subjectivity,
                "vader_compound": article.vader_compound,
                "vader_positive": article.vader_positive,
                "vader_negative": article.vader_negative,
                "vader_neutral": article.vader_neutral,
                "analyzed_at": article.sentiment_analyzed_at.isoformat() if article.sentiment_analyzed_at else None
            }
            for article in articles
        ],
        "total": len(articles)
    }

@app.get("/api/sentiment/stats")
async def get_sentiment_statistics(db: Session = Depends(get_db)):
    """Get sentiment analysis statistics"""
    try:
        total_with_sentiment = db.query(NewsArticle).filter(
            NewsArticle.sentiment_score.isnot(None)
        ).count()
        
        sentiment_dist = db.query(
            NewsArticle.sentiment_label,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.sentiment_score.isnot(None)
        ).group_by(NewsArticle.sentiment_label).all()
        
        avg_scores = db.query(
            func.avg(NewsArticle.sentiment_score).label('avg_score'),
            func.avg(NewsArticle.sentiment_confidence).label('avg_confidence')
        ).filter(
            NewsArticle.sentiment_score.isnot(None)
        ).first()
        
        sentiment_by_symbol = db.query(
            NewsArticle.stock_symbol,
            NewsArticle.sentiment_label,
            func.count(NewsArticle.id).label('count')
        ).filter(
            NewsArticle.sentiment_score.isnot(None)
        ).group_by(NewsArticle.stock_symbol, NewsArticle.sentiment_label).all()
        
        return {
            "total_articles_with_sentiment": total_with_sentiment,
            "sentiment_distribution": {label: count for label, count in sentiment_dist},
            "average_sentiment_score": float(avg_scores.avg_score) if avg_scores.avg_score else 0.0,
            "average_confidence": float(avg_scores.avg_confidence) if avg_scores.avg_confidence else 0.0,
            "sentiment_by_symbol": {
                symbol: {
                    label: count for s, label, count in sentiment_by_symbol if s == symbol
                } for symbol in set(s for s, _, _ in sentiment_by_symbol)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)