import os
from pymongo import MongoClient


class Database(object):
    
    def __init__(self, name):
        try:
            self.client = MongoClient(os.getenv('DATABASE_URL'))
            self.DATABASE = self.client[name]
            print('Database ready!')
        except Exception as error:
            print('Database not connected! ('+ str(error) +')')

    
    def insert_one(self, collection, data):
        """
        Returns:
            string: error
        """
        try:
            self.DATABASE[collection].insert_one(data)
        except Exception as error:
            return str(error)
        return None

    
    def find(self, collection, query):
        """
        Returns:
            string: error
            array: values
        """
        try:
            value = self.DATABASE[collection].find({}, query)
        except Exception as error:
            return str(error), None
        return None, value

    # Return (error, value)
    def find_one(self, collection, query):
        """
        Returns:
            string: error
            object: value
        """
        try:
            value = self.DATABASE[collection].find_one(query)
        except Exception as error:
            return str(error), None
        return None, value

    
    def update_one(self, collection, filtering, query):
        """
        Returns:
            string: error
        """
        try:
            self.DATABASE[collection].update_one(filtering, query)
        except Exception as error:
            return str(error)
        return None

    
    def delete_one(self, collection, data):
        """
        Returns:
            string: error
        """
        try:
            self.DATABASE[collection].delete_one(data)
        except Exception as error:
            return str(error)
        return None
