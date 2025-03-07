import pandas as pd
import logging
from pathlib import Path
import psycopg
from toast_exports.utils.name_formatter import format_name

logger = logging.getLogger(__name__)

def process_orders(conn):
    """
    Process orders from CSV file and insert into database.
    
    Parameters:
    - conn: psycopg connection object
    """
    sample_data_path = Path('sample_data/20240410/OrderDetails.csv')
    
    logger.info("Reading orders data...")
    df = pd.read_csv(sample_data_path)
    
    # First, ensure we have the location in the locations table
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO locations (location) VALUES (%s) ON CONFLICT (location) DO NOTHING",
                (df['Location'].iloc[0],)
            )
            conn.commit()
            
            # Get the location_id
            cursor.execute("SELECT id FROM locations WHERE location = %s", (df['Location'].iloc[0],))
            location_id = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error setting up location: {str(e)}")
            conn.rollback()
            raise
    
    inserted_count = 0
    skipped_count = 0
    error_count = 0
    
    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            try:
                # Format server name consistently
                server_name = format_name(row['Server'])
                
                # First, ensure the server exists in employees table
                cursor.execute(
                    """
                    INSERT INTO employees (employee_id, employee_guid, employee_name) 
                    VALUES (%s, uuid_generate_v4(), %s)
                    ON CONFLICT (employee_name) DO NOTHING
                    RETURNING id
                    """,
                    (0, server_name)  # Using 0 as a placeholder employee_id
                )
                result = cursor.fetchone()
                if result:
                    server_id = result[0]
                else:
                    # Get the existing server_id
                    cursor.execute("SELECT id FROM employees WHERE employee_name = %s", (server_name,))
                    server_id = cursor.fetchone()[0]
                
                # Convert string dates to timestamps
                opened_at = pd.to_datetime(row['Opened'])
                closed_at = pd.to_datetime(row['Closed']) if pd.notna(row['Closed']) else None
                paid_at = pd.to_datetime(row['Paid']) if pd.notna(row['Paid']) else None

                # Calculate duration in minutes
                duration_minutes = None
                if pd.notna(row['Duration (Opened to Paid)']):
                    duration_str = row['Duration (Opened to Paid)']
                    hours, minutes, seconds = map(int, duration_str.split(':'))
                    duration_minutes = hours * 60 + minutes
                
                # Insert order
                cursor.execute("""
                    INSERT INTO orders (
                        location_id, order_id, order_number, opened_at, closed_at, paid_at,
                        guest_count, tab_names, server_id, table_number, revenue_center,
                        dining_area, service_period, dining_option, discount_amount,
                        subtotal, tax, tip, gratuity, total, is_voided,
                        duration_minutes, order_source
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (order_id) DO NOTHING
                    RETURNING id
                """, (
                    location_id,
                    int(row['Order Id']),
                    row['Order #'],
                    opened_at,
                    closed_at,
                    paid_at,
                    row['# of Guests'],
                    row['Tab Names'],
                    server_id,
                    row['Table'],
                    row['Revenue Center'],
                    row['Dining Area'],
                    row['Service'],
                    row['Dining Options'],
                    row['Discount Amount'],
                    row['Amount'],
                    row['Tax'],
                    row['Tip'],
                    row['Gratuity'],
                    row['Total'],
                    row['Voided'],
                    duration_minutes,
                    row['Order Source']
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                    logger.debug(f"Inserted order: {row['Order #']}")
                else:
                    skipped_count += 1
                    logger.debug(f"Order already exists (skipped): {row['Order #']}")
                conn.commit()
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing order {row.get('Order #', 'unknown')}: {str(e)}")
                conn.rollback()
    
    logger.info(f"Orders processing complete. {inserted_count} inserted, {skipped_count} skipped, {error_count} errors")

def import_order(conn, row):
    """
    Import a single order and return its id.
    """
    with conn.cursor() as cur:
        try:
            # Get location_id
            cur.execute("SELECT id FROM locations WHERE location = %s", (row['Location'],))
            location_id = cur.fetchone()
            if not location_id:
                logger.error(f"Error: Location not found: {row['Location']}")
                return None

            # Get server_id using formatted name
            if pd.notna(row['Server']):
                formatted_name = format_name(row['Server'])
                cur.execute("SELECT id FROM employees WHERE employee_name = %s", (formatted_name,))
                server_id = cur.fetchone()
                if not server_id:
                    logger.error(f"Error: Server not found in employees table: {formatted_name} (original: {row['Server']})")
                    return None
                server_id = server_id[0]
            else:
                logger.error(f"Error: No server specified for order {row['Order Id']}")
                return None

            # Convert string dates to timestamps
            opened_at = pd.to_datetime(row['Opened'])
            closed_at = pd.to_datetime(row['Closed']) if pd.notna(row['Closed']) else None
            paid_at = pd.to_datetime(row['Paid']) if pd.notna(row['Paid']) else None

            # Calculate duration in minutes
            duration_minutes = None
            if pd.notna(row['Duration (Opened to Paid)']):
                duration_str = row['Duration (Opened to Paid)']
                hours, minutes, seconds = map(int, duration_str.split(':'))
                duration_minutes = hours * 60 + minutes

            # Insert order
            cur.execute("""
                INSERT INTO orders (
                    location_id, order_id, order_number, opened_at, closed_at, paid_at,
                    guest_count, tab_names, server_id, table_number, revenue_center,
                    dining_area, service_period, dining_option, discount_amount,
                    subtotal, tax, tip, gratuity, total, is_voided,
                    duration_minutes, order_source
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (order_id) DO NOTHING
                RETURNING id
            """, (
                location_id[0],
                int(row['Order Id']),
                row['Order #'],
                opened_at,
                closed_at,
                paid_at,
                row['# of Guests'],
                row['Tab Names'],
                server_id,
                row['Table'],
                row['Revenue Center'],
                row['Dining Area'],
                row['Service'],
                row['Dining Options'],
                row['Discount Amount'],
                row['Amount'],
                row['Tax'],
                row['Tip'],
                row['Gratuity'],
                row['Total'],
                row['Voided'],
                duration_minutes,
                row['Order Source']
            ))
            
            result = cur.fetchone()
            if result:
                logger.info(f"Info: Inserted new order: {row['Order #']}")
                return result[0]
            else:
                logger.info(f"Info: Order already exists (skipped): {row['Order #']}")
                return None

        except Exception as e:
            logger.error(f"Error inserting order {row['Order Id']}: {str(e)}")
            raise

def import_check(conn, row, order_id):
    """
    Import a single check associated with an order.
    Returns True if check was inserted, False if skipped.
    """
    with conn.cursor() as cur:
        try:
            # Convert date and time strings to proper formats
            opened_date = pd.to_datetime(row['Opened Date']).date() if pd.notna(row['Opened Date']) else None
            opened_time = pd.to_datetime(row['Opened Time']).time() if pd.notna(row['Opened Time']) else None

            # Insert check
            cur.execute("""
                INSERT INTO checks (
                    order_id, check_id, check_number, customer_id, customer_name,
                    customer_phone, customer_email, customer_family, location_code,
                    opened_date, opened_time, item_description, table_size,
                    discount, discount_reason, tax, tender, total, receipt_link
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (order_id, check_number) DO NOTHING
                RETURNING id
            """, (
                order_id,
                int(row['Check Id']),
                row['Check #'],
                row['Customer Id'],
                row['Customer'],
                row['Customer Phone'],
                row['Customer Email'],
                row['Customer Family'],
                row['Location Code'],
                opened_date,
                opened_time,
                row['Item Description'],
                row['Table Size'],
                row['Discount'],
                row['Reason of Discount'],
                row['Tax'],
                row['Tender'],
                row['Total'],
                row['Link']
            ))
            
            result = cur.fetchone()
            if result:
                logger.info(f"Info: Inserted new check: {row['Check #']}")
                return True
            else:
                logger.info(f"Info: Check already exists (skipped): {row['Check #']}")
                return False

        except Exception as e:
            logger.error(f"Error inserting check {row['Check Id']}: {str(e)}")
            raise 