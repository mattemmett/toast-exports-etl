import psycopg
import json

def insert_menus_into_db(conn):
    """
    Inserts menu data into the 'menus' table in the database.

    Parameters:
    - connection: A psycopg2 database connection object (used with a `with` statement).
    - data: A list of dictionaries containing menu data.
    """
    insert_menus_sql = """
        INSERT INTO menus (
            guid,
            name,
            description,
            id_string,
            orderable_online,
            orderable_online_status,
            visibility,
            start_time,
            end_time,
            start_time_hhmm,
            end_time_hhmm,
            start_time_local_standard_time,
            end_time_local_standard_time,
            start_time_hhmm_local_standard_time,
            end_time_hhmm_local_standard_time,
            available_all_times,
            available_all_days,
            days_available_bits,
            days_available_string
        ) VALUES (
            %(guid)s,
            %(name)s,
            %(description)s,
            %(idString)s,
            %(orderableOnline)s,
            %(orderableOnlineStatus)s,
            %(visibility)s,
            %(startTime)s,
            %(endTime)s,
            %(startTimeHHmm)s,
            %(endTimeHHmm)s,
            %(startTimeLocalStandardTime)s,
            %(endTimeLocalStandardTime)s,
            %(startTimeHHmmLocalStandardTime)s,
            %(endTimeHHmmLocalStandardTime)s,
            %(availableAllTimes)s,
            %(availableAllDays)s,
            %(daysAvailableBits)s,
            %(daysAvailableString)s
        )
        ON CONFLICT DO NOTHING;
    """
    with open('./samaple-data/20240410/MenuExport_adddeea2-4ff3-46e6-840b-5b8fa9fad1db.json' , 'r') as file:
        data = json.load(file)
    
    with conn.cursor() as cursor:
        # Execute the query for each menu item in the data
            for menu in data:
                try:
                    cursor.execute(insert_menus_sql, menu)
                    print(f"Inserted menu: {menu['name']}")
                except psycopg.errors.UniqueViolation:
                    print(f"Menu with guid {menu['guid']} already exists. Skipping insertion.")
                else:
                    conn.commit()