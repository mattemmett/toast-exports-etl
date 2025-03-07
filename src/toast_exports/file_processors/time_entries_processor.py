import pandas as pd
import logging
from pathlib import Path
import psycopg
from toast_exports.utils.name_formatter import format_name

logger = logging.getLogger(__name__)

def process_time_entries(conn):
    """
    Process time entries from CSV file and insert into database.
    
    Parameters:
    - conn: psycopg connection object
    """
    sample_data_path = Path('sample_data/20240410/TimeEntries.csv')
    
    logger.info("Reading time entries data...")
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
                # Format employee name consistently
                employee_name = format_name(row['Employee'])
                
                # Ensure job exists
                cursor.execute(
                    """
                    INSERT INTO jobs (job_id, job_guid, job_code, job_title)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (job_id) DO NOTHING
                    RETURNING id
                    """,
                    (row['Job Id'], row['Job GUID'], row['Job Code'], row['Job Title'])
                )
                result = cursor.fetchone()
                if result:
                    job_id = result[0]
                else:
                    # Get existing job_id
                    cursor.execute("SELECT id FROM jobs WHERE job_id = %s", (row['Job Id'],))
                    job_id = cursor.fetchone()[0]
                
                # Get or create employee
                cursor.execute(
                    """
                    SELECT id FROM employees 
                    WHERE employee_id = %s 
                    OR employee_guid = %s 
                    OR employee_name = %s
                    """,
                    (str(row['Employee Id']), row['Employee GUID'], employee_name)
                )
                result = cursor.fetchone()
                
                if result:
                    employee_id = result[0]
                    # Update employee record with any missing information
                    cursor.execute(
                        """
                        UPDATE employees 
                        SET 
                            employee_id = %s,
                            employee_guid = %s,
                            employee_external_id = %s,
                            employee_name = %s
                        WHERE id = %s
                        """,
                        (row['Employee Id'], row['Employee GUID'], 
                         str(row['Employee External Id']), employee_name, employee_id)
                    )
                else:
                    # Create new employee
                    cursor.execute(
                        """
                        INSERT INTO employees (employee_id, employee_guid, employee_external_id, employee_name)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """,
                        (row['Employee Id'], row['Employee GUID'], 
                         str(row['Employee External Id']), employee_name)
                    )
                    employee_id = cursor.fetchone()[0]
                
                # Insert time entry
                cursor.execute("""
                    INSERT INTO time_entries (
                        location_id, employee_id, job_id, in_date, out_date,
                        auto_clock_out, total_hours, unpaid_break_time,
                        paid_break_time, payable_hours, cash_tips_declared,
                        non_cash_tips, total_gratuity, total_tips,
                        tips_withheld, wage, regular_hours, overtime_hours,
                        regular_pay, overtime_pay, total_pay
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (employee_id, in_date) DO NOTHING
                    RETURNING id
                """, (
                    location_id,
                    employee_id,
                    job_id,
                    pd.to_datetime(row['In Date']),
                    pd.to_datetime(row['Out Date']),
                    row['Auto Clock-out'],
                    row['Total Hours'],
                    row['Unpaid Break Time'],
                    row['Paid Break Time'],
                    row['Payable Hours'],
                    row['Cash Tips Declared'],
                    row['Non Cash Tips'],
                    row['Total Gratuity'],
                    row['Total Tips'],
                    row['Tips Withheld'],
                    row['Wage'],
                    row['Regular Hours'],
                    row['Overtime Hours'],
                    row['Regular Pay'],
                    row['Overtime Pay'],
                    row['Total Pay']
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                    logger.debug(f"Inserted time entry for: {employee_name}")
                else:
                    skipped_count += 1
                    logger.debug(f"Time entry already exists (skipped) for: {employee_name}")
                conn.commit()
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing time entry for {employee_name if 'employee_name' in locals() else 'unknown'}: {str(e)}")
                conn.rollback()
    
    logger.info(f"Time entries processing complete. {inserted_count} inserted, {skipped_count} skipped, {error_count} errors")
