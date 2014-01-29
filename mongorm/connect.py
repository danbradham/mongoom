from gevent import monkey
monkey.patch_all()
from pymongo import MongoClient

CONNECTION = None


def connect(database, host, port):
    '''Connect to a database at given host and port.'''
    global CONNECTION
    c = MongoClient(host, port)
    CONNECTION = c[database]


def get_connection():
    '''Get global connection.'''
    global CONNECTION
    return CONNECTION
