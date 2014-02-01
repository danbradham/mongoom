from mongorm import *
from bson import DBRef
from datetime import datetime


class Version(Document):
    name = Field(str, required=True)
    user = RefField()
    path = Field(str)
    images = ListField(str)
    modified = Field(datetime, default=datetime.utcnow)
    parent = RefField()


class Component(Document):
    name = Field(str)
    user = RefField()
    created = Field(datetime, default=datetime.utcnow)
    versions = ListRefField()
    parent = RefField()


class Container(Document):

    name = Field(str, required=True)
    user = RefField()
    created = Field(datetime, default=datetime.utcnow)
    components = ListRefField()


def main():
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

    model_a.versions.append(master)
    model_a.save()
    master.save()
