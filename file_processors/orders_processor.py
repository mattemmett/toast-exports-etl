import psycopg
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def process_orders(conn):
    """
    Process orders and their associated checks from CSV files.
    """
    # Read the CSV files
    orders_df = pd.read_csv('./samaple-data/20240410/OrderDetails.csv')
    checks_df = pd.read_csv('./samaple-data/20240410/CheckDetails.csv')
    
    logger.info(f"Loaded {len(orders_df)} orders and {len(checks_df)} checks")
    
    # Process each order and its associated checks
    for _, order_row in orders_df.iterrows():
        try:
            # First insert the order
            order_id = import_order(conn, order_row)
            if not order_id:
                continue
                
            # Get the check numbers for this order
            if pd.isna(order_row['Checks']):
                logger.warning(f"No checks found for order {order_row['Order #']}")
                continue
                
            check_numbers = str(order_row['Checks']).split(',')
            check_numbers = [num.strip() for num in check_numbers]
            
            logger.info(f"Looking for checks: {check_numbers} for order {order_row['Order #']}")
            
            # Process each associated check
            for check_num in check_numbers:
                try:
                    check_num = int(check_num)
                except ValueError:
                    logger.error(f"Could not convert check number {check_num} to integer")
                    continue
                
                matching_checks = checks_df[checks_df['Check #'] == check_num]
                if matching_checks.empty:
                    logger.warning(f"No check found with number {check_num} for order {order_row['Order #']}")
                    continue
                    
                for _, check_row in matching_checks.iterrows():
                    try:
                        import_check(conn, check_row, order_id)
                    except Exception as check_error:
                        logger.error(f"Error processing check {check_num}: {str(check_error)}")
                        raise
                
            conn.commit()
            logger.info(f"Successfully processed order {order_row['Order #']} and its checks")
            
        except Exception as e:
            logger.error(f"Error processing order {order_row['Order #']}: {str(e)}")
            conn.rollback()

def format_server_name(server_name):
    """
    Convert server name from 'Bartender A' format to 'A, Bartender' format
    """
    if not server_name or not isinstance(server_name, str):
        return None
        
    parts = server_name.split()
    if len(parts) < 2:
        return server_name
        
    # Take the last word as the last name, join the rest as first name
    last_name = parts[-1]
    first_name = ' '.join(parts[:-1])
    return f"{last_name}, {first_name}"

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
                logger.error(f"Location not found: {row['Location']}")
                return None
            location_id = location_id[0]

            # Get server_id using formatted name
            if pd.notna(row['Server']):
                formatted_name = format_server_name(row['Server'])
                cur.execute("SELECT id FROM employees WHERE employee_name = %s", (formatted_name,))
                server_id = cur.fetchone()
                if not server_id:
                    logger.error(f"Server not found in employees table: {formatted_name} (original: {row['Server']})")
                    return None
                server_id = server_id[0]
            else:
                logger.warning(f"No server specified for order {row['Order Id']}")
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
            
            order_id = cur.fetchone()[0]
            logger.info(f"Inserted order: {row['Order Id']}")
            return order_id

        except Exception as e:
            logger.error(f"Error inserting order {row['Order Id']}: {str(e)}")
            raise

def import_check(conn, row, order_id):
    """
    Import a single check associated with an order.
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
            logger.info(f"Inserted check: {row['Check Id']} for order id {order_id}")

        except Exception as e:
            logger.error(f"Error inserting check {row['Check Id']}: {str(e)}")
            raise 