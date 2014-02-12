from datetime import datetime
from .documents import Document
from .fields import Field


class Event(Document):
    ''':class:`Event` documents live in a capped mongodb collection.  Allowing
    people to subscribe to events using a tailable cursor.  Inherit from
    :class:`Event` to create custom events.

    :param ref: :class:`Document` that the :class:`Event` refers to.
    :param user: User that fired the :class:`Event`.
    :param created: Date that the :class:`Event` was fired.
    '''
    _collection = {"name": "Event", "capped": True, "max": 100, "size": 2**20}
    ref = Field(Document)
    created = Field(datetime, default=datetime.utcnow)

    @classmethod
    def fire(cls, **data):
        '''A convenience method for firing an event. "Firing an event" is
        exactly the same as saving an instance of :class:`Event`.

        Usage::

            doc = Document(...).save()
            Event.fire(ref=doc)
        '''

        cls(**data).save()
