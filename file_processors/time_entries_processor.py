import psycopg
import pandas as pd
import os

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

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            location = row['Location']  # Access the value for 'Location'
            try:
                # Use ON CONFLICT DO NOTHING to handle duplicates at the database level
                cur.execute("""
                    INSERT INTO locations (location)
                    VALUES (%s)
                    ON CONFLICT DO NOTHING
                    """, (location,))
                print(f"Inserted location: {location}")
            except psycopg.errors.UniqueViolation:
                # No rollback needed since ON CONFLICT prevents errors
                print(f"Location already exists: {location}")
        # Commit after processing all rows
        conn.commit()
    print("All locations processed.")


def import_jobs(conn, df):
    job_columns = ['Job Id', 'Job GUID', 'Job Code', 'Job Title']
    jobs_df = df[job_columns].drop_duplicates(subset=['Job Id'])

    with conn.cursor() as cur:
        for _, row in jobs_df.iterrows():
            try:
                # Insert the job into the jobs table
                cur.execute("""
                    INSERT INTO jobs (job_id, job_guid, job_code, job_title)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (job_id) DO NOTHING
                """, (
                    row['Job Id'], row['Job GUID'], row['Job Code'], row['Job Title']
                ))
                print(f"Inserted job: {row['Job Title']}")
            except psycopg.errors.UniqueViolation:
                print(f"Job already exists: {row['Job Title']}")
        conn.commit()
    print("All jobs processed.")

def import_employees(conn, df):
    """
    Processes the unique employees from the DataFrame and inserts them into the employees table.
    """
    # Define the relevant employee columns
    employee_columns = ['Employee Id', 'Employee GUID', 'Employee External Id', 'Employee']

    # Extract unique employees
    employees_df = df[employee_columns].drop_duplicates(subset=['Employee Id'])

    with conn.cursor() as cur:
        for _, row in employees_df.iterrows():
            try:
                # Insert employee data into the employees table
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
                print(f"Inserted employee: {row['Employee']}")
            except psycopg.errors.UniqueViolation:
                print(f"Employee already exists: {row['Employee']}")
        # Commit after processing all rows
        conn.commit()
    print("All employees processed.")

def import_time_entries(conn, df):
    """
    Processes and inserts time entries into the time_entries table.
    Links time entries to their respective location, employee, and job.
    """
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            try:
                # Fetch location_id
                cur.execute("SELECT id FROM locations WHERE location = %s", (row['Location'],))
                location_id = cur.fetchone()
                if location_id:
                    location_id = location_id[0]
                else:
                    print(f"Location not found for time entry: {row['Location']}")
                    continue

                # Fetch employee_id
                cur.execute("SELECT id FROM employees WHERE employee_id = %s", (row['Employee Id'],))
                employee_id = cur.fetchone()
                if employee_id:
                    employee_id = employee_id[0]
                else:
                    print(f"Employee not found for time entry: {row['Employee']}")
                    continue

                # Fetch job_id
                cur.execute("SELECT id FROM jobs WHERE job_id = %s", (row['Job Id'],))
                job_id = cur.fetchone()
                if job_id:
                    job_id = job_id[0]
                else:
                    print(f"Job not found for time entry: {row['Job Title']}")
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
                    location_id, employee_id, job_id,
                    row['In Date'], row['Out Date'], row['Auto Clock-out'] == 'Yes',
                    row['Total Hours'], row['Unpaid Break Time'], row['Paid Break Time'], row['Payable Hours'],
                    row['Cash Tips Declared'], row['Non Cash Tips'], row['Total Gratuity'], row['Total Tips'], row['Tips Withheld'],
                    row['Wage'], row['Regular Hours'], row['Overtime Hours'],
                    row['Regular Pay'], row['Overtime Pay'], row['Total Pay']
                ))
                print(f"Inserted time entry for employee: {row['Employee']}")
            except Exception as e:
                print(f"Error inserting time entry for employee: {row['Employee']} - {e}")
        # Commit the transaction after processing all rows
        conn.commit()
    print("All time entries processed.")
