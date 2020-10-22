import os
import time
from dotenv import load_dotenv
import json

def run():
    # Import enviromental variables
    load_dotenv(dotenv_path='src/variables.env')
    
    # Init database
    from database import Database
    database = Database(os.getenv('DATABASE_NAME'))

    # Create default access
    error, code, results = database.find(os.getenv('CLIENTS_COLLECTION'),'')
    if len(list(results)) == 0:
        default_client = json.load(open(os.getenv('DEFAULT_TOKEN')))
        error, code = database.insert_one(os.getenv('CLIENTS_COLLECTION'), default_client)
        if error:
            print('Default client not created!')
            return 
        print('Default client created!')

    # Start server
    from server import server
    server(database)

if __name__ == "__main__":
    run()
