"""
Configuration settings for the toast-exports-etl package.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv('PG_HOST', 'localhost')
DB_PORT = os.getenv('PG_PORT', '5432')
DB_NAME = os.getenv('PG_DBNAME', 'toast-etl')
DB_USER = os.getenv('PG_USER', 'postgres')
DB_PASSWORD = os.getenv('PG_PASSWORD', '')

# Construct database URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Sample data configuration
SAMPLE_DATA_DIR = Path('sample_data')
CURRENT_DATA_DIR = SAMPLE_DATA_DIR / '20240410'

# Ensure sample data directory exists
SAMPLE_DATA_DIR.mkdir(exist_ok=True)
CURRENT_DATA_DIR.mkdir(exist_ok=True) 