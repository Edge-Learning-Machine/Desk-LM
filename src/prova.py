from pymongo import MongoClient
import os


client = MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017)
db = client.elm

_items = db.models.find()
items = [item for item in _items]

print(items)