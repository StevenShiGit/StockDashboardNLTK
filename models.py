from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    link = Column(Text, nullable=False, unique=True)
    summary = Column(Text)
    source = Column(String(100))
    stock_symbol = Column(String(10), nullable=False, index=True)
    published_date = Column(DateTime)
    scraped_at = Column(DateTime, default=func.now())
    is_processed = Column(Boolean, default=False)
    
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    sentiment_confidence = Column(Float)
    textblob_polarity = Column(Float)
    textblob_subjectivity = Column(Float)
    vader_compound = Column(Float)
    vader_positive = Column(Float)
    vader_negative = Column(Float)
    vader_neutral = Column(Float)
    sentiment_analyzed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_stock_symbol_published', 'stock_symbol', 'published_date'),
        Index('idx_scraped_at', 'scraped_at'),
        Index('idx_sentiment_score', 'sentiment_score'),
        Index('idx_sentiment_label', 'sentiment_label'),
    )
    
    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...', symbol='{self.stock_symbol}', sentiment='{self.sentiment_label}')>"

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(200))
    price = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    volume = Column(Integer)
    avg_volume = Column(Integer)
    market_cap = Column(String(50))
    pe_ratio = Column(Float)
    eps = Column(Float)
    dividend = Column(Float)
    dividend_yield = Column(Float)
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    exchange = Column(String(20))
    ipo_date = Column(Date)
    currency = Column(String(10))
    high_52w = Column(Float)
    low_52w = Column(Float)
    rsi = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_symbol', 'symbol'),
        Index('idx_sector', 'sector'),
        Index('idx_industry', 'industry'),
        Index('idx_updated_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}', price={self.price})>"