import os
from pymongo import MongoClient
from commons.error import api_errors


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
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)

    def find(self, collection, query):
        try:
            values = self.DATABASE[collection].find({}, query)
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)
        return values

    def find_one(self, collection, query):
        try:
            value = self.DATABASE[collection].find_one(query)
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)
        if not value:
            error = api_errors['database']
            error['details'] = 'Document not found'
            raise ValueError(error)
        return value

    def update_one(self, collection, filtering, query):
        try:
            self.DATABASE[collection].update_one(filtering, query)
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)
 
    def delete_one(self, collection, data):
        try:
            self.DATABASE[collection].delete_one(data)
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)

    def count_document(self, collection):
        try:
            num = self.DATABASE[collection].count()
        except Exception as e:
            error = api_errors['database']
            error['details'] = str(e)
            raise ValueError(error)
        return num

    def exist(self, collection, filter):
        try:
            self.find_one(collection, filter)
        except:
            return False
        return True
        
