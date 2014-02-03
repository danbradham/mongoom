from datetime import datetime
from .documents import Document
from .fields import RefField, Field


def fire(event, *args, **kwargs):
    event(*args, **kwargs).save()


class Event(Document):
    _collection = {"name": "Event", "capped": True, "max": 100, "size": 2**20}
    ref = RefField(Document)
    user = RefField(Document)
    created = Field(datetime, default=datetime.utcnow)
