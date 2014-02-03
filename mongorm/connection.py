from pymongo import MongoClient
from pymongo.errors import CollectionInvalid


CONNECTION = None
DATABASE = None


def connect(database, host="localhost", port=27017):
    '''Connect to a database at given host and port.'''
    global CONNECTION
    global DATABASE
    c = MongoClient(host, port)
    CONNECTION = c
    DATABASE = c[database]
    return c


def get_database():
    '''Get database'''
    global DATABASE
    return DATABASE


def get_collection(**params):
    global DATABASE
    try:
        DATABASE.create_collection(**params)
    except CollectionInvalid:
        pass
    return DATABASE[params["name"]]


def get_connection():
    '''Get global connection.'''
    global CONNECTION
    return CONNECTION
