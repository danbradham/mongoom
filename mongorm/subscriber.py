import sys
from time import sleep
from threading import Thread
from .connection import get_collection


class Subscriber(Thread):
    '''Watch a database collection by using a tailable cursor.
    Collection must be initialized with capped=True prior to invoking
    a subscriber thread.

    :param collection: Database collection to be subscribed to.
    :param *args: standard thread arguments.
    :param **kwargs: standard thread keyword arguments.
    '''

    def __init__(self, collection, *args, **kwargs):
        self.collection = get_collection(name=collection)
        super(Subscriber, self).__init__(*args, **kwargs)

    def run(self):
        '''Start watching a database collection.'''
        cursor = self.collection.find(tailable=True, await_data=True)
        while cursor.alive:
            try:
                doc = cursor.next()
                self.decode(doc)
            except StopIteration:
                sleep(0)

    def decode(self, doc):
        '''Decode event document on receiving a doc from tailable cursor.
        Requires all Document subclasses to be imported into the "__main__"
        module.'''

        doc_type = getattr(sys.modules["__main__"], doc["_type"])
        document = doc_type(**doc)
        self.handle(document)

    def handle(self, document):
        '''What do you want to do with the decoded document?'''
        pass
