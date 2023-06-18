from pymongo import MongoClient

class Database:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)

    def get_collection(self, database_name, collection_name):
        db = self.client[database_name]
        return db[collection_name]