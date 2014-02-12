from pymongo import MongoClient
from pymongo.errors import CollectionInvalid


CONNECTION = None
DATABASE = None


def connect(database, host="localhost", port=27017, **kwargs):
    '''Connect to a database at given host and port. Sets two global
    attributes, CONNECTION and DATABASE.

    Returns a MongoClient object

    :param database: Name of database to use.
    :param host: Host address
    :param port: Host port
    :param kwargs: Extra keyword arguments for :class:`pymongo.mongo_client.MongoClient`'''

    global CONNECTION
    global DATABASE
    c = MongoClient(host, port, **kwargs)
    CONNECTION = c
    DATABASE = c[database]
    return c


def get_database():
    '''Get database'''
    global DATABASE
    return DATABASE


def get_connection():
    '''Get global connection.'''
    global CONNECTION
    return CONNECTION


def get_collection(index_kwargs=None, coll_kwargs=None):
    '''Gets a collection from index_kwargs and coll_kwargs.
    If a collection does not exist create collection using coll_kwargs.
    If an index does not exist, ensure an index using index_kwargs.

    :param index_kwargs: Dictionary matching the signature of
        :func:`pymongo.database.ensure_index`.
    :param coll_kwargs: Dictionary matching the signature of
        :func:`pymongo.database.create_collection`
    '''
    global DATABASE
    try:
        DATABASE.create_collection(**coll_kwargs)
    except CollectionInvalid:
        pass
    collection = DATABASE[coll_kwargs["name"]]
    if index_kwargs:
        indices = collection.index_information()
        index_name = "_".join(
            [str(item) for key in index_kwargs["key_or_list"] for item in key])
        if not index_name in indices:
            collection.ensure_index(**index_kwargs)
    return collection


