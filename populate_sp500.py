"""
Populate database with S&P 500 companies
This script adds all S&P 500 stock symbols and names to the database
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, create_tables, test_connection
from models import Stock
from sp500_data import get_sp500_companies
from datetime import datetime

def populate_sp500():
    
    
    if not test_connection():
      
        return False
    
  
    
    create_tables()
    
    
    companies = get_sp500_companies()
    
    db = SessionLocal()
    
    try:
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for symbol, name in companies:
            try:
                existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
                
                if existing_stock:
                    if not existing_stock.name:
                        existing_stock.name = name
                        existing_stock.updated_at = datetime.now()
                        updated_count += 1
                      
                    else:
                        skipped_count += 1
                        
                else:
                    new_stock = Stock(
                        symbol=symbol,
                        name=name,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.add(new_stock)
                    db.commit()
                    added_count += 1
                
            except Exception as e:
                
                db.rollback()
                continue
        
        
        return True
        
    except Exception as e:
    
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """Main function"""
   
    
    if populate_sp500():
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)