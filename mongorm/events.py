from datetime import datetime
from .documents import Document
from .fields import RefField, Field


def fire(event, *args, **kwargs):
    '''A convenience function for firing an event. "Firing an event" is
    exactly the same as saving an Event document to the database.

    :param *args: Event documents __init__ args
    :param **kwargs:: Event documents __init__ kwargs
    '''
    event(*args, **kwargs).save()


class Event(Document):
    _collection = {"name": "Event", "capped": True, "max": 100, "size": 2**20}
    ref = RefField(Document)
    user = RefField(Document)
    created = Field(datetime, default=datetime.utcnow)
