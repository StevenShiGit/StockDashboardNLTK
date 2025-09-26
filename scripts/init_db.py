"""
Database initialization script
Run this script to create the database tables
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import create_tables, test_connection
from config import Config

def main():
    """Initialize the database"""
    
    try:
        Config.validate_config()
        
        if not test_connection():
            return 1
        
        
        create_tables()
        
        return 0
        
    except Exception as e:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)