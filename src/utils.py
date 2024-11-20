import os
from dotenv import load_dotenv

def load_env_variables():
    load_dotenv()
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    return db_host, db_user, db_password, db_name
