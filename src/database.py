from pymongo import MongoClient
import os

class Database(object):
    
    def __init__(self, name):
        try:
            self.client = MongoClient(os.getenv('DATABASE_URL'))
            self.DATABASE = self.client[name]
            print('Database ready!')
        except Exception as error:
            print('Database not connected! ('+ str(error) +')')

    def insert_one(self, collection, data):
        try:
            self.DATABASE[collection].insert_one(data)
        except Exception as error:
            return (str(error), 404)
        return (None, None)

    def find(self, collection, query):
        try:
            value = self.DATABASE[collection].find({}, query)
        except Exception as error:
            return (str(error), 404, None)
        return (None, None, value)

    def find_one(self, collection, query):
        try:
            value = self.DATABASE[collection].find_one(query)
        except Exception as error:
            return (str(error), 404, None)
        return (None, None, value)

    def update_one(self, collection, filtering, query):
        try:
            self.DATABASE[collection].update_one(filtering, query)
        except Exception as error:
            return (str(error), 404)
        return (None, None)

    def delete_one(self, collection, data):
        try:
            self.DATABASE[collection].delete_one(data)
        except Exception as error:
            return (str(error), 404)
        return (None, None)
