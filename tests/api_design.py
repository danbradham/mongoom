from pymongorm import connect, Document, Field, ListField, ListRefField, RefField
from datetime import datetime


class User(Document):
    name = Field(basestring)
    last_name = Field(basestring)
    created = Field(datetime, default=datetime.utcnow)


class Version(Document):
    name = Field(basestring, required=True)
    user = RefField(User)
    path = Field(basestring)
    images = ListField(basestring)
    modified = Field(datetime, default=datetime.utcnow)


class Component(Document):
    name = Field(basestring)
    user = RefField(User)
    created = Field(datetime, default=datetime.utcnow)
    versions = ListRefField(Version)


class Container(Document):

    name = Field(basestring, required=True)
    user = RefField(User)
    created = Field(datetime, default=datetime.utcnow)
    components = ListRefField(Component)


def main():
    connect("test_db", "localhost", 27017)

    me = User.find(name="Dan", last_name="Bradham")

    asset_a = Container(
        name="Asset A",
        user=me,
        ).save()

    model_a = Component(
        name="Model A",
        user=me,
        parent=asset_a,
        ).save()

    master = Version(
        name="master",
        user=me,
        path="path/to/file.ma",
        images=["path/to/imagefile.png"],
        parent=model_a,
        ).save()

    model_a.versions += master
    model_a.save()
    master.save()
