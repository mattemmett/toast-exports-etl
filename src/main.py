import os
from src.filehandlers import import_time_entries
from src.utils import load_env_variables
from src.database import create_connection

def main():
    # Load environment variables
    load_env_variables()

    # Ensure TimeEntries.csv is processed first
    import_time_entries()
    # Add other ETL workflow steps here

if __name__ == "__main__":
    main()
