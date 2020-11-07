import os
import sys
import time
import json

# Import enviromental variables
from dotenv import load_dotenv
load_dotenv(dotenv_path='api/variables.env')

host = os.getenv('SERVER_HOST')
port = os.getenv('SERVER_PORT')

# Init database
from database import Database
database = Database(os.getenv('DATABASE_NAME'))

# Create default access
try:
    num = database.count_document(os.getenv('CLIENTS_COLLECTION'))
except ValueError as error:
    print(error)
    sys.exit()

if num == 0:
    try:
        with open(os.getenv('DEFAULT_TOKEN')) as base:
            default_client = json.load(base)
    except:
        print('Missing BASE_TOKEN file')
        sys.exit()
    try:
        database.insert_one(os.getenv('CLIENTS_COLLECTION'), default_client)
        print('Default client created!')
    except ValueError as error:
        print(error)
        sys.exit()

# Create necessary folders
for dir in [os.getenv('DATASETS_PATH'), os.getenv('INPUT_PATH'), os.getenv('OUTPUT_PATH'), os.getenv('ZIP_PATH'), os.getenv('STORAGE_PATH')]:
    if not os.path.exists(dir):
        os.makedirs(dir)

# Start server
from server import server
app = server(database)

if __name__ == "__main__":
    app.run(debug=True, host=host, port=port, ssl_context=('api/resources/cert.pem', 'api/resources/key.pem'))
