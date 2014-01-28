from mongorm import Document, Field, ListField
from datetime import datetime


class Project(Document):
    image = Field(str)
    name = Field(str, required=True)
    status = Field(int)
    user = Field(str)


class Sequence(Document):
    image = Field(str)
    name = Field(str, required=True)
    status = Field(int)
    user = Field(str)


class Version(Document):
    images = ListField(str)
    videos = ListField(str)
    filepath = Field(str)

t
