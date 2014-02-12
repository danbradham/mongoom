from gevent import monkey
monkey.patch_all()
from collections import defaultdict
from datetime import datetime
import functools
from mongoom import connect, Subscriber, Event, fire, Document, Field
from pprint import pprint
from random import choice
from time import sleep
from threading import Thread


class Asset(Document):
    name = Field(basestring, required=True)
    created = Field(datetime, default=datetime.utcnow)


class Update(Event):
    '''Update Event'''


class Create(Event):
    '''Create Event'''


class Delete(Event):
    '''Delete Event'''


class EventHandler(Subscriber):

    _handlers = defaultdict(set)

    def handle(self, document):
        for handler in self._handlers[document.__class__]:
            handler(document)


def producer():
    for i in xrange(20):
        fire(choice(Event.__subclasses__()),
             ref=Asset(name=choice(["Bill", "Bob", "Henry"])).save())
        sleep(0)


def handles(*events):
    '''Adds handlers to EventHandler.'''
    def wrapped(fn):
        for event in events:
            EventHandler._handlers[event].add(fn)

        @functools.wraps(fn)
        def wraps(document):
            return fn
        return wraps
    return wrapped


@handles(Update, Create, Delete)
def event_printer(document):
    '''Print all events.'''
    print "event printer: ", document


@handles(Create)
def on_create(document):
    '''Do something on Create events'''
    print "on create: ", document
    pprint(document.ref.data, width=1)


if __name__ == "__main__":
    c = connect("test_db")
    c.drop_database("test_db")

    fire(Event)  # Fire a blank Event to initialize capped collection
    ev_producer = Thread(target=producer)
    ev_subscriber = EventHandler("Event")

    ev_producer.start()
    ev_subscriber.start()
