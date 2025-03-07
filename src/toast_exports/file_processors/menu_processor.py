import psycopg
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def insert_menus_into_db(conn):
    """
    Inserts menu data into the 'menus' table in the database.

    Parameters:
    - connection: A psycopg3 database connection object (used with a `with` statement).
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
    
    sample_data_path = Path('sample_data/20240410/MenuExport_adddeea2-4ff3-46e6-840b-5b8fa9fad1db.json')
    with open(sample_data_path, 'r') as file:
        data = json.load(file)
    
    logger.info(f"Processing {len(data)} menu items")
    inserted_count = 0
    skipped_count = 0
    
    with conn.cursor() as cursor:
        for menu in data:
            try:
                cursor.execute(insert_menus_sql, menu)
                if cursor.rowcount > 0:
                    inserted_count += 1
                    logger.info(f"Info: Inserted new menu item: {menu['name']}")
                else:
                    skipped_count += 1
                    logger.info(f"Info: Menu item already exists (skipped): {menu['name']}")
                conn.commit()
            except Exception as e:
                logger.error(f"Error processing menu item {menu.get('name', 'unknown')}: {str(e)}")
                conn.rollback()
    
    logger.info(f"Menu processing complete. {inserted_count} items inserted, {skipped_count} items already existed")