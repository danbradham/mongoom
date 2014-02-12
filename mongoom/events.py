from datetime import datetime
from .documents import Document
from .fields import Field


def fire(event, **data):
    '''A convenience function for firing an event. "Firing an event" is
    exactly the same as saving an Event document to the database.

    :param **data: Event documents data. Same signature as the Event class.
    '''
    event(**data).save()


class Event(Document):
    '''Event documents live in a capped mongodb collection. Allowing
    people to Subscribe to events using a tailable cursor. Inherit from
    Event to create custom events.

    :param ref: Document that the event refers to.
    :param user: User that fired the event.
    :param created: Date that the event was fired.
    '''
    _collection = {"name": "Event", "capped": True, "max": 100, "size": 2**20}
    ref = Field(Document)
    user = Field(Document)
    created = Field(datetime, default=datetime.utcnow)
