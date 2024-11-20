import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def import_time_entries():
    # Load environment variables from .env file
    load_dotenv()

    # Load the CSV file into a DataFrame
    csv_file_path = 'samaple-data/20240410/TimeEntries.csv'
    df = pd.read_csv(csv_file_path)

    # Convert relevant columns to datetime format
    df['In Date'] = pd.to_datetime(df['In Date'], format='%m/%d/%y %I:%M %p')
    df['Out Date'] = pd.to_datetime(df['Out Date'], format='%m/%d/%y %I:%M %p')

    # Convert datetime columns to strings formatted for MySQL
    df['In Date'] = df['In Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['Out Date'] = df['Out Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convert 'Auto Clock-out' to boolean
    df['Auto Clock-out'] = df['Auto Clock-out'].astype(bool)

    # Connect to MySQL
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()

            # SQL statement to insert data
            sql_insert_query = """
            INSERT INTO TimeEntries 
            (Location, LocationCode, Id, GUID, EmployeeId, EmployeeGUID, EmployeeExternalId, EmployeeName, 
            JobId, JobGUID, JobCode, JobTitle, InDate, OutDate, AutoClockOut, TotalHours, UnpaidBreakTime, 
            PaidBreakTime, PayableHours, CashTipsDeclared, NonCashTips, TotalGratuity, TotalTips, TipsWithheld, 
            Wage, RegularHours, OvertimeHours, RegularPay, OvertimePay, TotalPay)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Insert DataFrame records one by one
            for index, row in df.iterrows():
                record_tuple = (
                    row['Location'], row['Location Code'], row['Id'], row['GUID'], row['Employee Id'], 
                    row['Employee GUID'], row['Employee External Id'], row['Employee'], row['Job Id'], 
                    row['Job GUID'], row['Job Code'], row['Job Title'], row['In Date'], row['Out Date'], 
                    row['Auto Clock-out'], row['Total Hours'], row['Unpaid Break Time'], row['Paid Break Time'], 
                    row['Payable Hours'], row['Cash Tips Declared'], row['Non Cash Tips'], row['Total Gratuity'], 
                    row['Total Tips'], row['Tips Withheld'], row['Wage'], row['Regular Hours'], 
                    row['Overtime Hours'], row['Regular Pay'], row['Overtime Pay'], row['Total Pay']
                )
                
                try:
                    cursor.execute(sql_insert_query, record_tuple)
                except Error as e:
                    print(f"Error inserting row {index}: {e}")

            # Commit the transaction
            connection.commit()

            print(f"{cursor.rowcount} rows inserted successfully into TimeEntries table")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
