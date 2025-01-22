import os
from dotenv import load_dotenv
import psycopg
from db import create_tables
from file_processors import menu_processor, time_entries_processor

load_dotenv()

connectionString = (
    "hostaddr=" + os.getenv('PG_HOST') + " " +
    "dbname=" + os.getenv('PG_DBNAME') + " " +
    "user=" + os.getenv('PG_USER') + " " +
    "password=" + os.getenv('PG_PASSWORD')
)

# Connect to an existing database
with psycopg.connect(connectionString) as conn:
    
    # Open a cursor to perform database operations
    create_tables.create_tables(conn)
    menu_processor.insert_menus_into_db(conn)
    time_entries_processor.process_time_entries(conn)
    

    


#with open('samaple-data/20240410/MenuExport_adddeea2-4ff3-46e6-840b-5b8fa9fad1db.json' , 'r') as file:
#    data = json.load(file)










#print(data)
    #print(data[1]['groups'])
#print(len(data[0].keys()))
    #print(data.keys())
    #for i in range(len(data)):
    #    print(data[i]['groups'])
