import os
import time
from dotenv import load_dotenv

def run():
    # Import enviromental variables
    load_dotenv(dotenv_path='src/variables.env')
    
    # Init database
    from database import Database
    database = Database(os.getenv('DATABASE_NAME'))

    # Start server
    from server import server
    server(database)

if __name__ == "__main__":
    run()
