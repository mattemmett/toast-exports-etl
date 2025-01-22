import psycopg

def create_table_menus(conn):
    """
    Create the `menus` table if it doesn't exist. This table stores menu information with
    details such as name, description, availability, and visibility settings.
    """
    with conn.cursor() as cur:
        cur.execute("""
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
        """)

def create_tables_time_entries(conn):
    """
    Create the `locations` and `employees` tables if they don't exist. These tables store
    information about work locations and employees, respectively.
    """
    with conn.cursor() as cur:
        # Create the `locations` table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                location VARCHAR(255) UNIQUE NOT NULL
            );
        """)

        # Create the jobs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,                  -- Auto-incrementing unique identifier
                job_id BIGINT UNIQUE NOT NULL,          -- Job Id from the input data
                job_guid UUID UNIQUE NOT NULL,          -- Job GUID
                job_code VARCHAR(50),                   -- Job code
                job_title VARCHAR(255) NOT NULL        -- Job title
            );
        """)
        
        # Create the `employees` table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,              -- Auto-incrementing unique identifier
                employee_id BIGINT UNIQUE NOT NULL, -- Employee Id from the input data
                employee_guid UUID UNIQUE NOT NULL, -- Employee GUID
                employee_external_id VARCHAR(50),   -- Employee External Id (optional)
                employee_name VARCHAR(255) NOT NULL -- Employee name
            );
        """)

        # Create the time_entries table
        cur.execute("""
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
        """)

        conn.commit()

def create_tables(conn):
    """
    Orchestrate the creation of all required tables: menus, locations, and employees.
    """
    create_table_menus(conn)
    create_tables_time_entries(conn)
