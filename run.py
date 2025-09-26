"""
Simple startup script for the Finviz News Scraper
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import sqlalchemy
        import requests
        import bs4
        import psycopg2
        return True
    except ImportError as e:
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        return True
    else:
        return False

def main():
    """Main startup function"""
    
    if not check_requirements():
        return 1
    
    if not check_env_file():
        return 1
    
    try:
        from database import test_connection, create_tables
        if not test_connection():
            return 1
        
        create_tables()
    except Exception as e:
        return 1
    
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)