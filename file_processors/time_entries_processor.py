import psycopg
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def process_time_entries(conn):
    """
    Processes the time entries by importing locations and employees.
    """
    # Read the TimeEntries.csv file into a DataFrame
    with open('./samaple-data/20240410/TimeEntries.csv', 'r') as file:
        df = pd.read_csv(file)

    # Import locations
    import_locations(conn, df)

    # Import jobs
    import_jobs(conn, df)

    # Import employees
    import_employees(conn, df)

    # Import time entries
    import_time_entries(conn, df)


def import_locations(conn, df):
    """
    Processes the unique locations from the DataFrame and inserts them into the locations table.
    """
    # Remove duplicate locations
    df = df.drop_duplicates(subset=['Location'])
    inserted_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            location = row['Location']
            try:
                cur.execute("""
                    INSERT INTO locations (location)
                    VALUES (%s)
                    ON CONFLICT DO NOTHING
                    """, (location,))
                if cur.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"Info: Inserted new location: {location}")
                else:
                    skipped_count += 1
                    logger.info(f"Info: Location already exists (skipped): {location}")
            except Exception as e:
                logger.error(f"Error processing location {location}: {str(e)}")
        conn.commit()
    logger.info(f"Locations processing complete. {inserted_count} inserted, {skipped_count} already existed")


def import_jobs(conn, df):
    job_columns = ['Job Id', 'Job GUID', 'Job Code', 'Job Title']
    jobs_df = df[job_columns].drop_duplicates(subset=['Job Id'])
    inserted_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for _, row in jobs_df.iterrows():
            try:
                cur.execute("""
                    INSERT INTO jobs (job_id, job_guid, job_code, job_title)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (job_id) DO NOTHING
                """, (
                    row['Job Id'], row['Job GUID'], row['Job Code'], row['Job Title']
                ))
                if cur.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"Info: Inserted new job: {row['Job Title']}")
                else:
                    skipped_count += 1
                    logger.info(f"Info: Job already exists (skipped): {row['Job Title']}")
            except Exception as e:
                logger.error(f"Error processing job {row['Job Title']}: {str(e)}")
        conn.commit()
    logger.info(f"Jobs processing complete. {inserted_count} inserted, {skipped_count} already existed")

def import_employees(conn, df):
    """
    Processes the unique employees from the DataFrame and inserts them into the employees table.
    """
    employee_columns = ['Employee Id', 'Employee GUID', 'Employee External Id', 'Employee']
    employees_df = df[employee_columns].drop_duplicates(subset=['Employee Id'])
    inserted_count = 0
    skipped_count = 0

    with conn.cursor() as cur:
        for _, row in employees_df.iterrows():
            try:
                cur.execute("""
                    INSERT INTO employees (employee_id, employee_guid, employee_external_id, employee_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (employee_id) DO NOTHING
                """, (
                    row['Employee Id'],
                    row['Employee GUID'],
                    row['Employee External Id'],
                    row['Employee']
                ))
                if cur.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"Info: Inserted new employee: {row['Employee']}")
                else:
                    skipped_count += 1
                    logger.info(f"Info: Employee already exists (skipped): {row['Employee']}")
            except Exception as e:
                logger.error(f"Error processing employee {row['Employee']}: {str(e)}")
        conn.commit()
    logger.info(f"Employees processing complete. {inserted_count} inserted, {skipped_count} already existed")

def import_time_entries(conn, df):
    """
    Processes and inserts time entries into the time_entries table.
    Links time entries to their respective location, employee, and job.
    """
    processed_count = 0
    error_count = 0

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            try:
                # Fetch location_id
                cur.execute("SELECT id FROM locations WHERE location = %s", (row['Location'],))
                location_id = cur.fetchone()
                if not location_id:
                    logger.warning(f"Info: Location not found for time entry: {row['Location']}")
                    continue

                # Fetch employee_id
                cur.execute("SELECT id FROM employees WHERE employee_id = %s", (row['Employee Id'],))
                employee_id = cur.fetchone()
                if not employee_id:
                    logger.warning(f"Info: Employee not found for time entry: {row['Employee']}")
                    continue

                # Fetch job_id
                cur.execute("SELECT id FROM jobs WHERE job_id = %s", (row['Job Id'],))
                job_id = cur.fetchone()
                if not job_id:
                    logger.warning(f"Info: Job not found for time entry: {row['Job Title']}")
                    continue

                # Insert the time entry
                cur.execute("""
                    INSERT INTO time_entries (
                        location_id, employee_id, job_id, in_date, out_date, auto_clock_out,
                        total_hours, unpaid_break_time, paid_break_time, payable_hours,
                        cash_tips_declared, non_cash_tips, total_gratuity, total_tips, tips_withheld,
                        wage, regular_hours, overtime_hours, regular_pay, overtime_pay, total_pay
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    location_id[0], employee_id[0], job_id[0],
                    row['In Date'], row['Out Date'], row['Auto Clock-out'] == 'Yes',
                    row['Total Hours'], row['Unpaid Break Time'], row['Paid Break Time'], row['Payable Hours'],
                    row['Cash Tips Declared'], row['Non Cash Tips'], row['Total Gratuity'], row['Total Tips'], row['Tips Withheld'],
                    row['Wage'], row['Regular Hours'], row['Overtime Hours'],
                    row['Regular Pay'], row['Overtime Pay'], row['Total Pay']
                ))
                processed_count += 1
                logger.info(f"Info: Processed time entry for employee: {row['Employee']}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing time entry for employee {row['Employee']}: {str(e)}")
        conn.commit()
    logger.info(f"Time entries processing complete. {processed_count} entries processed, {error_count} errors encountered")
