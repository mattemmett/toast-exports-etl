import logging
import psycopg
from toast_exports.config import DB_URL

logger = logging.getLogger(__name__)

def drop_tables(conn):
    """
    Drop all tables from the database.
    Tables are dropped in reverse dependency order.
    
    Parameters:
    - conn: psycopg connection object
    """
    tables = [
        "time_entries",
        "checks",
        "orders",
        "menus",
        "employees",
        "jobs",
        "locations"
    ]
    
    with conn.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                conn.commit()
                logger.info(f"Dropped table: {table}")
            except Exception as e:
                logger.error(f"Error dropping table {table}: {str(e)}")
                conn.rollback()
                raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        with psycopg.connect(DB_URL) as conn:
            drop_tables(conn)
            logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        raise 