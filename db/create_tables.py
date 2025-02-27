import psycopg
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        logger.error(f"Error {description}: {str(e)}")
        raise

def create_table_menus(conn):
    """
    Create the `menus` table if it doesn't exist. This table stores menu information with
    details such as name, description, availability, and visibility settings.
    """
    try:
        with conn.cursor() as cur:
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS menus (
                    guid UUID PRIMARY KEY,                       -- Unique identifier as the primary key
                    name VARCHAR(100) NOT NULL,                 -- Name (e.g., "Soft Drinks")
                    description TEXT DEFAULT '',                -- Description (optional, default empty string)
                    id_string VARCHAR(50) NOT NULL,             -- Identifier as a string
                    orderable_online BOOLEAN NOT NULL DEFAULT TRUE, -- Indicates if orderable online
                    orderable_online_status VARCHAR(10) DEFAULT 'YES', -- Online status
                    visibility VARCHAR(10) DEFAULT 'ALL',       -- Visibility status
                    start_time BIGINT DEFAULT NULL,             -- Start time in milliseconds
                    end_time BIGINT DEFAULT NULL,               -- End time in milliseconds
                    start_time_hhmm VARCHAR(5) DEFAULT NULL,    -- Start time in HH:mm format
                    end_time_hhmm VARCHAR(5) DEFAULT NULL,      -- End time in HH:mm format
                    start_time_local_standard_time BIGINT DEFAULT NULL, -- Start time in milliseconds (local standard time)
                    end_time_local_standard_time BIGINT DEFAULT NULL,   -- End time in milliseconds (local standard time)
                    start_time_hhmm_local_standard_time VARCHAR(5) DEFAULT NULL, -- Start time in HH:mm (local standard)
                    end_time_hhmm_local_standard_time VARCHAR(5) DEFAULT NULL,   -- End time in HH:mm (local standard)
                    available_all_times BOOLEAN NOT NULL DEFAULT TRUE, -- Indicates if available all times
                    available_all_days BOOLEAN NOT NULL DEFAULT TRUE,  -- Indicates if available all days
                    days_available_bits SMALLINT DEFAULT 127,          -- Bitmask indicating available days (0-127)
                    days_available_string TEXT[] DEFAULT NULL          -- Array of days (e.g., ["Mon"])
                );
                """,
                "created menus table"
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to create menus table: {str(e)}")
        conn.rollback()
        raise

def create_tables_time_entries(conn):
    """
    Create the `locations` and `employees` tables if they don't exist. These tables store
    information about work locations and employees, respectively.
    """
    try:
        with conn.cursor() as cur:
            # Create the `locations` table
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

            # Create the jobs table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,                  -- Auto-incrementing unique identifier
                    job_id BIGINT UNIQUE NOT NULL,          -- Job Id from the input data
                    job_guid UUID UNIQUE NOT NULL,          -- Job GUID
                    job_code VARCHAR(50),                   -- Job code
                    job_title VARCHAR(255) NOT NULL        -- Job title
                );
                """,
                "created jobs table"
            )
            
            # Create the `employees` table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,              -- Auto-incrementing unique identifier
                    employee_id BIGINT UNIQUE NOT NULL, -- Employee Id from the input data
                    employee_guid UUID UNIQUE NOT NULL, -- Employee GUID
                    employee_external_id VARCHAR(50),   -- Employee External Id (optional)
                    employee_name VARCHAR(255) NOT NULL -- Employee name
                );
                """,
                "created employees table"
            )

            # Create the time_entries table
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS time_entries (
                    id SERIAL PRIMARY KEY,                     -- Auto-incrementing unique identifier
                    location_id INT NOT NULL,                  -- Foreign key to locations table
                    employee_id INT NOT NULL,                  -- Foreign key to employees table
                    job_id INT NOT NULL,                       -- Foreign key to jobs table
                    in_date TIMESTAMP NOT NULL,                -- Clock-in time
                    out_date TIMESTAMP NOT NULL,               -- Clock-out time
                    auto_clock_out BOOLEAN NOT NULL,           -- Auto clock-out status
                    total_hours NUMERIC(5, 2) NOT NULL,        -- Total hours worked
                    unpaid_break_time NUMERIC(5, 2),           -- Unpaid break time
                    paid_break_time NUMERIC(5, 2),             -- Paid break time
                    payable_hours NUMERIC(5, 2) NOT NULL,      -- Payable hours
                    cash_tips_declared NUMERIC(10, 2),         -- Declared cash tips
                    non_cash_tips NUMERIC(10, 2),              -- Non-cash tips
                    total_gratuity NUMERIC(10, 2),             -- Total gratuity
                    total_tips NUMERIC(10, 2),                 -- Total tips
                    tips_withheld NUMERIC(10, 2),              -- Withheld tips
                    wage NUMERIC(10, 2) NOT NULL,              -- Wage
                    regular_hours NUMERIC(5, 2),               -- Regular hours worked
                    overtime_hours NUMERIC(5, 2),              -- Overtime hours worked
                    regular_pay NUMERIC(10, 2),                -- Regular pay
                    overtime_pay NUMERIC(10, 2),               -- Overtime pay
                    total_pay NUMERIC(10, 2) NOT NULL,         -- Total pay
                    CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE,
                    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE,
                    CONSTRAINT fk_job FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
                );
                """,
                "created time_entries table"
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to create time entries tables: {str(e)}")
        conn.rollback()
        raise

def create_tables_orders(conn):
    """
    Create the orders and checks tables if they don't exist.
    These tables store information about orders and their associated checks.
    """
    try:
        with conn.cursor() as cur:
            # Create orders table
            execute_with_error_handling(
                cur,
                """
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,                      -- Auto-incrementing unique identifier
                    location_id INT NOT NULL,                   -- Foreign key to locations table
                    order_id BIGINT UNIQUE NOT NULL,            -- Order Id from the input data
                    order_number VARCHAR(50) NOT NULL,          -- Order # from input
                    opened_at TIMESTAMP NOT NULL,               -- When order was opened
                    closed_at TIMESTAMP,                        -- When order was closed
                    paid_at TIMESTAMP,                          -- When order was paid
                    guest_count INT NOT NULL,                   -- Number of guests
                    tab_names TEXT,                            -- Tab names (optional)
                    server_id INT NOT NULL,                     -- Foreign key to employees table
                    table_number VARCHAR(50),                   -- Table number (optional)
                    revenue_center VARCHAR(100),                -- Revenue center
                    dining_area VARCHAR(100),                   -- Dining area
                    service_period VARCHAR(50),                 -- Service period (e.g., Dinner, Late Night)
                    dining_option VARCHAR(100),                 -- Dining options
                    discount_amount NUMERIC(10,2) DEFAULT 0,    -- Discount amount
                    subtotal NUMERIC(10,2) NOT NULL,            -- Amount before tax/tip
                    tax NUMERIC(10,2) NOT NULL,                 -- Tax amount
                    tip NUMERIC(10,2) DEFAULT 0,                -- Tip amount
                    gratuity NUMERIC(10,2) DEFAULT 0,           -- Gratuity amount
                    total NUMERIC(10,2) NOT NULL,               -- Total amount
                    is_voided BOOLEAN DEFAULT FALSE,            -- Voided status
                    duration_minutes INT,                       -- Duration in minutes
                    order_source VARCHAR(50),                   -- Order source (e.g., In Store)
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

            # Updated checks table with additional fields
            execute_with_error_handling(
                cur,
                """
                CREATE TABLE IF NOT EXISTS checks (
                    id SERIAL PRIMARY KEY,                      -- Auto-incrementing unique identifier
                    order_id INT NOT NULL,                      -- Foreign key to orders table
                    check_id BIGINT UNIQUE NOT NULL,            -- Check Id from the input data
                    check_number VARCHAR(50) NOT NULL,          -- Check number
                    customer_id VARCHAR(100),                   -- Customer Id (optional)
                    customer_name VARCHAR(255),                 -- Customer name (optional)
                    customer_phone VARCHAR(50),                 -- Customer phone (optional)
                    customer_email VARCHAR(255),                -- Customer email (optional)
                    customer_family VARCHAR(255),               -- Customer family (optional)
                    location_code VARCHAR(50),                  -- Location code
                    opened_date DATE,                          -- Opened date
                    opened_time TIME,                          -- Opened time
                    item_description TEXT,                      -- Items ordered description
                    table_size INT,                            -- Table size
                    discount NUMERIC(10,2) DEFAULT 0,          -- Discount amount
                    discount_reason VARCHAR(255),              -- Reason for discount
                    tax NUMERIC(10,2) DEFAULT 0,               -- Tax amount
                    tender VARCHAR(50),                        -- Payment method (Cash, Visa, etc.)
                    total NUMERIC(10,2) NOT NULL,              -- Total amount
                    receipt_link TEXT,                         -- Link to receipt
                    CONSTRAINT fk_order 
                        FOREIGN KEY (order_id) 
                        REFERENCES orders (id) 
                        ON DELETE CASCADE,
                    UNIQUE(order_id, check_number)              -- Each check number must be unique per order
                );
                """,
                "created checks table"
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to create orders tables: {str(e)}")
        conn.rollback()
        raise

def create_tables(conn):
    """
    Orchestrate the creation of all required tables
    """
    try:
        logger.info("Starting table creation process")
        create_table_menus(conn)
        create_tables_time_entries(conn)
        create_tables_orders(conn)
        logger.info("Successfully created all tables")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        raise
