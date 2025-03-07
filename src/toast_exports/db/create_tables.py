import logging
import psycopg

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
        if "CREATE TABLE" in sql:
            logger.info(f"Info: {description} (table already exists or was created)")
        elif "CREATE EXTENSION" in sql:
            logger.info(f"Info: {description} (extension already exists or was created)")
    except psycopg.Error as e:
        logger.error(f"Error {description}: {str(e)}")
        raise

def create_tables(conn):
    """
    Create all necessary database tables if they don't exist.
    
    Parameters:
    - conn: psycopg connection object
    """
    try:
        with conn.cursor() as cur:
            # Create UUID extension
            execute_with_error_handling(
                cur,
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
                "created UUID extension"
            )

            # Create locations table first (referenced by other tables)
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS locations (
                    id SERIAL PRIMARY KEY,
                    location VARCHAR(255) UNIQUE NOT NULL
                );
                """,
                "created locations table"
            )

            # Create jobs table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    job_id BIGINT UNIQUE NOT NULL,
                    job_guid UUID UNIQUE NOT NULL,
                    job_code VARCHAR(50),
                    job_title VARCHAR(255) NOT NULL
                );
                """,
                "created jobs table"
            )
            
            # Create employees table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    employee_id BIGINT UNIQUE NOT NULL,
                    employee_guid UUID UNIQUE NOT NULL,
                    employee_external_id VARCHAR(50),
                    employee_name VARCHAR(255) UNIQUE NOT NULL
                );
                """,
                "created employees table"
            )

            # Create menus table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS menus (
                    guid UUID PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT DEFAULT '',
                    id_string VARCHAR(50) NOT NULL,
                    orderable_online BOOLEAN NOT NULL DEFAULT TRUE,
                    orderable_online_status VARCHAR(10) DEFAULT 'YES',
                    visibility VARCHAR(10) DEFAULT 'ALL',
                    start_time BIGINT DEFAULT NULL,
                    end_time BIGINT DEFAULT NULL,
                    start_time_hhmm VARCHAR(5) DEFAULT NULL,
                    end_time_hhmm VARCHAR(5) DEFAULT NULL,
                    start_time_local_standard_time BIGINT DEFAULT NULL,
                    end_time_local_standard_time BIGINT DEFAULT NULL,
                    start_time_hhmm_local_standard_time VARCHAR(5) DEFAULT NULL,
                    end_time_hhmm_local_standard_time VARCHAR(5) DEFAULT NULL,
                    available_all_times BOOLEAN NOT NULL DEFAULT TRUE,
                    available_all_days BOOLEAN NOT NULL DEFAULT TRUE,
                    days_available_bits SMALLINT DEFAULT 127,
                    days_available_string TEXT[] DEFAULT NULL
                );
                """,
                "created menus table"
            )

            # Create orders table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    location_id INT NOT NULL,
                    order_id BIGINT UNIQUE NOT NULL,
                    order_number VARCHAR(50) NOT NULL,
                    opened_at TIMESTAMP NOT NULL,
                    closed_at TIMESTAMP,
                    paid_at TIMESTAMP,
                    guest_count INT NOT NULL,
                    tab_names TEXT,
                    server_id INT NOT NULL,
                    table_number VARCHAR(50),
                    revenue_center VARCHAR(100),
                    dining_area VARCHAR(100),
                    service_period VARCHAR(50),
                    dining_option VARCHAR(100),
                    discount_amount NUMERIC(10,2) DEFAULT 0,
                    subtotal NUMERIC(10,2) NOT NULL,
                    tax NUMERIC(10,2) NOT NULL,
                    tip NUMERIC(10,2) DEFAULT 0,
                    gratuity NUMERIC(10,2) DEFAULT 0,
                    total NUMERIC(10,2) NOT NULL,
                    is_voided BOOLEAN DEFAULT FALSE,
                    duration_minutes INT,
                    order_source VARCHAR(50),
                    CONSTRAINT fk_location 
                        FOREIGN KEY (location_id) 
                        REFERENCES locations (id) 
                        ON DELETE CASCADE,
                    CONSTRAINT fk_server
                        FOREIGN KEY (server_id)
                        REFERENCES employees (id)
                        ON DELETE CASCADE
                );
                """,
                "created orders table"
            )

            # Create checks table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id SERIAL PRIMARY KEY,
                    order_id INT NOT NULL,
                    check_id BIGINT UNIQUE NOT NULL,
                    check_number VARCHAR(50) NOT NULL,
                    customer_id VARCHAR(100),
                    customer_name VARCHAR(255),
                    customer_phone VARCHAR(50),
                    customer_email VARCHAR(255),
                    customer_family VARCHAR(255),
                    location_code VARCHAR(50),
                    opened_date DATE,
                    opened_time TIME,
                    item_description TEXT,
                    table_size INT,
                    discount NUMERIC(10,2) DEFAULT 0,
                    discount_reason VARCHAR(255),
                    tax NUMERIC(10,2) DEFAULT 0,
                    tender VARCHAR(50),
                    total NUMERIC(10,2) NOT NULL,
                    receipt_link TEXT,
                    CONSTRAINT fk_order 
                        FOREIGN KEY (order_id) 
                        REFERENCES orders (id) 
                        ON DELETE CASCADE,
                    UNIQUE(order_id, check_number)
                );
                """,
                "created checks table"
            )

            # Create time entries table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS time_entries (
                    id SERIAL PRIMARY KEY,
                    location_id INT NOT NULL,
                    employee_id INT NOT NULL,
                    job_id INT NOT NULL,
                    in_date TIMESTAMP NOT NULL,
                    out_date TIMESTAMP NOT NULL,
                    auto_clock_out BOOLEAN NOT NULL,
                    total_hours NUMERIC(5, 2) NOT NULL,
                    unpaid_break_time NUMERIC(5, 2),
                    paid_break_time NUMERIC(5, 2),
                    payable_hours NUMERIC(5, 2) NOT NULL,
                    cash_tips_declared NUMERIC(10, 2),
                    non_cash_tips NUMERIC(10, 2),
                    total_gratuity NUMERIC(10, 2),
                    total_tips NUMERIC(10, 2),
                    tips_withheld NUMERIC(10, 2),
                    wage NUMERIC(10, 2) NOT NULL,
                    regular_hours NUMERIC(5, 2),
                    overtime_hours NUMERIC(5, 2),
                    regular_pay NUMERIC(10, 2),
                    overtime_pay NUMERIC(10, 2),
                    total_pay NUMERIC(10, 2) NOT NULL,
                    CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE,
                    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
                    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
                    UNIQUE(employee_id, in_date)
                );
                """,
                "created time_entries table"
            )
            conn.commit()
            logger.info("All tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        conn.rollback()
        raise
