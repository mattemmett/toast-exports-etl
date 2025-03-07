import psycopg
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def execute_with_error_handling(cur, sql, description):
    """
    Execute SQL with error handling and logging.
    """
    try:
        cur.execute(sql)
        logger.info(f"Successfully {description}")
    except psycopg.Error as e:
        if "does not exist" in str(e):
            logger.info(f"Info: {description} (table did not exist)")
        else:
            logger.error(f"Error {description}: {str(e)}")
            raise

def drop_tables(conn):
    """
    Drop all tables in the correct order to handle dependencies.
    """
    with conn.cursor() as cur:
        try:
            # Drop checks table first (because it depends on orders)
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS checks CASCADE;
                """,
                "dropped checks table"
            )

            # Drop orders table (depends on locations and employees)
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS orders CASCADE;
                """,
                "dropped orders table"
            )

            # Drop time_entries table (depends on locations, employees, and jobs)
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS time_entries CASCADE;
                """,
                "dropped time_entries table"
            )

            # Drop jobs table
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS jobs CASCADE;
                """,
                "dropped jobs table"
            )

            # Drop employees table
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS employees CASCADE;
                """,
                "dropped employees table"
            )

            # Drop locations table
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS locations CASCADE;
                """,
                "dropped locations table"
            )

            # Drop menus table
            execute_with_error_handling(
                cur,
                """
                DROP TABLE IF EXISTS menus CASCADE;
                """,
                "dropped menus table"
            )

            conn.commit()
            logger.info("Successfully dropped all tables")

        except Exception as e:
            conn.rollback()
            logger.error(f"Error dropping tables: {str(e)}")
            raise

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Create connection string
    connection_string = (
        "hostaddr=" + os.getenv('PG_HOST') + " " +
        "dbname=" + os.getenv('PG_DBNAME') + " " +
        "user=" + os.getenv('PG_USER') + " " +
        "password=" + os.getenv('PG_PASSWORD')
    )
    
    # Connect and drop tables
    with psycopg.connect(connection_string) as conn:
        drop_tables(conn) 