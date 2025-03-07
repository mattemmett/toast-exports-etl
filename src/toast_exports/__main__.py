"""
Main entry point for the toast-exports-etl package.
Can be run with: python -m toast_exports
"""
import logging
import psycopg
from toast_exports.config import DB_URL
from toast_exports.db.create_tables import create_tables
from toast_exports.file_processors.menu_processor import insert_menus_into_db
from toast_exports.file_processors.orders_processor import process_orders
from toast_exports.file_processors.time_entries_processor import process_time_entries

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Connecting to database...")
        with psycopg.connect(DB_URL) as conn:
            # Create tables if they don't exist
            logger.info("Creating tables...")
            create_tables(conn)
            
            # Process data
            logger.info("Processing menu data...")
            insert_menus_into_db(conn)
            
            logger.info("Processing orders data...")
            process_orders(conn)
            
            logger.info("Processing time entries data...")
            process_time_entries(conn)
            
            logger.info("All processing completed successfully!")
            
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main() 