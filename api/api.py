import os
import time
from dotenv import load_dotenv
import json

def run():
    # Import enviromental variables
    load_dotenv(dotenv_path='api/variables.env')
    
    # Init database
    from database import Database
    database = Database(os.getenv('DATABASE_NAME'))

    # Create default access
    error, results = database.find(os.getenv('CLIENTS_COLLECTION'),'')
    if results and len(list(results)) == 0:
        default_client = json.load(open(os.getenv('DEFAULT_TOKEN')))
        error = database.insert_one(os.getenv('CLIENTS_COLLECTION'), default_client)
        if error:
            print('Default client not created!')
            return 
        print('Default client created!')

    # Create necessary folders
    for dir in [os.getenv('DATASETS_PATH'), os.getenv('INPUT_PATH'), os.getenv('OUTPUT_PATH'), os.getenv('ZIP_PATH'), os.getenv('STORAGE_PATH')]:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # Start server
    from server import server
    server(database)

if __name__ == "__main__":
    run()
